from django.db import models

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
    
    def __unicode__(self):
        return u"%s | %s | %d %d" % (self.sala, self.rfid, self.puerta_abierta, self.movimiento)
        
    def estado(self):
        return Estado(self, self.rfid, self.puerta_abierta, self.movimiento)
       
    def masAntiguoQue(minutos):
        now = datetime.now()
        return (now - self.timestamp).seconds / 60 > minutos

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
        self.color = self.get_color()
        print self.color, 'acoloooor'
    
    def get_color(self):
        if self.rfid == '' and not self.puerta_abierta and not self.movimiento:
            return NORMAL
        elif self.rfid == '' and not self.puerta_abierta and self.movimiento:
            return ALERTANARANJA
        elif self.rfid == '' and self.puerta_abierta and not self.movimiento:
            return ALERTAROJA
        elif self.rfid == '' and self.puerta_abierta and self.movimiento:
            return ALERTAROJA
        elif self.rfid and not self.puerta_abierta and not self.movimiento:
            return ALERTAVERDE
        elif self.rfid and not self.puerta_abierta and self.movimiento:
            return NORMAL
        elif self.rfid and self.puerta_abierta and not self.movimiento:
            return NORMAL
        elif self.rfid and self.puerta_abierta and self.movimiento:
            return NORMAL
