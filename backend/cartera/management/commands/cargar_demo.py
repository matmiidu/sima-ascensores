"""Carga una cartera ficticia del tamaño del caso: 6 técnicos, 62 edificios
(48 residenciales y 14 de otros usos) y 140 ascensores.

Los datos son inventados y siempre salen iguales (semilla fija), para que las
pruebas y las capturas se puedan repetir. Deja además los usuarios de prueba:
"jefe" para el jefe técnico y uno por técnico (su nombre de pila), todos con la
misma clave. Uso:

    python manage.py cargar_demo            # solo si la base está vacía
    python manage.py cargar_demo --borrar   # borra la cartera y la vuelve a cargar
"""
import random
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from cartera.models import Ascensor, Edificio, Tecnico
from cartera.usuarios import crear_usuarios_tecnicos
from planificacion.models import GeneracionCalendario
from terreno.models import RegistroMantencion

CLAVE_DEMO = "sima"

TECNICOS = [
    "Juan Pérez", "Rodrigo Soto", "Camila Rojas", "Luis Muñoz", "Andrés Díaz", "Felipe Contreras",
]
# Cada técnico atiende una zona; así el calendario agrupa traslados cortos.
ZONAS = [
    ["Providencia"], ["Ñuñoa"], ["Las Condes"], ["Santiago"], ["San Miguel", "La Cisterna"], ["La Florida", "Macul"],
]
CALLES = [
    "Av. Providencia", "Los Leones", "Pedro de Valdivia", "Irarrázaval", "Av. Grecia", "Av. Apoquindo",
    "Manquehue Sur", "San Diego", "Santa Rosa", "Gran Avenida", "Vicuña Mackenna", "Av. Macul",
    "Lira", "Eliodoro Yáñez", "José Pedro Alessandri", "Tobalaba", "Alcántara", "Carmen", "Exequiel Fernández",
]
NOMBRES = [
    "Edificio Mirador", "Torre Alameda", "Condominio Los Robles", "Edificio Plaza", "Torre Andes", "Edificio Parque",
    "Condominio Vista Sur", "Edificio Centenario", "Torre Oriente", "Edificio Los Aromos", "Edificio Portal",
    "Condominio El Bosque", "Edificio Nogales", "Torre Pacífico", "Edificio Las Palmas", "Edificio Bellavista",
]
MARCAS = ["Otis", "Schindler", "Thyssenkrupp", "Kone", "Mitsubishi", "Orona"]
ADMINISTRADORES = [
    "María González", "Patricia Fuentes", "Claudio Herrera", "Verónica Silva", "Jorge Morales", "Daniela Castro",
    "Sergio Reyes", "Paula Vargas", "Héctor Núñez", "Carolina Araya",
]
OTROS_USOS = ["oficinas"] * 8 + ["comercial"] * 3 + ["salud"] * 2 + ["educacion"]


def repartir_ascensores(rng, total_edificios, total_ascensores):
    """Entre 1 y 6 ascensores por edificio, sumando exactamente el total."""
    cuenta = [1] * total_edificios
    while sum(cuenta) < total_ascensores:
        i = rng.randrange(total_edificios)
        if cuenta[i] < 6:
            cuenta[i] += 1
    return cuenta


class Command(BaseCommand):
    help = "Carga la cartera ficticia del caso (62 edificios, 140 ascensores, 6 técnicos)."

    def add_arguments(self, parser):
        parser.add_argument("--borrar", action="store_true", help="Borra la cartera existente antes de cargar.")

    @transaction.atomic
    def handle(self, *args, borrar=False, **opts):
        User = get_user_model()
        if Edificio.objects.exists() and not borrar:
            self.stdout.write("La cartera ya tiene datos; use --borrar para recargarla.")
            creados = crear_usuarios_tecnicos(CLAVE_DEMO)
            if creados:
                self.stdout.write(f"Se crearon los usuarios de los técnicos que faltaban: {', '.join(creados)} "
                                  f"(clave {CLAVE_DEMO}).")
            return
        if borrar:
            # Primero las mantenciones registradas, que protegen a su visita; al
            # borrar los ascensores se van también sus visitas del calendario.
            RegistroMantencion.objects.all().delete()
            Ascensor.objects.all().delete()
            Edificio.objects.all().delete()
            GeneracionCalendario.objects.all().delete()
            User.objects.filter(tecnico__isnull=False).delete()
            Tecnico.objects.all().delete()

        rng = random.Random(2026)
        tecnicos = [
            Tecnico.objects.create(nombre=n, telefono=f"+56 9 {rng.randint(5000, 9999)} {rng.randint(1000, 9999)}")
            for n in TECNICOS
        ]
        usos = ["residencial"] * 48 + OTROS_USOS
        rng.shuffle(usos)
        cuenta = repartir_ascensores(rng, 62, 140)
        hoy = date(2026, 10, 19)
        usados = set()
        for i, uso in enumerate(usos):
            z = i % len(ZONAS)
            comuna = rng.choice(ZONAS[z])
            while True:
                direccion = f"{rng.choice(CALLES)} {rng.randint(100, 3999)}"
                if (direccion, comuna) not in usados:
                    usados.add((direccion, comuna))
                    break
            admin = rng.choice(ADMINISTRADORES)
            edificio = Edificio.objects.create(
                nombre=f"{NOMBRES[i % len(NOMBRES)]} {i // len(NOMBRES) + 1}" if i >= len(NOMBRES) else NOMBRES[i],
                direccion=direccion,
                comuna=comuna,
                tipo_uso=uso,
                administrador_nombre=admin,
                administrador_correo=admin.lower().replace(" ", ".").translate(str.maketrans("áéíóúñ", "aeioun")) + "@ejemplo.cl",
                administrador_telefono=f"+56 2 {rng.randint(2200, 2999)} {rng.randint(1000, 9999)}",
                tecnico_asignado=tecnicos[z],
            )
            # Residencial: certificación cada dos años; otros usos: cada año.
            vigencia = 730 if uso == "residencial" else 365
            for n in range(cuenta[i]):
                instalacion = date(rng.randint(1995, 2024), rng.randint(1, 12), rng.randint(1, 28))
                Ascensor.objects.create(
                    edificio=edificio,
                    identificador=f"A{n + 1}",
                    tipo="hidraulico" if rng.random() < 0.15 else "electrico",
                    uso="carga" if (uso != "residencial" and n == cuenta[i] - 1 and cuenta[i] > 2) else "pasajeros",
                    marca=rng.choice(MARCAS),
                    numero_serie=f"{rng.choice('ABCDEFKMOST')}{rng.randint(100000, 999999)}",
                    paradas=rng.randint(3, 22),
                    capacidad_kg=rng.choice([450, 630, 800, 1000, 1275]),
                    fecha_instalacion=instalacion,
                    vencimiento_certificacion=hoy + timedelta(days=rng.randint(-20, vigencia)),
                )

        if not User.objects.filter(username="jefe").exists():
            jefe = User.objects.create_superuser("jefe", "jefe@ejemplo.cl", CLAVE_DEMO)
            jefe.first_name, jefe.last_name = "Jefe", "Técnico"
            jefe.save()
        crear_usuarios_tecnicos(CLAVE_DEMO)
        usuarios = ", ".join(Tecnico.objects.exclude(usuario=None).values_list("usuario__username", flat=True))

        self.stdout.write(self.style.SUCCESS(
            f"Cargados {Tecnico.objects.count()} técnicos, {Edificio.objects.count()} edificios "
            f"y {Ascensor.objects.count()} ascensores. Usuarios de prueba (clave {CLAVE_DEMO}): jefe para el jefe "
            f"técnico; {usuarios} para los técnicos."
        ))
