# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Magnitud(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=120, blank=True)
    minimo = models.DecimalField(null=True, max_digits=13, decimal_places=1, blank=True)
    maximo = models.DecimalField(null=True, max_digits=13, decimal_places=1, blank=True)
    unidad = models.CharField(max_length=60, blank=True)
    uni = models.CharField(max_length=15, blank=True)
    class Meta:
        db_table = u'magnitudes'

    def __unicode__(self):
        return u"%s en %s" % (self.nombre, self.uni)
        
class Medida(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    texto = models.CharField(max_length=240, blank=True)

    class Meta:
        db_table = u'medidas'

    def __unicode__(self):
        return self.texto
        
class Provincia(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    zona_id = models.IntegerField(null=True, blank=True)
    nombre = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'provincias'


class Sitio(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=120, blank=True)
    ccc = models.CharField(max_length=9, blank=True)
    port = models.IntegerField(unique=True)
    class Meta:
        db_table = u'sitios'

    def __unicode__(self):
        return self.ccc

class RobotTipoIO(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=60, blank=True)
    campo = models.CharField(max_length=10, blank=True) # campo de la tabla Valores
    
    class Meta:
        db_table = u'robots_tipoio'

    def esEA(self):
        return self.nombre.startswith('Entrada Analogica')
        
    def esRE(self):
        return self.nombre.startswith('Registro')

    def esSD(self):
        return self.nombre.startswith('Salida Digital')

    def esED(self):
        return self.nombre.startswith('Entrada Digital')
        
    def __unicode__(self):
        return self.nombre
        
class RobotTipo(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=120, blank=True)
    mascara = models.CharField(max_length=500, blank=True)
        
    class Meta:
        db_table = u'robots_tipos'
        
    def __unicode__(self):
        return self.nombre
                
class Robot(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    tipo = models.ForeignKey(RobotTipo, null=True, db_column='tipo', blank=True)
    nombre = models.CharField(max_length=120)
    mbdir = models.CharField(max_length=6, blank=True)
    observaciones = models.TextField(blank=True)
    sitio = models.ForeignKey(Sitio, null=True, db_column='sitio', blank=True)
    last_valor = models.ForeignKey('Valor', null=True, blank=True, db_column='last_valor', related_name='Valor.robot')
    
    class Meta:
        db_table = u'robots'

    def __unicode__(self):
        return u"%s en %s" % (self.mbdir, self.sitio)

    def config_dict(self, gcond=None):

        configuracion = self.robotconfig_set.all()
        if gcond is not None:
            configuracion = configuracion.filter(graficable=gcond)
        entradasanalogicas = [c for c in configuracion if c.tipoio.esEA()]
        registros = [c for c in configuracion if c.tipoio.esRE()]
        salidasdigitales = [c for c in configuracion if c.tipoio.esSD()]
        entradasdigitales = [c for c in configuracion if c.tipoio.esED()]
        return {'entradasanalogicas': entradasanalogicas,
                'registros': registros,
                'salidasdigitales': salidasdigitales,
                'entradasdigitales': entradasdigitales
               }

    def confignames_dict(self, gcond=None):
    
        configuracion = self.robotconfig_set.all()
        if gcond is not None:
            configuracion = configuracion.filter(graficable=gcond)
        entradasanalogicas = [c.tipoio.campo for c in configuracion if c.tipoio.esEA()]
        registros = [c.tipoio.campo for c in configuracion if c.tipoio.esRE()]
        salidasdigitales = [c.tipoio.campo for c in configuracion if c.tipoio.esSD()]
        entradasdigitales = [c.tipoio.campo for c in configuracion if c.tipoio.esED()]
        return {u'entradasanalogicas': entradasanalogicas,
                u'registros': registros,
                u'salidasdigitales': salidasdigitales,
                u'entradasdigitales': entradasdigitales
               }
               
class RobotConfig(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    robot = models.ForeignKey(Robot, db_column='robot')
    tipoio = models.ForeignKey(RobotTipoIO, null=True, db_column='tipoio', blank=True)   
    magnitud = models.ForeignKey(Magnitud, null=True, db_column='magnitud', blank=True)
    medida = models.ForeignKey(Medida, null=True, db_column='medida', blank=True)
    editable = models.BooleanField()
    graficable = models.BooleanField() 
    
    class Meta:
        db_table = u'robots_config'

class Valor(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    robot = models.ForeignKey(Robot, null=True, db_column='robot', blank=True)
    ea1 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    ea2 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    ea3 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    ea4 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    ea5 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    ea6 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    ea7 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    ea8 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    ea9 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    ea10 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    re1 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    re2 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    re3 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    re4 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    re5 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    re6 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    re7 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    re8 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    re9 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    re10 = models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)
    sd1 = models.IntegerField(null=True, blank=True)
    sd2 = models.IntegerField(null=True, blank=True)
    sd3 = models.IntegerField(null=True, blank=True)
    sd4 = models.IntegerField(null=True, blank=True)
    sd5 = models.IntegerField(null=True, blank=True)
    sd6 = models.IntegerField(null=True, blank=True)
    sd7 = models.IntegerField(null=True, blank=True)
    sd8 = models.IntegerField(null=True, blank=True)
    sd9 = models.IntegerField(null=True, blank=True)
    sd10 = models.IntegerField(null=True, blank=True)
    ed1 = models.IntegerField(null=True, blank=True)
    ed2 = models.IntegerField(null=True, blank=True)
    ed3 = models.IntegerField(null=True, blank=True)
    ed4 = models.IntegerField(null=True, blank=True)
    ed5 = models.IntegerField(null=True, blank=True)
    ed6 = models.IntegerField(null=True, blank=True)
    ed7 = models.IntegerField(null=True, blank=True)
    ed8 = models.IntegerField(null=True, blank=True)
    ed9 = models.IntegerField(null=True, blank=True)
    ed10 = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(null=True)
    class Meta:
        db_table = u'valores'
        ordering = ('id',)

EVENTO_CHOICES = (
    ('I', 'Informacion'),
    ('W', 'Advertencia'),
    ('A', 'Alerta'),
)

class Evento(models.Model):
    timestamp = models.DateTimeField(null=True, auto_now=True)
    tipo = models.CharField(max_length=1, choices=EVENTO_CHOICES)
    texto = models.CharField(max_length=60, blank=True)
    
    def __unicode__(self):
        return "%s: %s - %s" % (self.timestamp, self.tipo, self.texto)

# Signals

from django.db.models.signals import post_save

def record_last_valor(sender, instance, created, **kwargs):
    print "LAST_VALOR"*5
    print instance, created
    if created:
        instance.robot.last_valor = instance
        instance.robot.save()
        print instance.robot.last_valor
        print instance == instance.robot.last_valor

post_save.connect(record_last_valor, sender=Valor)
