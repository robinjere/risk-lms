"""
Script to create new banker users for the Risk LMS system
"""
import os
import django
import sys

# Add the project directory to Python path
sys.path.append(r'c:\Users\Paul\New folder')
os.chdir(r'c:\Users\Paul\New folder')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')
django.setup()

from accounts.models import User
from django.db import transaction

# New banker users to create
new_bankers = [
    {
        'email': 'Jasmin.Lugome@cbtbank.co.tz',
        'first_name': 'Jasmin',
        'last_name': 'Lugome',
        'username': 'JLugome'
    },
    {
        'email': 'Zena.Mashaka@cbtbank.co.tz',
        'first_name': 'Zena', 
        'last_name': 'Mashaka',
        'username': 'ZMashaka'
    },
    {
        'email': 'Shufaa.Zimbamagoma@cbtbank.co.tz',
        'first_name': 'Shufaa',
        'last_name': 'Zimbamagoma', 
        'username': 'SZimbamagoma'
    },
    {
        'email': 'Angel.Laswai@cbtbank.co.tz',
        'first_name': 'Angel',
        'last_name': 'Laswai',
        'username': 'ALaswai'
    },
    {
        'email': 'Abdallah.Likongwe@cbtbank.co.tz',
        'first_name': 'Abdallah',
        'last_name': 'Likongwe',
        'username': 'ALikongwe'
    },
    {
        'email': 'Clemence.Bayona@cbtbank.co.tz',
        'first_name': 'Clemence',
        'last_name': 'Bayona',
        'username': 'CBayona'
    }
]

print("Co-operative Bank of Tanzania PLC - Creating New Banker Users")
print("=" * 65)

created_users = []
existing_users = []
errors = []

with transaction.atomic():
    for banker_info in new_bankers:
        try:
            # Check if user already exists
            if User.objects.filter(email=banker_info['email']).exists():
                existing_users.append(banker_info['email'])
                print(f"⚠ User already exists: {banker_info['email']}")
                continue
                
            if User.objects.filter(username=banker_info['username']).exists():
                # Try alternative username
                original_username = banker_info['username']
                banker_info['username'] = banker_info['username'] + "2"
                print(f"⚠ Username {original_username} exists, using {banker_info['username']}")
            
            # Create new banker user
            user = User.objects.create_user(
                username=banker_info['username'],
                email=banker_info['email'],
                first_name=banker_info['first_name'],
                last_name=banker_info['last_name'],
                password='CBTBank2024!',  # Default password
                role='banker',
                is_active=True,
                is_staff=False
            )
            
            created_users.append({
                'user': user,
                'info': banker_info
            })
            
            print(f"✅ Created: {user.get_full_name()} ({user.email})")
            print(f"   Username: {user.username}")
            print(f"   Role: {user.role}")
            print(f"   Password: CBTBank2024!")
            print()
            
        except Exception as e:
            errors.append({
                'email': banker_info['email'],
                'error': str(e)
            })
            print(f"❌ Error creating {banker_info['email']}: {e}")

print("\n" + "=" * 65)
print("SUMMARY:")
print("-" * 30)

print(f"\n✅ Successfully Created: {len(created_users)} users")
for user_data in created_users:
    user = user_data['user']
    print(f"   • {user.get_full_name()} - {user.email}")

if existing_users:
    print(f"\n⚠ Already Existed: {len(existing_users)} users")
    for email in existing_users:
        print(f"   • {email}")

if errors:
    print(f"\n❌ Errors: {len(errors)} users")
    for error_data in errors:
        print(f"   • {error_data['email']}: {error_data['error']}")

print(f"\n📊 USER STATISTICS:")
total_users = User.objects.count()
bankers = User.objects.filter(role='banker').count()
risk_admins = User.objects.filter(role='head_of_risk').count()
compliance = User.objects.filter(role='risk_compliance_specialist').count()
admins = User.objects.filter(role='admin').count()

print(f"   • Total Users: {total_users}")
print(f"   • Bankers: {bankers}")
print(f"   • Risk Admins: {risk_admins}")
print(f"   • Compliance Specialists: {compliance}")
print(f"   • System Admins: {admins}")

print(f"\n🔐 LOGIN INFORMATION:")
print("Default password for all new users: CBTBank2024!")
print("Users can login at: http://127.0.0.1:8000/accounts/login/")
print("Users should change their password after first login")

print(f"\n🎓 NEXT STEPS:")
print("1. Notify users of their login credentials")
print("2. Users can now access the Risk Management training courses")
print("3. Users can take quizzes and earn certificates") 
print("4. Monitor user progress in the admin panel")

print(f"\n✅ New banker users ready for Risk Management training!")