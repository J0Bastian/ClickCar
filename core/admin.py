from django.contrib import admin
from .models.vehiculo import Vehiculo
from .models.reserva import Reserva
from .models.usuarios import Usuario

admin.site.register(Vehiculo)
admin.site.register(Usuario)
admin.site.register(Reserva)
