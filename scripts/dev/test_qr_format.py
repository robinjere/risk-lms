import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

def decode_qr_data(qr_data):
    """Decode the QR code data format"""
    parts = qr_data.split('|')
    if len(parts) >= 8 and parts[0] == 'COOP-CERT':
        return {
            'prefix': parts[0],
            'certificate_number': parts[1],
            'participant_name': parts[2],
            'email': parts[3],
            'course': parts[4],
            'score': parts[5],
            'date': parts[6],
            'verification_url': parts[7],
            'status': parts[8] if len(parts) > 8 else 'VALID'
        }
    return None

# Test with existing certificate
from certificates.models import Certificate

try:
    certificate = Certificate.objects.get(certificate_number__startswith='COOP-RISK')
    
    print(f'Testing certificate: {certificate.certificate_number}')
    print(f'User: {certificate.user.get_full_name()}')
    print(f'Course: {certificate.course.title if certificate.course else "Risk Management Program"}')
    print(f'Score: {certificate.overall_score:.1f}%')
    
    # Show the QR code data format
    qr_text = f"COOP-CERT|{certificate.certificate_number}|{certificate.user.get_full_name()}|{certificate.user.email}|{certificate.course.title if certificate.course else 'Risk Management Program'}|{certificate.overall_score:.1f}%|{certificate.issue_date.strftime('%Y-%m-%d')}|{certificate.verification_url}|VALID"
    
    print('\n=== QR Code Data ===')
    print(f'Raw: {qr_text}')
    print(f'Length: {len(qr_text)} characters')
    
    # Decode and display
    decoded = decode_qr_data(qr_text)
    if decoded:
        print('\n=== Decoded Information ===')
        for key, value in decoded.items():
            print(f'{key.replace("_", " ").title()}: {value}')
    else:
        print('Failed to decode QR data')
        
except Certificate.DoesNotExist:
    print('No certificate found')
except Exception as e:
    print(f'Error: {e}')