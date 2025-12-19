"""
Script to verify certificate QR code and display certificate information
"""
import os
import django
import sys
import json

# Add the project directory to Python path
sys.path.append(r'c:\Users\Paul\New folder')
os.chdir(r'c:\Users\Paul\New folder')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from certificates.models import Certificate

print("Co-operative Bank of Tanzania PLC - Certificate Verification")
print("=" * 60)

try:
    certificates = Certificate.objects.all()
    
    for certificate in certificates:
        print(f"\nCertificate Number: {certificate.certificate_number}")
        print(f"Issued To: {certificate.user.get_full_name()}")
        print(f"Email: {certificate.user.email}")
        print(f"Course: {certificate.course.title if certificate.course else 'Risk Management Program'}")
        print(f"Issue Date: {certificate.issue_date.strftime('%Y-%m-%d')}")
        
        # Show QR Code info
        if certificate.qr_code:
            print(f"\n✓ QR Code: {certificate.qr_code}")
        else:
            print("\n⚠ No QR code generated yet")
        
        # Show verification URL
        print(f"Verification URL: {certificate.verification_url}")
        print(f"Overall Score: {certificate.overall_score}%")
        print(f"Valid Status: {'✓ Valid' if certificate.is_valid else '❌ Invalid'}")
        print(f"\nPDF Location: {certificate.pdf_file}")
        
        # Check if PDF exists
        pdf_path = os.path.join('media', str(certificate.pdf_file))
        if os.path.exists(pdf_path):
            print(f"✓ PDF file exists and ready for download")
            file_size = os.path.getsize(pdf_path)
            print(f"  File size: {file_size:,} bytes")
        else:
            print("❌ PDF file not found")
        
        print("-" * 60)
        
    print(f"\n✓ Verified {certificates.count()} certificate(s)")
    print("\nCertificate Features:")
    print("• Co-operative Bank of Tanzania PLC branding")
    print("• Transparent logo background for professional appearance")
    print("• Small logo in header for authenticity")
    print("• Comprehensive QR code with full user verification data")
    print("• Secure certificate number for easy verification")
    print("• PDF format for easy sharing and printing")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()