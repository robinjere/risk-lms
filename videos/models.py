from django.db import models
from django.conf import settings
from courses.models import Course
import os
import json
from django.utils import timezone


class InteractiveCourse(models.Model):
    """Interactive SCORM/Captivate course package"""
    CONTENT_TYPES = [
        ('captivate', 'Adobe Captivate'),
        ('scorm', 'SCORM Package'),
        ('html5', 'HTML5 Course'),
        ('articulate', 'Articulate Storyline'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='interactive_courses')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='captivate')
    
    # Package storage
    package_file = models.FileField(upload_to='interactive_courses/packages/%Y/%m/', help_text='Original ZIP package')
    extracted_path = models.CharField(max_length=500, blank=True, help_text='Path to extracted content')
    entry_file = models.CharField(max_length=255, default='index.html', help_text='Main HTML file to launch')
    
    # Metadata from package
    duration_minutes = models.IntegerField(default=0, help_text='Estimated duration in minutes')
    total_slides = models.IntegerField(default=0)
    resolution_width = models.IntegerField(default=1280)
    resolution_height = models.IntegerField(default=720)
    
    # Thumbnail
    thumbnail = models.ImageField(upload_to='interactive_courses/thumbnails/', blank=True, null=True)
    
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_interactive_courses')
    
    class Meta:
        db_table = 'interactive_courses'
        ordering = ['order_index', 'created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_launch_url(self):
        """Get the URL to launch this interactive course"""
        if self.extracted_path:
            return f'/media/{self.extracted_path}/{self.entry_file}'
        return None
    
    def get_duration_display(self):
        """Return formatted duration"""
        if self.duration_minutes:
            hours = self.duration_minutes // 60
            minutes = self.duration_minutes % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes} minutes"
        return "Unknown"


class InteractiveCourseProgress(models.Model):
    """Track user's progress in interactive courses"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interactive_progress')
    interactive_course = models.ForeignKey(InteractiveCourse, on_delete=models.CASCADE, related_name='progress_records')
    
    # Progress tracking - slide by slide
    completion_percentage = models.IntegerField(default=0)
    current_slide = models.IntegerField(default=0, help_text='Current slide user is on (0 = not started)')
    highest_slide_reached = models.IntegerField(default=0, help_text='Highest slide number user has reached (no skipping)')
    total_time_spent = models.IntegerField(default=0, help_text='Total time in minutes')
    
    # Slide completion tracking (JSON: {"1": true, "2": true, "3": false, ...})
    slides_completed = models.JSONField(default=dict, blank=True, help_text='Track which slides are completed')

    # Per-slide timestamps for anti-skip enforcement
    slide_started_at = models.JSONField(default=dict, blank=True, help_text='ISO timestamps keyed by slide number for when user started a slide')
    slide_completed_at = models.JSONField(default=dict, blank=True, help_text='ISO timestamps keyed by slide number for when user completed a slide')
    skip_attempts = models.IntegerField(default=0, help_text='Count invalid slide jump attempts')

    # Quiz/assessment scores from the interactive course
    quiz_score = models.FloatField(null=True, blank=True)
    quiz_passed = models.BooleanField(null=True)
    quiz_attempts = models.IntegerField(default=0)
    
    # Content completion (must complete all slides before quiz)
    content_completed = models.BooleanField(default=False, help_text='All slides viewed')
    content_completed_at = models.DateTimeField(null=True, blank=True)
    
    is_completed = models.BooleanField(default=False, help_text='Course fully completed (content + quiz passed)')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SCORM data storage
    scorm_data = models.JSONField(default=dict, blank=True)
    scorm_suspend_data = models.TextField(default='', blank=True, help_text='SCORM suspend_data for course resume')
    
    class Meta:
        db_table = 'interactive_course_progress'
        unique_together = ['user', 'interactive_course']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.interactive_course.title}"
    
    def get_slides_completed_count(self):
        """Count how many slides are marked as completed"""
        return sum(1 for v in self.slides_completed.values() if v)
    
    def calculate_completion_percentage(self):
        """Calculate completion percentage based on slides completed"""
        total_slides = self.interactive_course.total_slides
        if total_slides > 0:
            completed = self.get_slides_completed_count()
            return int((completed / total_slides) * 100)
        return 0
    
    def can_access_slide(self, slide_number):
        """Check if user can access a specific slide (no skipping)"""
        try:
            slide_number = int(slide_number)
        except (TypeError, ValueError):
            return False

        if slide_number < 1:
            return False

        total_slides = int(self.interactive_course.total_slides or 0)
        if total_slides > 0 and slide_number > total_slides:
            return False

        return slide_number <= int(self.highest_slide_reached or 0) + 1

    def get_min_time_per_slide_seconds(self):
        total_slides = int(self.interactive_course.total_slides or 0)
        if total_slides <= 0:
            return 20
        duration_minutes = int(self.interactive_course.duration_minutes or 0)
        return max(20, (duration_minutes * 60) // total_slides) if duration_minutes > 0 else 20

    def start_slide(self, slide_number):
        """Persist a slide start timestamp (idempotent)."""
        slide_number = int(slide_number)
        key = str(slide_number)
        if not self.slide_started_at.get(key):
            self.slide_started_at[key] = timezone.now().isoformat()

    def mark_slide_completed(self, slide_number):
        """Mark a slide as completed and update progress"""
        slide_number = int(slide_number)
        key = str(slide_number)

        self.slides_completed[key] = True
        self.start_slide(slide_number)
        if not self.slide_completed_at.get(key):
            self.slide_completed_at[key] = timezone.now().isoformat()

        if slide_number > self.highest_slide_reached:
            self.highest_slide_reached = slide_number
        self.current_slide = slide_number
        self.completion_percentage = self.calculate_completion_percentage()
        
        # Check if all content is completed
        total_slides = self.interactive_course.total_slides
        if self.get_slides_completed_count() >= total_slides:
            self.content_completed = True
            if not self.content_completed_at:
                from django.utils import timezone
                self.content_completed_at = timezone.now()


class Video(models.Model):
    """Video model for course content"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/%Y/%m/')
    duration = models.IntegerField(help_text='Duration in seconds', default=0)
    file_size = models.BigIntegerField(default=0)
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'videos'
        ordering = ['order_index', 'created_at']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class VideoSubtitle(models.Model):
    """Subtitles/translations for videos"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='subtitles')
    language_code = models.CharField(max_length=10)
    language_name = models.CharField(max_length=50)
    subtitle_file = models.FileField(upload_to='subtitles/%Y/%m/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_subtitles'
        unique_together = ['video', 'language_code']
    
    def __str__(self):
        return f"{self.video.title} - {self.language_name}"

class VideoProgress(models.Model):
    """Track user's video watching progress (prevent skipping)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_progress')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='progress_records')
    watched_duration = models.IntegerField(default=0, help_text='Seconds watched')
    last_position = models.IntegerField(default=0, help_text='Last position in seconds')
    is_completed = models.BooleanField(default=False)
    skip_attempts = models.IntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_progress'
        unique_together = ['user', 'video']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.video.title}"
    
    def completion_percentage(self):
        if self.video.duration > 0:
            return (self.watched_duration / self.video.duration) * 100
        # For videos with unknown duration, use time-based completion
        # Consider 60 seconds as a reasonable minimum for completion
        elif self.watched_duration >= 60:
            return 100
        elif self.watched_duration > 0:
            return min((self.watched_duration / 60) * 100, 99)  # Cap at 99% until manually marked complete
        return 0
