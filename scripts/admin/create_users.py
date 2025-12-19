"""
Script to create Head of Risk and Risk & Compliance Specialist users
"""
from accounts.models import User

# Create Head of Risk - Jackline Muro
print("Creating Head of Risk user...")
head_of_risk = User.objects.create_user(
    email='Jackline.Muro@cbtbank.co.tz',
    username='JMuro',
    password='CBT@2025Risk',  # Change this password after first login
    first_name='Jackline',
    last_name='Muro',
    role='head_of_risk'
)
print(f"✅ Created: {head_of_risk.get_full_name()} ({head_of_risk.email})")
print(f"   Role: {head_of_risk.get_role_display()}")
print(f"   Can access admin: {head_of_risk.is_staff}")
print(f"   Username: {head_of_risk.username}")
print(f"   Password: CBT@2025Risk")
print()

# Create Risk & Compliance Specialist - Julleth Mselle
print("Creating Risk & Compliance Specialist user...")
specialist = User.objects.create_user(
    email='Julleth.Mselle@cbtbank.co.tz',
    username='JMselle',
    password='CBT@2025Compliance',  # Change this password after first login
    first_name='Julleth',
    last_name='Mselle',
    role='risk_compliance_specialist'
)
print(f"✅ Created: {specialist.get_full_name()} ({specialist.email})")
print(f"   Role: {specialist.get_role_display()}")
print(f"   Can access admin: {specialist.is_staff}")
print(f"   Username: {specialist.username}")
print(f"   Password: CBT@2025Compliance")
print()

print("=" * 60)
print("SUMMARY")
print("=" * 60)
print()
print("Both users have been created successfully!")
print()
print("🔐 LOGIN CREDENTIALS:")
print()
print("1️⃣  Head of Risk:")
print("   Email: Jackline.Muro@cbtbank.co.tz")
print("   Username: JMuro")
print("   Password: CBT@2025Risk")
print("   Admin URL: http://127.0.0.1:8000/admin/")
print()
print("2️⃣  Risk & Compliance Specialist:")
print("   Email: Julleth.Mselle@cbtbank.co.tz")
print("   Username: JMselle")
print("   Password: CBT@2025Compliance")
print("   Admin URL: http://127.0.0.1:8000/admin/")
print()
print("✅ Both users can now:")
print("   - Access the admin panel")
print("   - Upload courses and videos")
print("   - Add subtitles/translations")
print("   - Create question banks")
print()
print("⚠️  IMPORTANT: Ask users to change their passwords after first login!")
