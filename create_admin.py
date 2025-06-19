# create_admin.py

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eoweb.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'RickyV'
email = 'rickyvdev18@gmail.com'
password = 'Khasen18'

# Eliminar usuario anterior si ya existe
User.objects.filter(username=username).delete()

# Crear nuevo superusuario
User.objects.create_superuser(username=username, email=email, password=password)
print('Superusuario creado (forzado).')
