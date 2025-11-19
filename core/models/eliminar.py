from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Usuario

def eliminar_usuario(request, id):
    if request.session.get('usuario_rol') != "admin":
        messages.error(request, "No tienes permisos para eliminar usuarios.")
        return redirect('home')

    usuario = get_object_or_404(Usuario, id_usuario=id)

    usuario.delete()
    messages.success(request, "Usuario eliminado correctamente.")
    return redirect('visualizar_perfiles')
