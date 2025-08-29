from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from .models import Cliente, Empleado, EmpleadoDocumento, Puesto, Obra, Servicio, TrabajoRealizado
from .forms import ClienteForm, ServicioForm, ObraForm
from django.db.models import Q
from django.http import HttpResponseForbidden  # para validación de permisos
from django.db.models import Max
from django.db.models.functions import Length
from django.http import JsonResponse
from django.db import IntegrityError
from django.core.files.base import ContentFile
from datetime import date
import base64, uuid

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
    usuario = request.user
    es_superusuario = usuario.is_superuser
    es_admin = usuario.groups.filter(name="Administrador").exists()
    es_supervisor = usuario.groups.filter(name="Supervisor").exists()
    es_empleado = request.user.groups.filter(name="Empleado").exists()
    servicios = None
    if es_empleado:
        servicios = Servicio.objects.filter(empleado_asignado=request.user)
    # Los empleados normales no necesitan flag especial; se asume por exclusión

    return render(request, "gestion/inicio.html", {
        "es_superusuario": es_superusuario,
        "es_admin": es_admin,
        "es_supervisor": es_supervisor,
        "servicios": servicios,
        "es_empleado": es_empleado,
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

def generar_clave_cliente():
    max_clave = Cliente.objects.aggregate(max=Max('clave'))['max']
    try:
        siguiente = int(max_clave) + 1 if max_clave else 1
    except:
        siguiente = Cliente.objects.count() + 1
    return f"{siguiente:04d}"  # Esto da formato 0001, 0010, 0213

@login_required
def agregar_cliente(request):
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            if not cliente.clave:
                cliente.clave = generar_clave_cliente()
            try:
                cliente.save()
                messages.success(request, "Cliente agregado correctamente.")
                return redirect('lista_clientes')
            except IntegrityError:
                messages.error(request, f"Ya existe un cliente con la clave {cliente.clave}.")
                form.add_error('clave', "Ya existe un cliente con esta clave.")
    else:
        sugerencia = generar_clave_cliente()
        form = ClienteForm(initial={'clave': sugerencia})

    return render(request, 'gestion/agregar_cliente.html', {'form': form})

@login_required
def modificar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente modificado correctamente.")
            return redirect('lista_clientes')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'gestion/modificar_cliente.html', {'form': form})



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

def generar_id_empleado(puesto_nombre):
    if not puesto_nombre:
        return "EMP001"
    puesto = puesto_nombre.upper()

    if puesto.startswith("NIVEL UNO"):
        prefijo = "NIVU"
    elif puesto.startswith("NIVEL DOS"):
        prefijo = "NIVD"
    else:
        palabras = puesto.split()
        prefijo = ''.join([p[0]+p[1] for p in palabras if p.isalpha()])[:3].upper()
        if len(prefijo) < 3:
            prefijo = (prefijo + "")[:3]  # relleno por si acaso

    # Buscar el número más alto existente con ese prefijo
    existentes = Empleado.objects.filter(id_personal__startswith=prefijo).annotate(
        longitud=Length('id_personal')
    ).order_by('-longitud', '-id_personal')

    if existentes.exists():
        ultimo = existentes.first().id_personal
        numero = ''.join(filter(str.isdigit, ultimo))
        siguiente = int(numero) + 1 if numero else 1
    else:
        siguiente = 1

    return f"{prefijo}{siguiente}"

@login_required
def agregar_empleado(request):
    if not request.user.is_superuser and not request.user.groups.filter(name='Administrador').exists():
        return redirect('lista_empleados')
    
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").upper()
        email = request.POST.get("email", "").upper()
        telefono = request.POST.get("telefono", "").upper()
        if not telefono.isdigit():
            messages.error(request, "El teléfono solo debe contener números.")
            return redirect("formulario_cliente")
        puesto_valor = request.POST.get("puesto", "").upper()

        # Si es un número, intenta buscar por ID. Si no, busca por nombre o crea uno nuevo.
        if puesto_valor and puesto_valor.isdigit():
            puesto = Puesto.objects.filter(id=puesto_valor).first()
        elif puesto_valor:
            puesto, _ = Puesto.objects.get_or_create(nombre=puesto_valor)
        else:
            puesto = None

        id_personal = generar_id_empleado(puesto.nombre) if puesto else ""
        
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
    id_sugerido = ""
    if puestos:
        primer_puesto = puestos.first()
        id_sugerido = generar_id_empleado(primer_puesto.nombre) if primer_puesto else ""

    return render(request, 'gestion/agregar_empleado.html', {
        'puestos': puestos,
        'id_sugerido': id_sugerido
    })


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
        empleado.nombre = request.POST.get("nombre", "").upper()
        empleado.id_personal = request.POST.get("id_personal", "").upper()
        empleado.email = request.POST.get("email")
        telefono = request.POST.get("telefono")

        # ✅ Validación de teléfono (solo dígitos y longitud exacta)
        if not telefono.isdigit():
            messages.error(request, "El teléfono debe contener solamente numeros.")
            return redirect('modificar_empleado', empleado_id=empleado.id)

        empleado.telefono = telefono
        
        puesto_nombre = request.POST.get("puesto", "").upper()
        puesto_obj, _ = Puesto.objects.get_or_create(nombre=puesto_nombre)
        empleado.puesto = puesto_obj


        # Evitar que un administrador pueda poner a otro como 'Administrador'
        #if nuevo_rol == "Administrador" and not request.user.is_superuser:
        #    messages.error(request, "Solo el superusuario puede asignar el rol de Administrador.")
        #    return redirect('modificar_empleado', empleado_id=empleado.id)

        # NUEVOS CAMPOS
        empleado.domicilio = request.POST.get("domicilio", "").upper()
        empleado.codigo_postal = request.POST.get("codigo_postal", "").upper()
        empleado.rfc = request.POST.get("rfc", "").upper()
        empleado.fecha_nacimiento = request.POST.get("fecha_nacimiento", "").upper()
        empleado.tipo_sangre = request.POST.get("tipo_sangre", "").upper()
        
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

#OBRAS

@login_required
def listado_obras(request):
    query = request.GET.get('q', '')

    obras = Obra.objects.all()

    if query:
        obras = obras.filter(
            Q(clave_obra__icontains=query) |
            Q(nombre__icontains=query) |
            Q(cliente__nombre__icontains=query)
        )

    return render(request, 'gestion/listado_obras.html', {
        'obras': obras,
        'query': query,
    })


@login_required
# Ver obras de un cliente
def ver_obras(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    obras = cliente.obras.all()
    return render(request, 'gestion/ver_obras.html', {'cliente': cliente, 'obras': obras})

# Agregar una nueva obra
@login_required
def agregar_obra(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    def construir_localizacion(cliente):
        partes = []
        if cliente.calle:
            partes.append(cliente.calle)
        if cliente.numero_exterior:
            partes.append(f"#{cliente.numero_exterior}")
        if cliente.numero_interior:
            partes.append(f"INT. {cliente.numero_interior}")
        if cliente.colonia:
            partes.append(f"Col. {cliente.colonia}")
        if hasattr(cliente, 'codigo_postal') and cliente.codigo_postal:
            partes.append(f"CP {cliente.codigo_postal}")
        if cliente.ciudad:
            partes.append(cliente.ciudad)
        return ', '.join(partes)

    if request.method == 'POST':
        form = ObraForm(request.POST)
        if form.is_valid():
            obra = form.save(commit=False)
            obra.cliente = cliente
            obra.localizacion = construir_localizacion(cliente)
            obra.save()
            messages.success(request, "Obra guardada correctamente.")
            return redirect('ver_obras', cliente_id=cliente.id)
    else:
        # 👇 Establecer localización inicial al mostrar el formulario
        form = ObraForm(initial={
            'localizacion': construir_localizacion(cliente)
        })

    return render(request, 'gestion/agregar_obra.html', {
        'form': form,
        'cliente': cliente
    })



@login_required
def modificar_obra(request, obra_id):
    obra = get_object_or_404(Obra, id=obra_id)
    cliente = obra.cliente  # Para mostrar el nombre del cliente y redireccionar correctamente

    if request.method == 'POST':
        form = ObraForm(request.POST, instance=obra)
        if form.is_valid():
            form.save()
            messages.success(request, "Obra modificada correctamente.")
            return redirect('ver_obras', cliente_id=cliente.id)
    else:
        form = ObraForm(instance=obra)

    return render(request, 'gestion/modificar_obra.html', {'form': form, 'cliente': cliente})

@login_required
def eliminar_obra(request, obra_id):
    obra = get_object_or_404(Obra, id=obra_id)
    cliente_id = obra.cliente.id
    obra.delete()
    messages.success(request, "Obra eliminada correctamente.")
    return redirect('ver_obras', cliente_id=cliente_id)

#SERVICIOS DE OBRA

def agregar_servicio(request, obra_id):
    obra = get_object_or_404(Obra, id=obra_id)
    trabajos = TrabajoRealizado.objects.all()

    if request.method == 'POST':
        post_data = request.POST.copy()
        trabajo_seleccionado = post_data.get('trabajo_realizado', '')

        if trabajo_seleccionado.startswith("nuevo_"):
            nombre_trabajo = trabajo_seleccionado.replace("nuevo_", "")
            trabajo_obj, created = TrabajoRealizado.objects.get_or_create(nombre=nombre_trabajo)
            post_data['trabajo_realizado'] = str(trabajo_obj.id)

        form = ServicioForm(post_data, request.FILES)
        form.fields['trabajo_realizado'].queryset = TrabajoRealizado.objects.all()

        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.obra = obra
            servicio.clave_cliente = obra.cliente.clave
            servicio.localizacion = obra.localizacion

            # Asignar el empleado seleccionado en el formulario
            empleado_seleccionado = form.cleaned_data.get('empleado_asignado')
            if empleado_seleccionado:
                servicio.empleado_asignado = empleado_seleccionado

            servicio.save()

            # Guardar firmas desde base64
            def guardar_firma(campo_name, input_name):
                data = request.POST.get(input_name)
                if data and "base64," in data:
                    try:
                        formato, imgstr = data.split(';base64,')
                        ext = formato.split('/')[-1]
                        archivo = ContentFile(base64.b64decode(imgstr), name=f"{uuid.uuid4()}.{ext}")
                        setattr(servicio, campo_name, archivo)
                    except Exception as e:
                        print(f"[ERROR] No se pudo guardar {campo_name}: {e}")

            guardar_firma('superviso_firma', 'firma_superviso_data')
            guardar_firma('capturo_firma', 'firma_capturo_data')
            guardar_firma('facturo_firma', 'firma_facturo_data')
            guardar_firma('autorizo_firma', 'firma_autorizo_data')
            guardar_firma('vobo_cliente_firma', 'firma_vobo_cliente_data')
            guardar_firma('lab_firma', 'firma_lab_data')

            servicio.save()
            return redirect('detalle_servicio', servicio_id=servicio.id)
    else:
        form = ServicioForm()
        if 'empleado_asignado' in form.fields:
            form.fields['empleado_asignado'].queryset = User.objects.filter(groups__name='Empleado')


    return render(request, 'gestion/agregar_servicio.html', {
        'form': form,
        'obra': obra,
        'cliente': obra.cliente,
        'trabajos': trabajos
    })

@login_required
def perfil_empleado(request):
    empleado = get_object_or_404(Empleado, user=request.user)
    servicios = empleado.servicios_asignados.all()
    return render(request, 'perfil_empleado.html', {
        'empleado': empleado,
        'servicios': servicios
    })

@login_required
def mis_servicios(request):
    usuario = request.user
    servicios = usuario.servicios_asignados.all()  # gracias al related_name
    return render(request, "gestion/mis_servicios.html", {"servicios": servicios})

@login_required
def ver_servicios(request, obra_id):
    obra = get_object_or_404(Obra, id=obra_id)
    servicios = obra.servicios.all()
    return render(request, 'gestion/ver_servicios.html', {
        'obra': obra,
        'servicios': servicios
    })

@login_required
def lista_servicios(request):
    user = request.user
    if user.groups.filter(name="Empleado").exists():
        # Solo los servicios asignados al empleado
        servicios = Servicio.objects.filter(empleado_asignado=user)
    elif user.groups.filter(name="Supervisor").exists():
        # Todos los servicios para supervisores
        servicios = Servicio.objects.all()
    else:
        # Administrador
        servicios = Servicio.objects.all()

    return render(request, "gestion/lista_servicios.html", {"servicios": servicios})

@login_required
def detalle_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    return render(request, "gestion/detalle_servicio.html", {
        "servicio": servicio
    })

@login_required
def modificar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    trabajos = TrabajoRealizado.objects.all()

    if request.method == "POST":
        post_data = request.POST.copy()
        trabajo_seleccionado = post_data.get('trabajo_realizado', '')

        if trabajo_seleccionado.startswith("nuevo_"):
            nombre_trabajo = trabajo_seleccionado.replace("nuevo_", "")
            trabajo_obj, created = TrabajoRealizado.objects.get_or_create(nombre=nombre_trabajo)
            post_data['trabajo_realizado'] = str(trabajo_obj.id)

        form = ServicioForm(post_data, request.FILES, instance=servicio)
        form.fields['trabajo_realizado'].queryset = TrabajoRealizado.objects.all()  # importante

        if form.is_valid():
            servicio = form.save(commit=False)

            if request.user.groups.filter(name="Empleado").exists():
                servicio.empleado_asignado = request.user

            # Guardar firmas desde base64
            def guardar_firma(servicio_obj, data, campo_name):
                if data and "base64," in data:
                    try:
                        formato, imgstr = data.split(';base64,')
                        ext = formato.split('/')[-1]
                        archivo = ContentFile(base64.b64decode(imgstr), name=f"{uuid.uuid4()}.{ext}")
                        setattr(servicio_obj, campo_name, archivo)
                    except Exception as e:
                        print(f"[ERROR] No se pudo guardar {campo_name}: {e}")

            guardar_firma(servicio, post_data.get('firma_superviso_data'), 'superviso_firma')
            guardar_firma(servicio, post_data.get('firma_capturo_data'), 'capturo_firma')
            guardar_firma(servicio, post_data.get('firma_facturo_data'), 'facturo_firma')
            guardar_firma(servicio, post_data.get('firma_autorizo_data'), 'autorizo_firma')
            guardar_firma(servicio, post_data.get('firma_vobo_cliente_data'), 'vobo_cliente_firma')
            guardar_firma(servicio, post_data.get('firma_lab_data'), 'lab_firma')

            servicio.save()
            return redirect("detalle_servicio", servicio_id=servicio.id)
    else:
        form = ServicioForm(instance=servicio)

    return render(request, "gestion/modificar_servicio.html", {
        "form": form,
        "servicio": servicio,
        "trabajos": trabajos
    })

def guardar_firma(servicio, data_url, campo_modelo):
    if not data_url or not data_url.startswith("data:image"):
        return  # No reemplazar si no llega nada

    header, base64data = data_url.split(";base64,")
    ext = header.split("/")[-1]
    try:
        decoded = base64.b64decode(base64data)
    except Exception:
        return

    filename = f"{campo_modelo}_{servicio.id}.{ext}"
    imagen = ContentFile(decoded, name=filename)
    setattr(servicio, campo_modelo, imagen)


@login_required
@require_POST
def eliminar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    obra_id = servicio.obra.id
    servicio.delete()
    messages.success(request, "Servicio eliminado correctamente.")
    return redirect('ver_servicios', obra_id=obra_id)



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



@login_required
def obtener_id_empleado_ajax(request):
    if request.method == 'GET':
        puesto_id = request.GET.get('puesto_id')

        if not puesto_id:
            return JsonResponse({'error': 'No se envió ID de puesto'}, status=400)

        try:
            puesto = Puesto.objects.get(id=puesto_id)
            nuevo_id = generar_id_empleado(puesto.nombre)
            return JsonResponse({'id_personal': nuevo_id})
        except Puesto.DoesNotExist:
            return JsonResponse({'error': 'Puesto no encontrado'}, status=404)