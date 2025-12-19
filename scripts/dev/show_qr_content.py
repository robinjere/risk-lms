"""
Script to show what information appears when QR code is scanned
This demonstrates the self-contained certificate data
"""
import os
import django
import sys

# Add the project directory to Python path
sys.path.append(r'c:\Users\Paul\New folder')
os.chdir(r'c:\Users\Paul\New folder')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from certificates.models import Certificate

print("Co-operative Bank of Tanzania PLC - QR Code Content Preview")
print("=" * 70)

try:
    certificates = Certificate.objects.all()
    
    for certificate in certificates:
        print(f"\nCertificate: {certificate.certificate_number}")
        print("=" * 50)
        
        # Regenerate QR code content to show what scanner will see
        from django.utils import timezone
        
        qr_text = f"""🏆 CERTIFICATE OF COMPLETION 🏆

📜 Certificate #: {certificate.certificate_number}
👤 Full Name: {certificate.user.get_full_name()}
📧 Email: {certificate.user.email}
🆔 Username: {certificate.user.username}
📚 Course: {certificate.course.title if certificate.course else 'Risk Management Program'}
📊 Final Score: {certificate.overall_score:.1f}%
📅 Completed: {certificate.issue_date.strftime('%B %d, %Y')}
🏦 Issuing Bank: Co-operative Bank of Tanzania PLC
🏢 Department: Risk Management & Compliance
🌐 Website: www.coopbank.co.tz
✅ Status: VALID & AUTHENTIC

This certificate confirms successful completion of the Risk Management training program with a score of {certificate.overall_score:.1f}%. 

Verification: {certificate.verification_url}
Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} EAT"""
        
        print("\n📱 WHEN QR CODE IS SCANNED, THIS TEXT APPEARS IMMEDIATELY:")
        print("=" * 70)
        print(qr_text)
        print("=" * 70)
        
        print("\n✅ KEY BENEFITS:")
        print("• ✓ Complete certificate information displays instantly")
        print("• ✓ No internet connection required for basic verification")
        print("• ✓ All personal details included (name, email, username)")
        print("• ✓ Course completion details and score shown")
        print("• ✓ Official bank branding and contact information")
        print("• ✓ Verification URL available for online cross-check")
        print("• ✓ Timestamp and authenticity confirmation")
        print("• ✓ Emojis make information easy to read and identify")
        
        print(f"\n📏 QR CODE SPECIFICATIONS:")
        print(f"• Size in PDF: 2.0 inches (optimal for smartphone scanning)")
        print(f"• Version: 4 (supports larger data content)")
        print(f"• Error Correction: Medium (balances size and reliability)")
        print(f"• Content Length: ~{len(qr_text)} characters")
        print(f"• Positioning: Bottom center with white background border")
        
    print(f"\n🎯 SCANNING EXPERIENCE:")
    print("1. Point smartphone camera or QR scanner at certificate")
    print("2. QR code is detected automatically (large 2-inch size)")
    print("3. All certificate information appears immediately on screen")
    print("4. No need to visit websites or enter certificate numbers")
    print("5. Perfect for offline verification and instant authentication")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()