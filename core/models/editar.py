def editar_usuario(request, id):
    if request.session.get('usuario_rol') != "admin":
        messages.error(request, "No tienes permisos para editar usuarios.")
        return redirect('home')

    usuario = get_object_or_404(Usuario, id_usuario=id)

    if request.method == "POST":
        usuario.nombre = request.POST.get("nombre")
        usuario.correo = request.POST.get("correo")
        usuario.telefono = request.POST.get("telefono")
        usuario.nombre_rol = request.POST.get("nombre_rol")
        usuario.activo = True if request.POST.get("activo") == "on" else False

        usuario.save()
        messages.success(request, "Usuario actualizado correctamente.")
        return redirect('perfil_usuario', id=id)

    return render(request, "core/editar_usuario.html", {"usuario": usuario})
