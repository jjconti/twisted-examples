from django.db import models
from datetime import datetime
from django.db.models.signals import pre_save

class Persona(models.Model):
    rfid = models.CharField(max_length=100)
    nombre = models.CharField(max_length=200)
    legajo = models.CharField(max_length=10)
    empleado_de_telecom = models.BooleanField()
    vencimiento_de_acceso = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        return self.nombre


class Sala(models.Model):
    ccc = models.CharField(max_length=3)
    numero_de_sala = models.IntegerField()
    nombre = models.CharField(max_length=30)
    
    def __unicode__(self):
        return u"%s - %s - %s" % (self.ccc, self.numero_de_sala, self.nombre)
    
    def estado(self):
        try:
            estado = self.registroacceso_set.latest().estado()
        except RegistroAcceso.DoesNotExist:
            estado = None
        return estado
          
        
class RegistroAcceso(models.Model):
    sala = models.ForeignKey(Sala)
    timestamp = models.DateTimeField(auto_now_add=True)  
    rfid = models.CharField(max_length=100, blank=True)
    puerta_abierta = models.BooleanField()
    movimiento = models.BooleanField()
    tiempoDesdeNormalAnterior = models.IntegerField(blank=True, null=True)  # en minutos
    
    def __unicode__(self):
        return u"%s | %s | %d %d | %s" % (self.sala, self.rfid, self.puerta_abierta, self.movimiento, self.estado().esAlerta())
        
    def estado(self):
        return Estado(self, self.rfid, self.puerta_abierta, self.movimiento)

    def masAntiguoQue(self, minutos):
        now = datetime.now()
        delta = now - self.timestamp
        totalMinutos = delta.seconds / 60 + delta.days * 24 * 60
        return totalMinutos > int(minutos)

    class Meta:
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'
        
NORMAL = 'ffffff'
ALERTANARANJA = 'ffd200'
ALERTAROJA = 'ff0000'
ALERTAVERDE = '00ff00'
ALERTAAMARILLO = 'ffff00'

class Estado(object):

    def __init__(self, registro, rfid, puerta_abierta, movimiento):
        self.registro = registro
        self.rfid = rfid
        self.puerta_abierta = puerta_abierta
        self.movimiento = movimiento
        self.color = self.setTipoYObtenerColor()
        print self.color, 'acoloooor'
    
    def esAlerta(self):
        print "es alerta?", self.tipo
        return self.tipo.startswith('alerta')

    def setTipoYObtenerColor(self):
        if self.rfid == '' and not self.puerta_abierta and not self.movimiento:
            self.tipo = 'normal'
            return NORMAL
        elif self.rfid == '' and self.puerta_abierta and not self.movimiento:
            self.tipo = 'alerta_naranja'
            return ALERTANARANJA
        elif self.rfid == '' and not self.puerta_abierta and self.movimiento:
            self.tipo = 'alerta_roja'
            return ALERTAROJA
        elif self.rfid == '' and self.puerta_abierta and self.movimiento:
            self.tipo = 'alerta_roja'
            return ALERTAROJA
        elif self.rfid and not self.puerta_abierta and not self.movimiento:
            self.tipo = 'alerta_verde'
            return ALERTAVERDE
        elif self.rfid and self.puerta_abierta and not self.movimiento:
            self.tipo = 'alerta_naranja'
            return ALERTANARANJA
        elif self.rfid and not self.puerta_abierta and self.movimiento:
            self.tipo = 'normal'
            return NORMAL
        elif self.rfid and self.puerta_abierta and self.movimiento:
            self.tipo = 'normal'
            return NORMAL

def pre_save_Registro(sender, instance, **kw):
    estadoAnterior = instance.sala.estado()
    print estadoAnterior
    if estadoAnterior is None or not estadoAnterior.esAlerta():
        instance.tiempoDesdeNormalAnterior = 0
    else:
        t = estadoAnterior.registro.tiempoDesdeNormalAnterior
        now = datetime.now()
        delta = now - estadoAnterior.registro.timestamp
        instance.tiempoDesdeNormalAnterior = delta.seconds / 60 + delta.days * 24 * 60 + t
        print "valor seteado en instancia", instance.tiempoDesdeNormalAnterior
        

pre_save.connect(pre_save_Registro, sender=RegistroAcceso, dispatch_uid="salas.models")

