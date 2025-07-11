import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eoweb.settings')
django.setup()

User = get_user_model()

# Cambia estos valores a los que desees
username = "RickyV"
email = "rickyvdev18@gmail.com"
password = "Khasen18"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superusuario creado correctamente.")
else:
    print("El superusuario ya existe.")
