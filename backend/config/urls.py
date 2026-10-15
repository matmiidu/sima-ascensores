from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter

from cartera.views import AscensorViewSet, EdificioViewSet, TecnicoViewSet
from planificacion.views import FeriadoViewSet, VisitaViewSet, generar, resumen
from terreno.views import ChecklistPruebaViewSet

router = DefaultRouter()
router.register("tecnicos", TecnicoViewSet, basename="tecnico")
router.register("edificios", EdificioViewSet, basename="edificio")
router.register("ascensores", AscensorViewSet, basename="ascensor")
router.register("visitas", VisitaViewSet, basename="visita")
router.register("feriados", FeriadoViewSet, basename="feriado")
router.register("poc/checklists", ChecklistPruebaViewSet, basename="checklist-prueba")


@api_view(["GET"])
def yo(request):
    u = request.user
    return Response({"usuario": u.username, "nombre": u.get_full_name() or u.username})


admin.site.site_header = "SIMA · Ascensores Altavía"
admin.site.site_title = "SIMA"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", obtain_auth_token),
    path("api/yo/", yo),
    path("api/calendario/generar/", generar),
    path("api/calendario/resumen/", resumen),
    path("api/", include(router.urls)),
]
