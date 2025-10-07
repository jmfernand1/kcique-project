from django.db import models

# Create your models here.
class Desembolso(models.Model):
    referencia = models.CharField(max_length=100, unique=True)
    obligacion = models.BigIntegerField()
    id_cliente = models.BigIntegerField()
    nit_beneficiario = models.BigIntegerField()
    aliado = models.CharField(max_length=255)
    tipo_cta_destino = models.CharField(max_length=50)
    cod_tipo_cuenta_destino = models.IntegerField()
    num_cta_destino = models.BigIntegerField()
    banco_destino = models.CharField(max_length=100)
    cod_banco_destino = models.IntegerField()
    valor_desembolso = models.FloatField()
    numero_tramos = models.IntegerField()
    plazo_tramo_1 = models.IntegerField()
    tipo_tasa_tramo_1 = models.CharField(max_length=10)
    tasa_tramo_1 = models.FloatField()
    amortizacion_tramo_1 = models.CharField(max_length=10)
    plazo_tramo_2 = models.IntegerField()
    tipo_tasa_tramo_2 = models.CharField(max_length=10)
    tasa_tramo_2 = models.FloatField()
    amortizacion_tramo_2 = models.CharField(max_length=10)
    dia_pago_cuota = models.IntegerField(null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Desembolso {self.referencia}"

class CargoFijo(models.Model):
    desembolso = models.ForeignKey(Desembolso, related_name='cargos_fijos', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=10)
    nombre_cargo_fijo = models.CharField(max_length=255)
    fecha_efectiva = models.DateField(null=True, blank=True)
    fecha_revision = models.DateField(null=True, blank=True)
    periodicidad = models.CharField(max_length=50, null=True, blank=True)
    valor = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre_cargo_fijo} ({self.codigo})"
    

class Garantia(models.Model):
    referencia = models.CharField(max_length=100, null=True, blank=True)
    obligacion = models.BigIntegerField()
    id_cliente = models.BigIntegerField()
    id_garante = models.BigIntegerField()
    cod_fasecolda = models.CharField(max_length=50)
    codigo_fasecolda = models.CharField(max_length=50)
    color = models.CharField(max_length=100, null=True, blank=True)
    placa = models.CharField(max_length=20)
    poliza_vehiculo = models.CharField(max_length=50, null=True, blank=True)
    cod_aseguradora = models.CharField(max_length=20, null=True, blank=True)
    nro_poliza = models.CharField(max_length=50, null=True, blank=True)
    valor_asegurado = models.FloatField(null=True, blank=True)
    fecha_vencimiento_seguro = models.DateField(null=True, blank=True)
    tipo_prima = models.CharField(max_length=50, null=True, blank=True)
    valor_prima = models.FloatField(null=True, blank=True)
    folio_electronico = models.CharField(max_length=50, null=True, blank=True)
    valor_vehiculo = models.BigIntegerField(null=True, blank=True)
    modelo = models.CharField(max_length=10, null=True, blank=True)
    fecha_prenda = models.DateField(null=True, blank=True)
    chasis = models.CharField(max_length=50, null=True, blank=True)
    motor = models.CharField(max_length=50, null=True, blank=True)
    serie = models.CharField(max_length=50, null=True, blank=True)
    servicio = models.CharField(max_length=50, null=True, blank=True)
    fecha_desembolso = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Garantía {self.placa} - Referencia {self.referencia}"