"""
Script to regenerate certificate with Co-op Bank of Tanzania PLC logo background
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

print("Co-operative Bank of Tanzania PLC - Certificate with Logo Background")
print("=" * 70)

try:
    # Check if logo exists
    logo_path = os.path.join('static', 'images', 'CoopLogo.png')
    if os.path.exists(logo_path):
        print(f"✓ Logo found at: {logo_path}")
    else:
        print(f"❌ Logo not found at: {logo_path}")
        print("Please ensure CoopLogo.png is copied to static/images/ folder")
        sys.exit(1)
    
    # Find existing certificates
    certificates = Certificate.objects.all()
    
    if not certificates.exists():
        print("No certificates found in the database.")
        sys.exit(0)
    
    for certificate in certificates:
        print(f"\nProcessing Certificate: {certificate.certificate_number}")
        print(f"User: {certificate.user.get_full_name()}")
        print(f"Course: {certificate.course.title if certificate.course else 'Risk Management Program'}")
        
        # Delete old PDF to regenerate with logo
        try:
            if certificate.pdf_file:
                certificate.pdf_file.delete(save=False)
                print("Deleted old PDF file")
        except:
            pass
        
        # Regenerate PDF with logo background
        print("Generating new PDF certificate with logo background...")
        from certificates.views import generate_certificate_pdf
        generate_certificate_pdf(certificate)
        
        certificate.save()
        
        print(f"✓ Certificate regenerated successfully with logo!")
        print(f"  PDF File: {certificate.pdf_file}")
        
    print(f"\n✓ Successfully processed {certificates.count()} certificate(s)")
    print("\nNew features added:")
    print("• Transparent Co-op Bank logo as certificate background")
    print("• Small logo at top left corner of certificate")
    print("• Professional branding with Co-operative Bank of Tanzania PLC")
    print("• Maintains all existing QR code and user information features")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()