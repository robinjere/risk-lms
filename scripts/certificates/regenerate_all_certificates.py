"""
Script to regenerate QR codes and PDFs for all existing certificates
Run with: python manage.py shell < regenerate_all_certificates.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from certificates.models import Certificate
from certificates.views import generate_certificate_pdf

def regenerate_certificates():
    """Regenerate QR codes and PDFs for all certificates"""
    certificates = Certificate.objects.all()
    
    print(f"Found {certificates.count()} certificate(s) to regenerate")
    
    for cert in certificates:
        print(f"\n--- Processing Certificate #{cert.id} ---")
        print(f"Certificate Number: {cert.certificate_number}")
        print(f"User: {cert.user.get_full_name()} ({cert.user.email})")
        print(f"Course: {cert.get_course_title()}")
        print(f"Score: {cert.overall_score}%")
        
        try:
            # Regenerate QR code with full user information
            print("Regenerating QR code...")
            cert.generate_qr_code()
            cert.save()
            print(f"QR code saved: {cert.qr_code.name}")
            
            # Regenerate PDF
            print("Regenerating PDF certificate...")
            generate_certificate_pdf(cert)
            cert.save()
            print(f"PDF saved: {cert.pdf_file.name}")
            
            print(f"✓ Certificate #{cert.id} regenerated successfully!")
            
        except Exception as e:
            print(f"✗ Error regenerating certificate #{cert.id}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n=== Regeneration Complete ===")

if __name__ == "__main__":
    regenerate_certificates()
else:
    # When run via shell
    regenerate_certificates()
