from django.urls import path
from .views import (
    home, products, exit, reserva, login_usuario,
    visualizar_perfiles, perfil_usuario,
    editar_usuario, eliminar_usuario, confirmar_reserva, registro_usuario,verificar_codigo,olvide_password,
    verificar_codigo_reset, nueva_contrasena,descargar_pdf,
    descargar_pdf_usuario, panel_reservas, mis_reservas,admin_reservas, ver_detalle_reserva, lista_vehiculos,
    agregar_vehiculo, eliminar_vehiculo,
)

urlpatterns = [
    path('', home, name='home'),
    path('products/', products, name='products'),
    path('logout/', exit, name='exit'),
    path('reserva/<int:id>/', reserva, name='reserva'),
    path('login/', login_usuario, name='login'),
    path('perfiles/', visualizar_perfiles, name='visualizar_perfiles'),
    path('perfil/<int:id>/', perfil_usuario, name='perfil_usuario'),
    path('perfil/<int:id>/editar/', editar_usuario, name='editar_usuario'),
    path('perfil/<int:id>/eliminar/', eliminar_usuario, name='eliminar_usuario'),
    path('confirmar/', confirmar_reserva, name='confirmar_reserva'),
    path('registro/', registro_usuario, name='registro'),
    path('verificar/', verificar_codigo, name='verificar_codigo'),
    path('olvide/', olvide_password, name='olvide_password'),
    path('olvide/verificar/', verificar_codigo_reset, name='verificar_codigo_reset'),
    path('olvide/nueva/', nueva_contrasena, name='nueva_contrasena'),
    path("descargar_pdf/", descargar_pdf_usuario, name="descargar_pdf"),
    path('admin-reservas/', panel_reservas, name='panel_reservas'),
    path("mis-reservas/", mis_reservas, name="mis_reservas"),
    path('admin/reservas/', admin_reservas, name='admin_reservas'),
    path("reserva/<int:id_reserva>/detalle/", ver_detalle_reserva, name="detalle_reserva"),
    path('reserva/<int:id_reserva>/pdf/', descargar_pdf, name='pdf_reserva'),
    # Vehículos
    path('vehiculos/', lista_vehiculos, name='lista_vehiculos'),
    path('vehiculos/agregar/', agregar_vehiculo, name='agregar_vehiculo'),
    path('vehiculos/eliminar/<int:id_vehiculo>/', eliminar_vehiculo, name='eliminar_vehiculo'),




]
