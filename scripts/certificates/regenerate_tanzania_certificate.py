"""
Script to regenerate certificate with Co-operative Bank of Tanzania PLC branding
and improved QR code positioning with comprehensive user information
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

print("Co-operative Bank of Tanzania PLC - Certificate Regeneration")
print("=" * 60)

try:
    # Find existing certificates
    certificates = Certificate.objects.all()
    
    if not certificates.exists():
        print("No certificates found in the database.")
        sys.exit(0)
    
    for certificate in certificates:
        print(f"\nProcessing Certificate: {certificate.certificate_number}")
        print(f"User: {certificate.user.get_full_name()}")
        print(f"Email: {certificate.user.email}")
        print(f"Course: {certificate.course.title if certificate.course else 'Risk Management Program'}")
        print(f"Score: {certificate.overall_score:.1f}%")
        
        # Update certificate number format if needed
        if certificate.certificate_number.startswith('COOP-RISK'):
            old_number = certificate.certificate_number
            certificate.certificate_number = certificate.certificate_number.replace('COOP-RISK', 'COOP-TZ')
            certificate.verification_url = certificate.verification_url.replace(old_number, certificate.certificate_number)
            print(f"Updated certificate number: {certificate.certificate_number}")
        
        # Delete old files to regenerate
        try:
            if certificate.qr_code:
                certificate.qr_code.delete(save=False)
                print("Deleted old QR code")
        except:
            pass
            
        try:
            if certificate.pdf_file:
                certificate.pdf_file.delete(save=False)
                print("Deleted old PDF file")
        except:
            pass
        
        # Regenerate QR code with comprehensive user information
        print("Generating new QR code with user details...")
        certificate.generate_qr_code()
        
        # Regenerate PDF with Tanzania PLC branding and centered QR code
        print("Generating new PDF certificate...")
        from certificates.views import generate_certificate_pdf
        generate_certificate_pdf(certificate)
        
        certificate.save()
        
        print(f"✓ Certificate regenerated successfully!")
        print(f"  QR Code: {certificate.qr_code}")
        print(f"  PDF File: {certificate.pdf_file}")
        
        # Show expected QR content
        expected_qr = f"""CERTIFICATE VERIFICATION
Certificate Number: {certificate.certificate_number}
Name: {certificate.user.get_full_name()}
Email: {certificate.user.email}
Username: {certificate.user.username}
Course: {certificate.course.title if certificate.course else 'Risk Management Program'}
Score: {certificate.overall_score:.1f}%
Issue Date: {certificate.issue_date.strftime('%B %d, %Y')}
Issuer: Co-operative Bank of Tanzania PLC
Department: Risk Management
Verify Online: {certificate.verification_url}
Status: VALID"""
        
        print(f"\nQR Code contains:")
        print("-" * 40)
        print(expected_qr)
        print("-" * 40)
        
    print(f"\n✓ Successfully processed {certificates.count()} certificate(s)")
    print("\nImprovements made:")
    print("• Updated to Co-operative Bank of Tanzania PLC")
    print("• QR code now centered at bottom of certificate")
    print("• QR code contains comprehensive user information")
    print("• Improved layout with better spacing")
    print("• Enhanced readability when scanned")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()