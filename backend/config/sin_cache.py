"""Las respuestas de la API no se guardan en la caché del navegador (H07).

La prueba de la jornada sin señal mostró que, sin este encabezado, Firefox sin conexión entregaba respuestas
viejas de /api/ sacadas de su caché como si vinieran del servidor: el técnico veía la lista sin el aviso
"Sin señal". La copia para trabajar sin señal la maneja la aplicación (terreno.ts), que sí avisa de cuándo es.
"""


class SinCacheEnApi:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        respuesta = self.get_response(request)
        if request.path.startswith("/api/"):
            respuesta["Cache-Control"] = "no-store"
        return respuesta
