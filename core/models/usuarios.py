from django.db import models

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.CharField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, null=True, blank=True)

    # subir las imagenes
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    nombre_rol = models.CharField(max_length=20, default="cliente")

    class Meta:
        db_table = "usuarios"

    def __str__(self):
        return self.nombre
