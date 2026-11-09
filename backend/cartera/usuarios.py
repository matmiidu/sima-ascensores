"""Usuarios de los técnicos (H04).

Cada técnico entra a SIMA con su propio usuario; así la aplicación sabe de
quién son las visitas que muestra. En la operación real el jefe técnico crea el
usuario en el panel y lo asocia al técnico. Esta función lo hace de una vez
para los técnicos que todavía no tienen, y la usa la carga de demostración.
"""
import unicodedata

from django.contrib.auth import get_user_model

from .models import Tecnico


def _sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def crear_usuarios_tecnicos(clave):
    """Crea un usuario para cada técnico activo que no tiene. Devuelve los nombres de usuario creados.

    El nombre de usuario es el nombre de pila en minúsculas y sin tildes
    ("Luis Muñoz" entra como "luis"); si ya está ocupado, nombre y apellido.
    """
    User = get_user_model()
    creados = []
    for tecnico in Tecnico.objects.filter(activo=True, usuario__isnull=True).order_by("id"):
        partes = _sin_tildes(tecnico.nombre).lower().split() or ["tecnico"]
        candidatos = [partes[0], ".".join(partes[:2]), f"{partes[0]}{tecnico.pk}"]
        libres = [c for c in candidatos if not User.objects.filter(username=c).exists()]
        if not libres:
            continue
        nombre, _, apellido = tecnico.nombre.partition(" ")
        tecnico.usuario = User.objects.create_user(libres[0], password=clave, first_name=nombre, last_name=apellido)
        tecnico.save(update_fields=["usuario"])
        creados.append(libres[0])
    return creados
