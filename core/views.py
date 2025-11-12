from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render
from .models.vehiculo import Vehiculo
from django.contrib import messages
from .models.usuarios import Usuario




def home(request):
    return render(request, 'core/home.html')  # Ajusta al nombre real de tu template


def exit(request):
    logout(request)  # Limpia sesión de Django
    request.session.flush()  # Limpia tu sesión personalizada
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('home')



def reserva(request, id):
    # Aquí puedes buscar el vehículo por su ID
    vehiculo = Vehiculo.objects.get(pk=id)
    return render(request, 'core/reserva.html', {'vehiculo': vehiculo})


def login_usuario(request):
    if request.method == 'POST':
        correo = request.POST.get('username')
        contrasena = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(correo=correo, contrasena=contrasena)
            
            if usuario.activo:
                # Guardar sesión personalizada
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_nombre'] = usuario.nombre
                request.session.set_expiry(3600)  # Sesión válida por 1 hora

                messages.success(request, f'Bienvenido {usuario.nombre}')
                return redirect('products')  # Redirige a productos correctamente
            else:
                messages.error(request, 'Tu cuenta está inactiva.')

        except Usuario.DoesNotExist:
            messages.error(request, 'Correo o contraseña incorrectos.')

    # Si no hay POST o hubo error, recarga el login
    return render(request, 'accounts/login.html')


def products(request):
    # Verificar si el usuario inició sesión correctamente
    if not request.session.get('usuario_id'):
        messages.warning(request, 'Debes iniciar sesión para ver los productos.')
        return redirect('login')

    # Si está autenticado, mostrar productos
    vehiculos = Vehiculo.objects.all()
    return render(request, 'core/products.html', {'vehiculos': vehiculos})