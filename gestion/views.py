from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from .models import Cliente, Empleado, EmpleadoDocumento, Puesto
from .forms import ClienteForm
from django.db.models import Q
from django.http import HttpResponseForbidden  # para validación de permisos
import os

# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, "¡Las credenciales son incorrectas! Intenta nuevamente...")

    return render(request, 'gestion/login.html')

@login_required
def inicio(request):
    es_admin = request.user.groups.filter(name='Administrador').exists()
    es_superusuario = request.user.is_superuser

    return render(request, 'gestion/inicio.html', {
        'es_admin': es_admin,
        'es_superusuario': es_superusuario
    })

def crear_grupos():
    # Grupo Administrador
    admin_group, created = Group.objects.get_or_create(name='Administrador')
    
    # Grupo Empleado
    empleado_group, created = Group.objects.get_or_create(name='Empleado')

    print("Grupos creados correctamente.")

#CRUD Y LISTA CLIENTES

@login_required
def lista_clientes(request):
    query = request.GET.get('busqueda', '')
    if query:
        clientes = Cliente.objects.filter(
            Q(nombre__icontains=query) |
            Q(id__iexact=query)
        )
    else:
        clientes = Cliente.objects.all()
    return render(request, 'gestion/lista_clientes.html', {'clientes': clientes})

@login_required
def agregar_cliente(request):
    if request.method == "POST": 
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente agregado correctamente.")
            return redirect('lista_clientes')
    else:
        form = ClienteForm()
    
    return render(request, 'gestion/agregar_cliente.html', {'form': form})

@login_required
def modificar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == 'POST':
        cliente.clave = request.POST.get('clave')
        cliente.nombre = request.POST.get('nombre')
        cliente.direccion = request.POST.get('direccion') 
        cliente.colonia = request.POST.get('colonia')
        cliente.ciudad = request.POST.get('ciudad')
        cliente.telefono = request.POST.get('telefono')
        cliente.atencion_a = request.POST.get('atencion_a')
        cliente.obra = request.POST.get('obra')
        cliente.localizacion = request.POST.get('localizacion')
        cliente.correo = request.POST.get('correo')
        cliente.save()
        return redirect('lista_clientes')

    return render(request, 'gestion/modificar_cliente.html', {'cliente': cliente})


@login_required
def ver_cliente(request, cliente_id):
    
    cliente = get_object_or_404(Cliente, id=cliente_id)
    return render(request, 'gestion/ver_cliente.html', {'cliente': cliente})

@login_required
def eliminar_cfdi_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if cliente.cfdi:
        cliente.cfdi.delete()
        cliente.cfdi = None
        cliente.save()
        messages.success(request, "CFDI eliminado correctamente.")
    return redirect('ver_cliente', cliente_id=cliente_id)

@login_required
def eliminar_cliente(request, cliente_id):
    if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
        return redirect('lista_clientes')

    cliente = get_object_or_404(Cliente, pk=cliente_id)

    if request.method == "POST":
        cliente.delete()
        return redirect('lista_clientes')

    return render(request, 'gestion/eliminar_cliente.html', {'cliente': cliente})


#CRUD Y LISTA EMPLEADOS
@login_required
def lista_empleados(request):
    if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
        return redirect('lista_empleados')

    empleados = Empleado.objects.all()
    query = request.GET.get('busqueda', '')
    rol = request.GET.get('rol', '')
    fecha_nacimiento = request.POST.get("fecha_nacimiento")
    

    if query:
        empleados = empleados.filter(
            Q(nombre__icontains=query) | Q(puesto__nombre__icontains=query) | Q(id_personal__icontains=query)
        )

    if rol:
        empleados = empleados.filter(usuario__groups__name=rol)
    
   

    sin_usuario = empleados.filter(usuario__isnull=True).count()
    if sin_usuario > 0: 
        messages.warning(request, f"{sin_usuario} empleado(s) no tienen usuario asociado.")

    return render(request, 'gestion/lista_empleados.html', {
        'empleados': empleados
    })


@login_required
def agregar_empleado(request):
    if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
        return redirect('lista_empleados')
    
    if request.method == "POST":
        id_personal = request.POST.get("id_personal", "").upper()
        nombre = request.POST.get("nombre", "").upper()
        email = request.POST.get("email", "").upper()
        telefono = request.POST.get("telefono", "").upper()
        puesto_valor = request.POST.get("puesto", "").upper()

        # Si es un número, intenta buscar por ID. Si no, busca por nombre o crea uno nuevo.
        if puesto_valor and puesto_valor.isdigit():
            puesto = Puesto.objects.filter(id=puesto_valor).first()
        elif puesto_valor:
            puesto, _ = Puesto.objects.get_or_create(nombre=puesto_valor)
        else:
            puesto = None
        username = request.POST.get("username")
        password = request.POST.get("password")
        rol = request.POST.get("rol")  # 'Administrador' o 'Empleado'

        # NUEVOS CAMPOS
        domicilio = request.POST.get("domicilio", "").upper()
        codigo_postal = request.POST.get("codigo_postal", "").upper()
        rfc = request.POST.get("rfc", "").upper()
        fecha_nacimiento = request.POST.get("fecha_nacimiento", "").upper()
        tipo_sangre = request.POST.get("tipo_sangre", "").upper()

        if not email:
            messages.error(request, "El correo electrónico es obligatorio.")
            return redirect('agregar_empleado')
        
        if not fecha_nacimiento:
            messages.error(request, "La fecha de nacimiento es obligatoria.")
            return redirect('agregar_empleado')
        
        if not telefono.isdigit():
            messages.error(request, "El teléfono solo debe contener números.")
            return redirect('agregar_empleado')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ese nombre de usuario ya está en uso.")
            return redirect('agregar_empleado')

        # Validación de rol
        if rol == "Administrador" and not request.user.is_superuser:
            messages.error(request, "Solo el superusuario puede asignar el rol de Administrador.")
            return redirect('agregar_empleado')

        user = User.objects.create_user(username=username, email=email, password=password)

        # Agregar al grupo según el rol
        try:
            grupo = Group.objects.get(name=rol)
            user.groups.add(grupo)
        except Group.DoesNotExist:
            messages.error(request, f"El grupo '{rol}' no existe.")
            user.delete()
            return redirect('agregar_empleado')

        # Crear el objeto Empleado
        Empleado.objects.create(
            id_personal=id_personal,
            nombre=nombre,
            email=email,
            telefono=telefono,
            puesto=puesto,
            usuario=user,
            domicilio=domicilio,
            codigo_postal=codigo_postal,
            rfc=rfc,
            fecha_nacimiento=fecha_nacimiento,
            tipo_sangre=tipo_sangre
        )

        messages.success(request, "Empleado agregado correctamente.")
        return redirect('lista_empleados')

    puestos = Puesto.objects.all()
    return render(request, 'gestion/agregar_empleado.html', {'puestos': puestos})


@login_required
def modificar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)

    # Solo superusuario o Administrador pueden editar
    if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
        return redirect('lista_empleados')

    # Comprobación dentro del POST también
    if request.method == "POST":

        # Si el usuario es un Administrador (no superusuario), NO puede modificar a otros administradores
        if request.user.groups.filter(name='Administrador').exists() and not request.user.is_superuser:
            if empleado.usuario.groups.filter(name='Administrador').exists():
                if empleado.usuario != request.user:
                    messages.error(request, "No tienes permiso para modificar a otro administrador.")
                    return redirect('lista_empleados')


        # CAMPOS ACTUALES
        #if request.method == "POST":
        empleado.nombre = request.POST.get("nombre")
        empleado.email = request.POST.get("email")
        telefono = request.POST.get("telefono")

        # ✅ Validación de teléfono (solo dígitos y longitud exacta)
        if not telefono.isdigit() or len(telefono) != 10:
            messages.error(request, "El teléfono debe contener exactamente 10 dígitos numéricos.")
            return redirect('modificar_empleado', empleado_id=empleado.id)

        empleado.telefono = telefono
        
        puesto_nombre = request.POST.get("puesto")
        puesto_obj, _ = Puesto.objects.get_or_create(nombre=puesto_nombre)
        empleado.puesto = puesto_obj


        # Evitar que un administrador pueda poner a otro como 'Administrador'
        #if nuevo_rol == "Administrador" and not request.user.is_superuser:
        #    messages.error(request, "Solo el superusuario puede asignar el rol de Administrador.")
        #    return redirect('modificar_empleado', empleado_id=empleado.id)

        # NUEVOS CAMPOS
        empleado.domicilio = request.POST.get("domicilio")
        empleado.codigo_postal = request.POST.get("codigo_postal")
        empleado.rfc = request.POST.get("rfc")
        empleado.fecha_nacimiento = request.POST.get("fecha_nacimiento")
        empleado.tipo_sangre = request.POST.get("tipo_sangre")
        
        # ROL
        nuevo_rol = request.POST.get("rol")

        # Si es administrador editándose a sí mismo, NO puede cambiar su propio rol
        if (
            empleado.usuario == request.user and 
            request.user.groups.filter(name='Administrador').exists() and 
            not request.user.is_superuser
        ):
            grupos_actuales = list(empleado.usuario.groups.values_list('name', flat=True))
            if nuevo_rol not in grupos_actuales:
                messages.error(request, "No puedes cambiar tu propio rol.")
                return redirect('modificar_empleado', empleado_id=empleado.id)

        # Si pasa la validación, actualizamos el grupo
        empleado.usuario.groups.clear()
        try:
            grupo = Group.objects.get(name=nuevo_rol)
            empleado.usuario.groups.add(grupo)
        except Group.DoesNotExist:
            messages.error(request, f"El grupo '{nuevo_rol}' no existe.")
            return redirect('modificar_empleado', empleado_id=empleado.id)

    
        empleado.save()
        messages.success(request, "Empleado modificado correctamente.")
        return redirect('lista_empleados')

    # Para marcar el grupo actual seleccionado
    grupos_usuario = empleado.usuario.groups.values_list('name', flat=True)
    puestos = Puesto.objects.all()
    return render(request, 'gestion/modificar_empleado.html', {
        'empleado': empleado,
        'empleado_grupo': grupos_usuario,
        'puestos': puestos
    })

@login_required
def ver_empleado(request, empleado_id):
    if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
        return redirect('lista_empleados')
    
    empleado = get_object_or_404(Empleado, id=empleado_id)
    documentos = empleado.documentos.all()
    return render(request, 'gestion/ver_empleado.html', {
        'empleado': empleado,
        'documentos': documentos
    })

@login_required
def subir_documento_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)

    if request.method == "POST" and request.FILES.get('archivo'):
        EmpleadoDocumento.objects.create(
            empleado=empleado,
            archivo=request.FILES['archivo'],
            descripcion=request.POST.get('descripcion', '')
        )
        messages.success(request, "Documento subido correctamente.")
    return redirect('ver_empleado', empleado_id=empleado.id)

@login_required
def eliminar_documento_empleado(request, documento_id):
    documento = get_object_or_404(EmpleadoDocumento, id=documento_id)

    # Validar que solo admins o superusuarios puedan borrar
    if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
        return HttpResponseForbidden("No tienes permiso para eliminar este documento.")

    empleado_id = documento.empleado.id
    documento.delete()
    messages.success(request, "Documento eliminado correctamente.")
    return redirect('ver_empleado', empleado_id=empleado_id)

@login_required
def eliminar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)

    if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
        return redirect('lista_empleados')

    if request.user.groups.filter(name='Administrador').exists():
        if empleado.usuario.groups.filter(name='Administrador').exists():
            return redirect('lista_empleados')

    if request.method == "POST":
        empleado.usuario.delete()
        empleado.delete()
        return redirect('lista_empleados')

    return render(request, 'gestion/eliminar_empleado.html', {'empleado': empleado})

@login_required
def editar_usuario_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)

    # Comprobamos si el usuario autenticado es un admin (no superuser)
    usuario_actual_es_admin = request.user.groups.filter(name='Administrador').exists() and not request.user.is_superuser

    # Comprobamos si el empleado a editar es también admin
    empleado_es_admin = empleado.usuario.groups.filter(name='Administrador').exists()

    # Si ambas condiciones se cumplen, solo se puede ver, no editar
    solo_lectura = usuario_actual_es_admin and empleado_es_admin

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if empleado.usuario:
            user = empleado.usuario
            user.username = username
            user.email = email

            if password:
                user.set_password(password)

            user.save()
            messages.success(request, f"Usuario de {empleado.nombre} actualizado correctamente.")
        else:
            messages.error(request, "Este empleado no tiene un usuario asignado.")

    return redirect('lista_empleados')



#Invitacion por correo para ingresar al sistema 
@login_required
def enviar_invitacion_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)

    try:
        usuario = User.objects.get(email=empleado.email)
    except User.DoesNotExist:
        messages.error(request, "Este empleado no tiene un usuario asociado.")
        return redirect('lista_empleados')

    token = default_token_generator.make_token(usuario)
    uid = urlsafe_base64_encode(force_bytes(usuario.pk))
    dominio = get_current_site(request).domain
    reset_url = f"https://{dominio}/reset/{uid}/{token}/" # antes decía "http://"

    subject = "Establece tu contraseña"
    message = render_to_string("registration/email_invitacion.html", {
        'user': usuario,
        'reset_url': reset_url,
    })

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [usuario.email])

    messages.success(request, f"Se envió la invitación a {usuario.email}")
    return redirect('lista_empleados')

#Restablecer la contraseña por medio del usuario desde el login.html
def password_reset_by_username(request):
    if request.method == "POST":
        username = request.POST.get("username")
        try:
            user = User.objects.get(username=username)
            if user.email:
                current_site = get_current_site(request)
                subject = 'Restablece tu contraseña'
                message = render_to_string('registration/password_reset_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                messages.success(request, "Se ha enviado un correo con instrucciones.")
                return redirect('login')
            else:
                messages.warning(request, "Este usuario no tiene un correo asociado.")
        except User.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")
    return render(request, 'registration/password_reset_form.html')


