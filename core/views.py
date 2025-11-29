from datetime import datetime, date
from decimal import Decimal
import random
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import get_template

from xhtml2pdf import pisa

from .models.vehiculo import Vehiculo
from .models.usuarios import Usuario
from .models.reserva import Reserva
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

logging.getLogger("xhtml2pdf").setLevel(logging.ERROR)


# ============================================================
#                   PÁGINAS BÁSICAS
# ============================================================

def home(request):
    vehiculos = Vehiculo.objects.all()
    return render(request, "core/home.html", {"vehiculos": vehiculos})


def exit(request):
    logout(request)
    request.session.flush()

    messages.info(request, "Sesión cerrada correctamente.", extra_tags="login")
    return redirect("home")



from datetime import date, datetime

def reserva(request, id_auto):
    vehiculo = get_object_or_404(Vehiculo, id_auto=id_auto)

    # Enviar fecha de hoy para bloquear días pasados en el calendario
    hoy = date.today().isoformat()

    if request.method == "POST":

        usuario_id = request.session.get("usuario_id")
        if not usuario_id:
            return redirect("login")

        try:
            fecha_inicio = datetime.strptime(request.POST["fecha_inicio"], "%Y-%m-%d").date()
            fecha_fin = datetime.strptime(request.POST["fecha_fin"], "%Y-%m-%d").date()
        except:
            return redirect("reserva", id_auto=id_auto)

        # Evitar reservar fechas pasadas
        if fecha_inicio < date.today():
            return redirect("reserva", id_auto=id_auto)

        # Final no puede ser menor al inicio
        if fecha_fin < fecha_inicio:
            return redirect("reserva", id_auto=id_auto)

        conflicto = Reserva.objects.filter(
            auto=vehiculo,
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio
        ).exists()

        if conflicto:
            return redirect("reserva", id_auto=id_auto)

        dias = (fecha_fin - fecha_inicio).days + 1
        valor_total = dias * vehiculo.precio_dia

        request.session["datos_reserva"] = {
            "vehiculo_id": vehiculo.id_auto,
            "fecha_inicio": str(fecha_inicio),
            "fecha_fin": str(fecha_fin),
            "dias": dias,
            "valor_total": float(valor_total),
        }
        request.session.modified = True
        request.session.save()

        return redirect("confirmar_reserva")

    return render(request, "core/reserva.html", {
        "vehiculo": vehiculo,
        "hoy": hoy
    })






def confirmar_reserva(request):
    if "datos_reserva" not in request.session:
        messages.error(request, "No hay una reserva en proceso.", extra_tags="confirmar")
        return redirect("home")

    data = request.session["datos_reserva"]
    vehiculo = get_object_or_404(Vehiculo, id_auto=data["vehiculo_id"])

    # Usuario autenticado
    usuario_id = request.session.get("usuario_id") or request.session.get("id_usuario")
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    if request.method == "POST":

        fecha_inicio = datetime.strptime(data["fecha_inicio"], "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(data["fecha_fin"], "%Y-%m-%d").date()

        nueva_reserva = Reserva.objects.create(
            usuario=usuario,
            auto=vehiculo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            valor_total=Decimal(str(data["valor_total"])),
            estado="confirmada",
        )

        # Limpiar la sesión
        del request.session["datos_reserva"]

        # Correo en HTML
        html_template = get_template("accounts/confirmacion_correo.html")
        html_message = html_template.render({
            "usuario": usuario,
            "vehiculo": vehiculo,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "valor_total": data["valor_total"],
        })

        send_mail(
            subject="Reserva Confirmada - ClickCar",
            message="Tu cliente de correo no soporta HTML.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.correo],
            fail_silently=False,
            html_message=html_message,
        )

        messages.success(request, "Reserva creada exitosamente.", extra_tags="confirmar")
        return redirect("mis_reservas")

    # GET mostrar resumen
    dias = data["dias"]
    subtotal = Decimal(str(vehiculo.precio_dia)) * Decimal(str(dias)) / Decimal("1.19")
    iva = Decimal(str(data["valor_total"])) - subtotal

    return render(request, "core/confirmar_reserva.html", {
        "vehiculo": vehiculo,
        "usuario": usuario, 
        "datos": {
            **data,
            "subtotal": round(subtotal, 2),
            "iva": round(iva, 2),
        }
    })




def login_usuario(request):

    if request.method == "POST":
        correo = request.POST.get("username")
        contrasena = request.POST.get("password")

        try:
            usuario = Usuario.objects.get(correo=correo, contrasena=contrasena)
        except Usuario.DoesNotExist:
            messages.error(request, "Correo o contraseña incorrectos.", extra_tags="login error")
            return render(request, "accounts/login.html")

        if not usuario.activo:
            messages.error(request, "Tu cuenta está inactiva.", extra_tags="login error")
            return render(request, "accounts/login.html")

        request.session["usuario_id"] = usuario.id_usuario
        request.session["id_usuario"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_correo"] = usuario.correo
        request.session["usuario_telefono"] = usuario.telefono
        request.session["usuario_rol"] = usuario.nombre_rol

        messages.success(request, f"Bienvenido {usuario.nombre}", extra_tags="login success")
        return redirect("products")

    return render(request, "accounts/login.html")


def products(request):
    if not request.session.get("usuario_id"):
        messages.warning(request, "Debes iniciar sesión para ver los productos.", extra_tags="login warning")
        return redirect("login")

    vehiculos = Vehiculo.objects.all()
    return render(request, "core/products.html", {"vehiculos": vehiculos})


# ADMIN – EDITAR / ELIMINAR USUARIOS


def editar_usuario(request, id):
    if request.session.get("usuario_rol") != "admin":
        messages.error(request, "Acceso denegado.", extra_tags="editar_usuario error")
        return redirect("home")

    usuario = get_object_or_404(Usuario, pk=id)

    if request.method == "POST":
        usuario.nombre = request.POST.get("nombre")
        usuario.correo = request.POST.get("correo")
        usuario.telefono = request.POST.get("telefono")
        usuario.nombre_rol = request.POST.get("rol")
        usuario.activo = "activo" in request.POST

        # FOTO SUBIDA DESDE LA WEEEEB
        if "foto_perfil" in request.FILES:
            usuario.foto_perfil = request.FILES["foto_perfil"]

        usuario.save()

        messages.success(request, "Usuario actualizado correctamente.", extra_tags="editar_usuario success")
        return redirect("perfil_usuario", id=id)

    return render(request, "core/editar_usuario.html", {"usuario": usuario})



def eliminar_usuario(request, id):
    if request.session.get("usuario_rol") != "admin":
        messages.error(request, "Acceso denegado.", extra_tags="admin_perfiles error")
        return redirect("home")

    usuario = get_object_or_404(Usuario, pk=id)
    usuario.delete()

    messages.success(request, "Usuario eliminado.", extra_tags="admin_perfiles success")
    return redirect("visualizar_perfiles")




def editar_perfil(request):
    # Identificar usuario logueado
    usuario_id = request.session.get("usuario_id") or request.session.get("id_usuario")

    if not usuario_id:
        messages.error(request, "Debes iniciar sesión.", extra_tags="perfil error")
        return redirect("login")

    usuario = get_object_or_404(Usuario, pk=usuario_id)

    if request.method == "POST":
        usuario.nombre = request.POST.get("nombre")
        usuario.correo = request.POST.get("correo")
        usuario.telefono = request.POST.get("telefono")

        # FOTO SUBIDA POR EL CLIENTE
        if "foto_perfil" in request.FILES:
            usuario.foto_perfil = request.FILES["foto_perfil"]

        usuario.save()

        messages.success(request, "Perfil actualizado correctamente.", extra_tags="perfil success")

        
        return redirect("perfil_usuario", id=usuario.id_usuario)

    return render(request, "core/editar_perfil_cliente.html", {"usuario": usuario})



def registro_usuario(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")
        contrasena = request.POST.get("contrasena")
        telefono = request.POST.get("telefono")

        # FOTO SUBIDA
        foto = request.FILES.get("foto")  # <-- IMPORTANTE

        if Usuario.objects.filter(correo=correo).exists():
            messages.error(request, "Este correo ya existe.", extra_tags="registro error")
            return redirect("registro")

        codigo = random.randint(100000, 999999)

        # Guardamos todo en la sesión
        request.session["registro_temp"] = {
            "nombre": nombre,
            "correo": correo,
            "contrasena": contrasena,
            "telefono": telefono,
            "codigo": codigo,
        }

        # Guardamos la foto temporalmente en la sesión
        if foto:
            request.session["registro_foto_nombre"] = foto.name
            request.session["registro_foto_contenido"] = foto.read().decode("latin-1")

        # Envimos código por correo
        send_mail(
            "Código de verificación - ClickCar",
            f"Tu código es: {codigo}",
            settings.DEFAULT_FROM_EMAIL,
            [correo],
        )

        messages.info(request, "Te enviamos un código a tu correo.", extra_tags="registro info")
        return redirect("verificar_codigo")

    return render(request, "registration/registro.html")


def verificar_codigo(request):
    temp = request.session.get("registro_temp")

    if not temp:
        messages.error(request, "Sesión expirada.", extra_tags="codigo_registro error")
        return redirect("registro")

    if request.method == "POST":
        if request.POST.get("codigo") != str(temp["codigo"]):
            messages.error(request, "Código incorrecto.", extra_tags="codigo_registro error")
            return redirect("verificar_codigo")

    
        #   RECUPERAR FOTO DE LA SESIÓN
        foto_contenido = request.session.get("registro_foto_contenido")
        foto_nombre = request.session.get("registro_foto_nombre")
        foto_file = None

        if foto_contenido and foto_nombre:
            from django.core.files.base import ContentFile
            
            # Foto convertida desde la sesión
            foto_file = ContentFile(foto_contenido.encode("latin-1"), name=foto_nombre)


        #      CREAR EL USUARIO
        Usuario.objects.create(
            nombre=temp["nombre"],
            correo=temp["correo"],
            contrasena=temp["contrasena"],
            telefono=temp["telefono"],
            nombre_rol="cliente",
            foto_perfil=foto_file 
        )


        #  LIMPIAR DATOS TEMPORALES
        del request.session["registro_temp"]
        if "registro_foto_contenido" in request.session:
            del request.session["registro_foto_contenido"]
        if "registro_foto_nombre" in request.session:
            del request.session["registro_foto_nombre"]

        messages.success(request, "Cuenta creada. Ahora puedes iniciar sesión.",
                         extra_tags="codigo_registro success")
        return redirect("login")

    return render(request, "registration/validar_codigo.html")



def olvide_password(request):
    if request.method == "POST":
        correo = request.POST.get("correo")

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            messages.error(request, "Ese correo no está registrado.", extra_tags="olvide error")
            return redirect("olvide_password")

        codigo = random.randint(100000, 999999)

        request.session["reset"] = {"correo": correo, "codigo": codigo}

        send_mail(
            "Recuperación de Contraseña",
            f"Tu código es: {codigo}",
            settings.DEFAULT_FROM_EMAIL,
            [correo],
        )

        messages.info(request, "Te enviamos un código a tu correo.", extra_tags="olvide info")
        return redirect("verificar_codigo_reset")

    return render(request, "registration/olvide_password.html")


def verificar_codigo_reset(request):
    if request.method == "POST":
        temp = request.session.get("reset")
        if not temp:
            messages.error(request, "Sesión expirada.", extra_tags="codigo_reset error")
            return redirect("olvide_password")

        if request.POST.get("codigo") != str(temp["codigo"]):
            messages.error(request, "Código incorrecto.", extra_tags="codigo_reset error")
            return redirect("verificar_codigo_reset")

        return redirect("nueva_contrasena")

    return render(request, "registration/verificar_codigo_reset.html")


def nueva_contrasena(request):
    temp = request.session.get("reset")

    if not temp:
        messages.error(request, "Sesión expirada.", extra_tags="cambiar_pass error")
        return redirect("olvide_password")

    if request.method == "POST":
        usuario = get_object_or_404(Usuario, correo=temp["correo"])
        usuario.contrasena = request.POST.get("contrasena")
        usuario.save()

        del request.session["reset"]

        messages.success(request, "Contraseña actualizada.", extra_tags="cambiar_pass success")
        return redirect("login")

    return render(request, "registration/nueva_contrasena.html")



def visualizar_perfiles(request):
    if request.session.get("usuario_rol") != "admin":
        messages.error(request, "Acceso denegado.", extra_tags="admin_perfiles error")
        return redirect("home")

    return render(request, "core/visualizar_perfiles.html", {
        "usuarios": Usuario.objects.all(),
        "reservas": Reserva.objects.all(),
        "vehiculos": Vehiculo.objects.all()
    })


def perfil_usuario(request, id):
    usuario = get_object_or_404(Usuario, id_usuario=id)
    return render(request, "core/perfil_usuario.html", {"usuario": usuario})


def panel_reservas(request):
    if request.session.get("usuario_rol") != "admin":
        messages.error(request, "Acceso denegado.", extra_tags="admin_reservas error")
        return redirect("home")

    return render(request, "core/panel_reservas.html", {
        "reservas": Reserva.objects.all()
    })


def mis_reservas(request):
    usuario_id = request.session.get("usuario_id") or request.session.get("id_usuario")
    if not usuario_id:
        return redirect("login")

    reservas = Reserva.objects.filter(usuario_id=usuario_id).order_by("-fecha_reserva")

    return render(request, "core/mis_reservas.html", {"reservas": reservas})



def ver_detalle_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    # Solo admin o el dueño de la reserva
    if request.session.get("usuario_rol") != "admin":
        usuario_id = request.session.get("usuario_id") or request.session.get("id_usuario")
        if reserva.usuario_id != usuario_id:
            messages.error(request, "No puedes ver reservas de otros usuarios.")
            return redirect("mis_reservas")

    return render(request, "core/detalle_reserva.html", {"reserva": reserva})



def descargar_pdf(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    template = get_template("core/pdf_reserva.html")

    html = template.render({
        "vehiculo": reserva.auto,
        "usuario": reserva.usuario,
        "datos": {
            "vehiculo_id": reserva.auto.id_auto,
            "fecha_inicio": reserva.fecha_inicio,
            "fecha_fin": reserva.fecha_fin,
            "dias": (reserva.fecha_fin - reserva.fecha_inicio).days + 1,
            "valor_total": reserva.valor_total,
        }
    })

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="reserva_{id_reserva}.pdf"'

    pisa.CreatePDF(html, dest=response)
    return response

def descargar_pdf_usuario(request):
    """
    Descargar el PDF de la reserva que está en proceso (usa los datos en sesión).
    """
    if "datos_reserva" not in request.session or (
        "usuario_id" not in request.session and "id_usuario" not in request.session
    ):
        return redirect("home")

    data = request.session["datos_reserva"]

    vehiculo = get_object_or_404(Vehiculo, id_auto=data["vehiculo_id"])
    usuario_id = request.session.get("usuario_id") or request.session.get("id_usuario")
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    template = get_template("core/pdf_reserva.html")
    html = template.render(
        {"vehiculo": vehiculo, "usuario": usuario, "datos": data}
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="reserva.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generando PDF")

    return response


def cancelar_reserva(request, id_reserva):
    usuario_id = request.session.get("usuario_id") or request.session.get("id_usuario")
    if not usuario_id:
        return redirect("login")

    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    # Validación de seguridad
    if reserva.usuario.id_usuario != usuario_id:
        messages.error(request, "No puedes cancelar reservas de otros usuarios.", extra_tags="mis_reservas error")
        return redirect("mis_reservas")

    # Ya cancelada
    if reserva.estado == "cancelada":
        messages.warning(request, "La reserva ya está cancelada.", extra_tags="mis_reservas warning")
        return redirect("mis_reservas")

    # No cancelar si ya inició
    if reserva.fecha_inicio <= date.today():
        messages.error(request, "No puedes cancelar una reserva que ya inició.", extra_tags="mis_reservas error")
        return redirect("mis_reservas")

    # ✔ CANCELAR LA RESERVA
    reserva.estado = "cancelada"
    reserva.save()

    # ✔ EMAIL HTML
    html_template = get_template("accounts/reserva_cancelada.html")
    html_message = html_template.render({
        "usuario": reserva.usuario,
        "reserva": reserva
    })

    send_mail(
        subject="Reserva Cancelada - ClickCar",
        message="Tu correo no soporta HTML, pero tu reserva fue cancelada exitosamente.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reserva.usuario.correo],
        fail_silently=False,
        html_message=html_message,
    )

    # Mensaje para mostrar en Mis Reservas
    messages.success(request, "Reserva cancelada correctamente.", extra_tags="mis_reservas success")

    return redirect("mis_reservas")

def lista_vehiculos(request):
    if request.session.get("usuario_rol") != "admin":
        messages.error(request, "Acceso denegado.", extra_tags="vehiculos error")
        return redirect("home")

    vehiculos = Vehiculo.objects.all()
    return render(request, "core/lista_vehiculos.html", {"vehiculos": vehiculos})



def agregar_vehiculo(request):
    if request.session.get("usuario_rol") != "admin":
        return redirect("home")

    if request.method == "POST":
        marca = request.POST.get("marca")
        modelo = request.POST.get("modelo")
        
        # Convertir año vacío en NULL
        anio_raw = request.POST.get("anio")
        anio = anio_raw if anio_raw and anio_raw.strip() != "" else None

        precio_dia = request.POST.get("precio_dia")
        descripcion = request.POST.get("descripcion")
        categoria = request.POST.get("categoria")
        combustible = request.POST.get("combustible")
        asientos = request.POST.get("asientos")
        color = request.POST.get("color")
        foto = request.FILES.get("foto")

        Vehiculo.objects.create(
            marca=marca,
            modelo=modelo,
            categoria=categoria,
            anio=anio,              # ← AQUÍ YA VA NULL SI ESTABA VACÍO
            precio_dia=precio_dia,
            descripcion=descripcion,
            combustible=combustible,
            asientos=asientos,
            color=color,
            foto=foto,
            disponible=True
        )

        return redirect("lista_vehiculos")

    return render(request, "core/agregar_vehiculo.html")










def editar_vehiculo(request, id_auto):
    if request.session.get("usuario_rol") != "admin":
        messages.error(request, "Acceso denegado.", extra_tags="vehiculos error")
        return redirect("home")

    vehiculo = get_object_or_404(Vehiculo, id_auto=id_auto)

    if request.method == "POST":
        vehiculo.marca = request.POST.get("marca")
        vehiculo.modelo = request.POST.get("modelo")
        vehiculo.categoria = request.POST.get("categoria")
        vehiculo.anio = request.POST.get("anio")
        vehiculo.precio_dia = request.POST.get("precio_dia")
        vehiculo.descripcion = request.POST.get("descripcion")
        vehiculo.combustible = request.POST.get("combustible")
        vehiculo.asientos = request.POST.get("asientos")
        vehiculo.color = request.POST.get("color")

        #FOTO NUEVA
        nueva_foto = request.FILES.get("foto")

        if nueva_foto:
            error_img = validar_imagen(nueva_foto)
            if error_img:
                messages.error(request, error_img, extra_tags="vehiculos error")
                return redirect("editar_vehiculo", id_auto=id_auto)

            vehiculo.foto = nueva_foto  # ✔ reemplaza la foto anterior

        vehiculo.save()

        messages.success(request, "Vehículo actualizado correctamente.", extra_tags="vehiculos success")
        return redirect("lista_vehiculos")

    return render(request, "core/editar_vehiculo.html", {"vehiculo": vehiculo})












def eliminar_vehiculo(request, id_auto):
    if request.session.get("usuario_rol") != "admin":
        messages.error(request, "Acceso denegado.", extra_tags="vehiculos error")
        return redirect("home")

    vehiculo = get_object_or_404(Vehiculo, id_auto=id_auto)
    vehiculo.delete()

    messages.success(request, "Vehículo eliminado correctamente.", extra_tags="vehiculos success")
    return redirect("lista_vehiculos")




def pdf_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    template_path = "pdf/reserva_premium.html"
    template = get_template(template_path)

    html = template.render({
        "reserva": reserva,
        "usuario": reserva.usuario,
        "vehiculo": reserva.auto,
    })

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="Reserva_{reserva.id_reserva}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generando el PDF", status=500)

    return response


def validar_imagen(foto, max_mb=5):
    if not foto:
        return None

    # Validar extensión permitida
    extensiones_validas = ["jpg", "jpeg", "png", "webp"]
    ext = foto.name.split(".")[-1].lower()

    if ext not in extensiones_validas:
        return "Formato inválido. Solo se permiten JPG, JPEG, PNG o WEBP."

    # Validar tamaño máximo
    max_bytes = max_mb * 1024 * 1024
    if foto.size > max_bytes:
        return f"La imagen supera el tamaño máximo permitido: {max_mb} MB."

    return None
