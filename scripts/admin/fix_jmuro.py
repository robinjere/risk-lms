import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risk_lms.settings')

import django
django.setup()

from accounts.models import User

u = User.objects.get(username='JMuro')
print(f'Username: {u.username}')
print(f'Email: {u.email}')
print(f'Has usable password before: {u.has_usable_password()}')

# Set password
u.set_password('Test123!')
u.save()

print(f'Password set to: Test123!')
print(f'Has usable password after: {u.has_usable_password()}')
