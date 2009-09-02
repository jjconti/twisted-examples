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


class Medida(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    texto = models.CharField(max_length=240, blank=True)
    class Meta:
        db_table = u'medidas'


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
    class Meta:
        db_table = u'sitios'


class RobotTipoIO(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=60, blank=True)
    class Meta:
        db_table = u'robots_tipoio'


class RobotTipo(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=120, blank=True)
    class Meta:
        db_table = u'robots_tipos'
        
        
class Robot(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    tipo = models.ForeignKey(RobotTipo, null=True, db_column='tipo', blank=True)
    nombre = models.CharField(max_length=120)
    mbdir = models.CharField(max_length=6, blank=True)
    observaciones = models.TextField(blank=True)
    sitio = models.ForeignKey(Sitio, null=True, db_column='sitio', blank=True)
    class Meta:
        db_table = u'robots'


class RobotConfig(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    robot = models.ForeignKey(Robot, db_column='robot')
    tipoio = models.ForeignKey(RobotTipoIO, null=True, db_column='tipoio', blank=True)
    magnitud = models.ForeignKey(Magnitud, null=True, db_column='magnitud', blank=True)
    medida = models.ForeignKey(Medida, null=True, db_column='medida', blank=True)
    class Meta:
        db_table = u'robots_config'

class Valor(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    robot = models.ForeignKey(Robot, null=True, db_column='robot', blank=True)
    ea1 = models.DecimalField(null=True, max_digits=13, decimal_places=3, blank=True)
    ea2 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ea3 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ea4 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ea5 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ea6 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ea7 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ea8 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ea9 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ea10 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    re1 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    re2 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    re3 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    re4 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    re5 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    re6 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    re7 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    re8 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    re9 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    re10 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    sd1 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    sd2 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    sd3 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    sd4 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    sd5 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    sd6 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    sd7 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    sd8 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    sd9 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    sd10 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ed1 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ed2 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ed3 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ed4 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ed5 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ed6 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ed7 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ed8 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ed9 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    ed10 = models.DecimalField(null=True, max_digits=12, decimal_places=0, blank=True)
    timestamp = models.DateTimeField(null=True)
    class Meta:
        db_table = u'valores'

