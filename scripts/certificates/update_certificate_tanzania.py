import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from certificates.models import Certificate

# Find and update the existing certificate
try:
    certificate = Certificate.objects.get(certificate_number__startswith='COOP-RISK')
    print(f'Found certificate: {certificate.certificate_number}')
    
    # Update certificate number to Tanzania format
    old_number = certificate.certificate_number
    certificate.certificate_number = certificate.certificate_number.replace('COOP-RISK', 'COOP-TZ')
    
    # Update verification URL
    certificate.verification_url = certificate.verification_url.replace(old_number, certificate.certificate_number)
    
    # Delete old files
    if certificate.qr_code:
        certificate.qr_code.delete()
    if certificate.pdf_file:
        certificate.pdf_file.delete()
    
    # Regenerate with Tanzania information
    certificate.generate_qr_code()
    
    from certificates.views import generate_certificate_pdf
    generate_certificate_pdf(certificate)
    
    certificate.save()
    
    print(f'Certificate updated successfully!')
    print(f'New certificate number: {certificate.certificate_number}')
    print(f'New verification URL: {certificate.verification_url}')
    print(f'QR Code: {certificate.qr_code}')
    print(f'PDF: {certificate.pdf_file}')
    
    # Test the QR code content
    qr_expected = f"COOP-TZ|{certificate.certificate_number}|{certificate.user.get_full_name()}|{certificate.user.email}|{certificate.course.title if certificate.course else 'Risk Management Program'}|{certificate.overall_score:.1f}%|{certificate.issue_date.strftime('%Y-%m-%d')}|Co-operative Bank of Tanzania|{certificate.verification_url}|VALID"
    print(f'\nExpected QR Content:\n{qr_expected}')
    
except Certificate.DoesNotExist:
    print('No certificate found to update')
except Exception as e:
    print(f'Error: {e}')