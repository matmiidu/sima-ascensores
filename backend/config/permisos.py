"""Quién puede hacer qué en SIMA (H04).

Hay dos clases de usuario. El jefe técnico (y quien administre con él) mantiene
la cartera y el calendario: es un usuario marcado como personal en el panel.
Los técnicos entran desde el celular con su propio usuario, ven sus visitas y
registran la mantención; el resto solo lo pueden consultar.
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission


def es_jefe(usuario):
    return bool(usuario and usuario.is_authenticated and usuario.is_staff)


def tecnico_de(usuario):
    """El técnico asociado al usuario, o None si el usuario no es de un técnico."""
    if not usuario or not usuario.is_authenticated:
        return None
    return getattr(usuario, "tecnico", None)


class LecturaOJefe(BasePermission):
    """Cualquier usuario con sesión consulta; solo el jefe técnico modifica."""

    message = "Solo el jefe técnico puede hacer cambios en la cartera y en el calendario."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.method in SAFE_METHODS or es_jefe(request.user)
