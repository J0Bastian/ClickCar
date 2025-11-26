from django.db import models
from .usuarios import Usuario
from .vehiculo import Vehiculo


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column="id_usuario"
    )

    auto = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        db_column="id_auto"
    )

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    ESTADOS = (
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="pendiente"
    )

    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_reserva = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reservas"

    def __str__(self):
        return f"Reserva {self.id_reserva} - {self.usuario.nombre}"
