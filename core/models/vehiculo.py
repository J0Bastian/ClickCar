from django.db import models

class Vehiculo(models.Model):
    id_auto = models.AutoField(primary_key=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    categoria = models.CharField(max_length=50, null=True, blank=True)
    anio = models.IntegerField(null=True, blank=True)
    precio_dia = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)
    descripcion = models.TextField(null=True, blank=True)

    # CAMPO CORRECTO PARA SUBIR FOTOS
    foto = models.ImageField(upload_to='vehiculos/', null=True, blank=True)

    combustible = models.CharField(max_length=50, null=True, blank=True)
    asientos = models.IntegerField(default=4)
    color = models.CharField(max_length=50)

    class Meta:
        db_table = "automoviles"

    def __str__(self):
        return f"{self.marca} {self.modelo}"
