from django.db import models

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True, max_length=100)
    contrasena = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    nombre_rol = models.CharField(max_length=50)

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return f"{self.nombre} ({self.nombre_rol})"