"""Cartera de edificios y equipos (EP1, historia H01)."""
from datetime import date

from django.conf import settings
from django.db import models


class Tecnico(models.Model):
    """Técnico de mantención. Se le asignan edificios y visitas."""

    nombre = models.CharField(max_length=120)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    # Ascensores que puede atender en un día hábil; lo usa el calendario (H03).
    capacidad_diaria = models.PositiveSmallIntegerField(default=6)
    # Usuario con que el técnico entra desde el celular (H04). Con él SIMA sabe
    # de quién son las visitas que muestra. Vacío si todavía no tiene acceso.
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="tecnico",
        help_text="Usuario con que el técnico entra a SIMA desde el celular.",
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "técnico"

    def __str__(self):
        return self.nombre


class Edificio(models.Model):
    class TipoUso(models.TextChoices):
        RESIDENCIAL = "residencial", "Residencial"
        OFICINAS = "oficinas", "Oficinas"
        COMERCIAL = "comercial", "Comercial"
        SALUD = "salud", "Salud"
        EDUCACION = "educacion", "Educación"
        MIXTO = "mixto", "Mixto"

    nombre = models.CharField(max_length=150)
    direccion = models.CharField("dirección", max_length=200)
    comuna = models.CharField(max_length=80)
    tipo_uso = models.CharField("tipo de uso", max_length=20, choices=TipoUso.choices)
    administrador_nombre = models.CharField("administrador", max_length=120, blank=True)
    administrador_correo = models.EmailField("correo del administrador", blank=True)
    administrador_telefono = models.CharField("teléfono del administrador", max_length=30, blank=True)
    tecnico_asignado = models.ForeignKey(
        Tecnico, null=True, blank=True, on_delete=models.SET_NULL, related_name="edificios",
        verbose_name="técnico asignado",
    )
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["comuna", "nombre"]
        constraints = [
            models.UniqueConstraint(fields=["direccion", "comuna"], name="edificio_direccion_unica"),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.comuna})"


class Ascensor(models.Model):
    class Tipo(models.TextChoices):
        ELECTRICO = "electrico", "Eléctrico de tracción"
        HIDRAULICO = "hidraulico", "Hidráulico"

    class Uso(models.TextChoices):
        PASAJEROS = "pasajeros", "Pasajeros"
        CARGA = "carga", "Carga"
        MONTACAMAS = "montacamas", "Montacamas"
        MONTAVEHICULOS = "montavehiculos", "Montavehículos"

    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE, related_name="ascensores")
    identificador = models.CharField(
        max_length=30, help_text="Cómo lo reconocen en el edificio, por ejemplo «A1» o «Torre B poniente»."
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    uso = models.CharField(max_length=20, choices=Uso.choices, default=Uso.PASAJEROS)
    marca = models.CharField(max_length=60, blank=True)
    numero_serie = models.CharField("número de serie", max_length=60, blank=True)
    paradas = models.PositiveSmallIntegerField(default=2)
    capacidad_kg = models.PositiveIntegerField("capacidad (kg)", null=True, blank=True)
    fecha_instalacion = models.DateField("fecha de instalación", null=True, blank=True)
    vencimiento_certificacion = models.DateField(
        "vencimiento de la certificación", null=True, blank=True,
        help_text="Fecha en que vence la certificación vigente (Ley 20.296).",
    )
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["edificio", "identificador"]
        verbose_name_plural = "ascensores"
        constraints = [
            models.UniqueConstraint(fields=["edificio", "identificador"], name="ascensor_identificador_unico"),
        ]

    def __str__(self):
        return f"{self.edificio.nombre} · {self.identificador}"

    def certificacion_vencida(self, hoy=None):
        if self.vencimiento_certificacion is None:
            return None
        return self.vencimiento_certificacion < (hoy or date.today())
