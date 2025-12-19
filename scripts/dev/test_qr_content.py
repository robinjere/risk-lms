import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from certificates.models import Certificate
import qrcode
from PIL import Image
import json

# Find the certificate
try:
    certificate = Certificate.objects.get(certificate_number__startswith='COOP-RISK')
    print(f'Testing certificate: {certificate.certificate_number}')
    print(f'User: {certificate.user.get_full_name()}')
    print(f'Email: {certificate.user.email}')
    print(f'Score: {certificate.overall_score}%')
    
    # Read the QR code to verify its content
    if certificate.qr_code:
        # Try to decode the QR code
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image
            
            # Open and decode QR code
            qr_image = Image.open(certificate.qr_code.path)
            decoded_objects = decode(qr_image)
            
            if decoded_objects:
                qr_data = decoded_objects[0].data.decode('utf-8')
                print('\n=== QR Code Content ===')
                print(qr_data)
            else:
                print('Could not decode QR code')
                
        except ImportError:
            print('pyzbar not installed, showing expected QR content instead:')
            
            # Show what should be in the QR code
            qr_text = f"""CERTIFICATE VERIFICATION
Cert No: {certificate.certificate_number}
Name: {certificate.user.get_full_name()}
Email: {certificate.user.email}
Course: {certificate.course.title if certificate.course else 'Risk Management Program'}
Score: {certificate.overall_score:.1f}%
Date: {certificate.issue_date.strftime('%B %d, %Y')}
Issuer: Co-operative Bank of Kenya Ltd
Verify: {certificate.verification_url}
Status: {'VALID' if certificate.is_valid else 'INVALID'}"""
            
            print('\n=== Expected QR Code Content ===')
            print(qr_text)
    else:
        print('No QR code found')
        
except Certificate.DoesNotExist:
    print('No certificate found')
except Exception as e:
    print(f'Error: {e}')