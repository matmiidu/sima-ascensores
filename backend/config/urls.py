from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from cartera.views import AscensorViewSet, EdificioViewSet, TecnicoViewSet, certificaciones
from planificacion.views import FeriadoViewSet, VisitaViewSet, generar, mis_visitas, resumen
from terreno.views import ChecklistPruebaViewSet, PuntoChecklistViewSet, RegistroMantencionViewSet, informe_pdf, informes

from .permisos import es_jefe, tecnico_de


class IngresoConToken(ObtainAuthToken):
    # El ingreso a la aplicación no mira la sesión del panel de administración:
    # si el navegador ya entró al panel, DRF exigía el código CSRF y el ingreso
    # fallaba con 403 aunque el usuario y la clave estuvieran bien.
    authentication_classes = []


router = DefaultRouter()
router.register("tecnicos", TecnicoViewSet, basename="tecnico")
router.register("edificios", EdificioViewSet, basename="edificio")
router.register("ascensores", AscensorViewSet, basename="ascensor")
router.register("visitas", VisitaViewSet, basename="visita")
router.register("feriados", FeriadoViewSet, basename="feriado")
router.register("poc/checklists", ChecklistPruebaViewSet, basename="checklist-prueba")
router.register("puntos-checklist", PuntoChecklistViewSet, basename="punto-checklist")
router.register("mantenciones", RegistroMantencionViewSet, basename="mantencion")


@api_view(["GET"])
def yo(request):
    """Quién entró: su nombre y si es el jefe técnico o un técnico."""
    u = request.user
    tecnico = tecnico_de(u)
    return Response({
        "usuario": u.username,
        "nombre": (tecnico.nombre if tecnico else u.get_full_name()) or u.username,
        "es_jefe": es_jefe(u),
        "tecnico": {"id": tecnico.id, "nombre": tecnico.nombre} if tecnico else None,
    })


admin.site.site_header = "SIMA · Ascensores Altavía"
admin.site.site_title = "SIMA"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", IngresoConToken.as_view()),
    path("api/yo/", yo),
    path("api/calendario/generar/", generar),
    path("api/calendario/resumen/", resumen),
    path("api/mis-visitas/", mis_visitas),
    path("api/certificaciones/", certificaciones),
    path("api/informes/", informes),
    path("api/informes/<int:edificio_id>/pdf/", informe_pdf),
    path("api/", include(router.urls)),
]
