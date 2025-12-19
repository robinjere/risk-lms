import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from certificates.models import Certificate

# Find the existing certificate and regenerate it with updated QR code
try:
    certificate = Certificate.objects.get(certificate_number__startswith='COOP-RISK')
    print(f'Found certificate: {certificate.certificate_number}')
    
    # Delete old files
    if certificate.qr_code:
        certificate.qr_code.delete()
    if certificate.pdf_file:
        certificate.pdf_file.delete()
    
    # Regenerate with improved QR code
    certificate.generate_qr_code()
    
    from certificates.views import generate_certificate_pdf
    generate_certificate_pdf(certificate)
    
    certificate.save()
    
    print(f'Certificate regenerated successfully!')
    print(f'QR Code: {certificate.qr_code}')
    print(f'PDF: {certificate.pdf_file}')
    
except Certificate.DoesNotExist:
    print('No certificate found to regenerate')
except Exception as e:
    print(f'Error: {e}')