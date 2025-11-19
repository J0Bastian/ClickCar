from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template
from django.http import HttpResponse

from datetime import datetime
import random
import json
import os

from django.conf import settings

# Modelos
from .models.vehiculo import Vehiculo


from .models.usuarios import Usuario
from .models.reserva import Reserva

# PDF
from xhtml2pdf import pisa
from django.shortcuts import render, redirect, get_object_or_404
from .models import Vehiculo


def home(request):
    vehiculos = Vehiculo.objects.all()
    return render(request, 'core/home.html', {'vehiculos': vehiculos})

def exit(request):
    logout(request)  # Limpia sesión de Django
    request.session.flush()  # Limpia tu sesión personalizada
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('home')



def reserva(request, id):

    vehiculo = Vehiculo.objects.get(pk=id)

    if request.method == "POST":
        fecha_inicio = datetime.strptime(request.POST["fecha_inicio"], "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(request.POST["fecha_fin"], "%Y-%m-%d").date()

        # Verificar usuario logueado
        if "usuario_id" not in request.session:
            messages.error(request, "Debes iniciar sesión para realizar una reserva.")
            return redirect("login")

        usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])

        # 1️⃣ Validar que no exista reserva cruzada
        conflicto = Reserva.objects.filter(
            auto=vehiculo,
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio
        ).exists()

        if conflicto:
            messages.error(request, "El vehículo NO está disponible para esas fechas.")
            return redirect("reserva", id=id)

        # 2️⃣ Aquí va el cálculo (ESTÁ BIEN COMO LO TIENES)
        dias = (fecha_fin - fecha_inicio).days + 1
        valor_total = dias * vehiculo.precio_dia

        # 3️⃣ Guardar temporal en sesión para pantalla de confirmación
        request.session["datos_reserva"] = {
            "vehiculo_id": vehiculo.id_vehiculo,
            "fecha_inicio": str(fecha_inicio),
            "fecha_fin": str(fecha_fin),
            "dias": dias,
            "valor_total": float(valor_total)
        }

        # 4️⃣ Ir a pantalla de confirmación
        return redirect("confirmar_reserva")

    return render(request, "core/reserva.html", {"vehiculo": vehiculo})


def confirmar_reserva(request):
    if "datos_reserva" not in request.session:
        return redirect("home")

    data = request.session["datos_reserva"]

    # Obtener el vehículo correctamente
    vehiculo = Vehiculo.objects.get(id_vehiculo=data["vehiculo_id"])

    if request.method == "POST":
        usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])

        Reserva.objects.create(
            usuario=usuario,
            auto=vehiculo,
            fecha_inicio=data["fecha_inicio"],
            fecha_fin=data["fecha_fin"],
            valor_total=data["valor_total"],
        )

        del request.session["datos_reserva"]
        messages.success(request, "¡Reserva creada exitosamente!")

        return redirect("home")

    return render(request, "core/confirmar_reserva.html", {
        "vehiculo": vehiculo,
        "datos": data
    })

def login_usuario(request):
    if request.method == 'POST':
        correo = request.POST.get('username')
        contrasena = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(correo=correo, contrasena=contrasena)
            
            if usuario.activo:

                # 🔥 Guardar toda la información que vas a usar
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_nombre'] = usuario.nombre
                request.session['usuario_correo'] = usuario.correo
                request.session['usuario_telefono'] = usuario.telefono

                # 🔥 Rol (para admin)
                request.session['usuario_rol'] = usuario.nombre_rol

                messages.success(request, f'Bienvenido {usuario.nombre}')
                return redirect('products')

            else:
                messages.error(request, 'Tu cuenta está inactiva.')

        except Usuario.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'accounts/login.html')
# Si no es POST o hubo error:

def products(request):
    # Verificar si el usuario inició sesión correctamente
    if not request.session.get('usuario_id'):
        messages.warning(request, 'Debes iniciar sesión para ver los productos.')
        return redirect('login')

    # Si está autenticado, mostrar productos
    vehiculos = Vehiculo.objects.all()
    return render(request, 'core/products.html', {'vehiculos': vehiculos})


def editar_usuario(request, id):
    if request.session.get('usuario_rol') != "admin":
        messages.error(request, "No tienes permisos para editar usuarios.")
        return redirect('home')

    usuario = Usuario.objects.get(pk=id)

    if request.method == "POST":
        usuario.nombre = request.POST.get("nombre")
        usuario.correo = request.POST.get("correo")
        usuario.telefono = request.POST.get("telefono")
        usuario.nombre_rol = request.POST.get("rol")
        usuario.save()

        messages.success(request, "Usuario actualizado correctamente.")
        return redirect('perfil_usuario', id=id)

    return render(request, 'core/editar_usuario.html', {"usuario": usuario})

def eliminar_usuario(request, id):
    if request.session.get('usuario_rol') != "admin":
        messages.error(request, "No tienes permisos para eliminar usuarios.")
        return redirect('home')

    usuario = Usuario.objects.get(pk=id)
    usuario.delete()

    messages.success(request, "Usuario eliminado correctamente.")
    return redirect('visualizar_perfiles')

def registro_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        telefono = request.POST.get('telefono')

        # Validar si el correo ya existe
        if Usuario.objects.filter(correo=correo).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect('registro')

        # Generar código
        codigo = random.randint(100000, 999999)

        # Guardar temporalmente en sesión
        request.session['registro_temp'] = {
            'nombre': nombre,
            'correo': correo,
            'contrasena': contrasena,
            'telefono': telefono,
            'codigo': codigo
        }

        # Enviar correo
        send_mail(
            'Código de verificación - ClickCar',
            f'Tu código de verificación es: {codigo}',
            settings.DEFAULT_FROM_EMAIL,
            [correo],
            fail_silently=False,
        )

        messages.info(request, "Te enviamos un código de verificación.")
        return redirect('verificar_codigo')

    return render(request, 'registration/registro.html')

def verificar_codigo(request):
    if request.method == 'POST':
        codigo_usuario = request.POST.get('codigo')
        temp = request.session.get('registro_temp')

        if not temp:
            messages.error(request, "Tu sesión expiró. Regístrate de nuevo.")
            return redirect('registro')

        if str(codigo_usuario) != str(temp['codigo']):
            messages.error(request, "Código incorrecto.")
            return redirect('verificar_codigo')

        # Crear usuario en la BD
        usuario = Usuario.objects.create(
            nombre=temp['nombre'],
            correo=temp['correo'],
            contrasena=temp['contrasena'],
            telefono=temp['telefono']
        )

        # Guardar en JSON
        guardar_en_json(usuario)

        del request.session['registro_temp']

        messages.success(request, "Registro completado. Ahora inicia sesión.")
        return redirect('login')

    return render(request, 'registration/validar_codigo.html')

def guardar_en_json(usuario):
    ruta = os.path.join(settings.BASE_DIR, 'core', 'fixtures', 'usuarios.json')

    if os.path.exists(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
    else:
        usuarios = []

    nuevo = {
        "model": "core.usuario",
        "pk": usuario.id_usuario,
        "fields": {
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "contrasena": usuario.contrasena,
            "telefono": usuario.telefono,
            "activo": usuario.activo
        }
    }

    usuarios.append(nuevo)

    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

def olvide_password(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')

        # Validar si existe
        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            messages.error(request, "Ese correo no está registrado.")
            return redirect('olvide_password')

        # Generar código
        codigo = random.randint(100000, 999999)

        request.session['reset'] = {
            'correo': correo,
            'codigo': codigo
        }

        # Enviar código
        send_mail(
            'Recuperación de contraseña - ClickCar',
            f'Tu código de recuperación es: {codigo}',
            settings.DEFAULT_FROM_EMAIL,
            [correo],
            fail_silently=False,
        )

        messages.info(request, "Te enviamos un código a tu correo.")
        return redirect('verificar_codigo_reset')

    return render(request, 'registration/olvide_password.html')

# 2. Validar código
def verificar_codigo_reset(request):
    if request.method == 'POST':
        codigo_usuario = request.POST.get('codigo')
        temp = request.session.get('reset')

        if not temp:
            messages.error(request, "Tu sesión expiró.")
            return redirect('olvide_password')

        if str(temp['codigo']) != str(codigo_usuario):
            messages.error(request, "Código incorrecto.")
            return redirect('verificar_codigo_reset')

        return redirect('nueva_contrasena')

    return render(request, 'registration/verificar_codigo_reset.html')

# 3. Crear nueva contraseña
def nueva_contrasena(request):
    temp = request.session.get('reset')

    if not temp:
        messages.error(request, "Sesión expirada.")
        return redirect('olvide_password')

    if request.method == 'POST':
        nueva = request.POST.get('contrasena')

        usuario = Usuario.objects.get(correo=temp['correo'])
        usuario.contrasena = nueva
        usuario.save()

        del request.session['reset']

        messages.success(request, "Contraseña actualizada. Ahora inicia sesión.")
        return redirect('login')

    return render(request, 'registration/nueva_contrasena.html')

def visualizar_perfiles(request):

    if not request.session.get('usuario_id'):
        messages.warning(request, "Debes iniciar sesión.")
        return redirect('login')

    if request.session.get('usuario_rol') != 'admin':
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('home')

    usuarios = Usuario.objects.all()
    reservas = Reserva.objects.all().order_by('-fecha_reserva')
    vehiculos = Vehiculo.objects.all()     # 👈 AÑADIDO AQUÍ

    return render(request, 'core/visualizar_perfiles.html', {
        'usuarios': usuarios,
        'reservas': reservas,
        'vehiculos': vehiculos             # 👈 AÑADIDO AQUÍ
    })


def perfil_usuario(request, id):
    # Validación: debe estar logueado
    try:
        usuario = Usuario.objects.get(id_usuario=id)
    except Usuario.DoesNotExist:
        messages.error(request, "El usuario no existe")
        return redirect('VisualizarPerfiles')

    return render(request, 'core/perfil_usuario.html', {
        'usuario': usuario
    })



def panel_reservas(request):
    if not request.session.get('usuario_id'):
        messages.warning(request, "Debes iniciar sesión.")
        return redirect('login')

    if request.session.get('usuario_rol') != "admin":
        messages.error(request, "No tienes permisos para ver reservas.")
        return redirect('home')

    reservas = Reserva.objects.all().order_by('-fecha_reserva')

    return render(request, 'core/panel_reservas.html', {
        'reservas': reservas
    })

def mis_reservas(request):

    if "usuario_id" not in request.session:
        return redirect("login")

    usuario_id = request.session["usuario_id"]

    reservas = Reserva.objects.filter(usuario_id=usuario_id).order_by("-fecha_reserva")

    return render(request, "core/mis_reservas.html", {
        "reservas": reservas
    })
def admin_reservas(request):

    # Validar que sea admin
    if request.session.get("usuario_rol") != "admin":
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect("home")

    # Traemos todas las reservas ordenadas por fecha
    reservas = Reserva.objects.select_related("usuario", "auto").order_by("-fecha_reserva")

    return render(request, "core/admin_reservas.html", {"reservas": reservas})


def ver_detalle_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, pk=id_reserva)

    context = {
        "reserva": reserva
    }
    return render(request, "core/detalle_reserva.html", context)

def descargar_pdf(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    template_path = 'core/pdf_reserva.html'
    context = {'reserva': reserva}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reserva_{id_reserva}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error creando PDF")

    return response

def descargar_pdf_usuario(request):
    if "datos_reserva" not in request.session:
        return redirect("home")

    data = request.session["datos_reserva"]
    vehiculo = Vehiculo.objects.get(id_vehiculo=data["vehiculo_id"])
    usuario = Usuario.objects.get(id_usuario=request.session["usuario_id"])

    template = get_template("core/pdf_reserva.html")

    html = template.render({
        "vehiculo": vehiculo,
        "datos": data,
        "usuario": usuario
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reserva.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generando PDF")
    return response

def lista_vehiculos(request):
    vehiculos = Vehiculo.objects.all()
    return render(request, 'vehiculos/lista_vehiculos.html', {'vehiculos': vehiculos})


def eliminar_vehiculo(request, id_vehiculo):
    vehiculo = get_object_or_404(Vehiculo, id_vehiculo=id_vehiculo)
    vehiculo.delete()
    return redirect('visualizar_perfiles')

def agregar_vehiculo(request):
    if request.method == "POST":

        marca = request.POST.get("marca")
        modelo = request.POST.get("modelo")
        categoria = request.POST.get("categoria")
        anio = request.POST.get("anio")
        precio_dia = request.POST.get("precio_dia")
        descripcion = request.POST.get("descripcion")
        foto_url = request.POST.get("foto_url")
        combustible = request.POST.get("combustible")
        asientos = request.POST.get("asientos")
        color = request.POST.get("color")

        vehiculo = Vehiculo.objects.create(
            marca=marca,
            modelo=modelo,
            categoria=categoria,
            anio=anio,
            precio_dia=precio_dia,
            descripcion=descripcion,
            foto_url=foto_url,
            combustible=combustible,
            asientos=asientos,
            color=color
        )

        return redirect('lista_vehiculos')

    return render(request, 'core/agregar_vehiculo.html')
