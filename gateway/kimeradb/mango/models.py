# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Compoundeventdetectors(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300, blank=True)
    alarmlevel = models.IntegerField(db_column='alarmLevel') # Field name made lowercase.
    returntonormal = models.CharField(max_length=3, db_column='returnToNormal') # Field name made lowercase.
    disabled = models.CharField(max_length=3)
    conditiontext = models.CharField(max_length=768, db_column='conditionText') # Field name made lowercase.
    xid = models.CharField(unique=True, max_length=150)
    class Meta:
        db_table = u'compoundEventDetectors'

class Datapointusers(models.Model):
    datapointid = models.ForeignKey('Datapoints', db_column='dataPointId') # Field name made lowercase.
    userid = models.ForeignKey('Users', db_column='userId') # Field name made lowercase.
    permission = models.IntegerField()
    class Meta:
        db_table = u'dataPointUsers'

class DatapointusersGp(models.Model):
    datapointid = models.IntegerField(db_column='dataPointId') # Field name made lowercase.
    userid = models.IntegerField(db_column='userId') # Field name made lowercase.
    permission = models.IntegerField()
    class Meta:
        db_table = u'dataPointUsers_gp'

class Datapoints(models.Model):
    id = models.IntegerField(primary_key=True)
    xid = models.CharField(unique=True, max_length=150)
    datasourceid = models.ForeignKey('Datasources', db_column='dataSourceId') # Field name made lowercase.
    data = models.TextField()
    class Meta:
        db_table = u'dataPoints'

class DatapointsGp(models.Model):
    id = models.IntegerField(primary_key=True)
    xid = models.CharField(unique=True, max_length=150)
    datasourceid = models.IntegerField(db_column='dataSourceId') # Field name made lowercase.
    data = models.TextField()
    class Meta:
        db_table = u'dataPoints_gp'

class Datasourceusers(models.Model):
    datasourceid = models.ForeignKey('Datasources', db_column='dataSourceId') # Field name made lowercase.
    userid = models.ForeignKey('Users', db_column='userId') # Field name made lowercase.
    class Meta:
        db_table = u'dataSourceUsers'

class DatasourceusersGp(models.Model):
    datasourceid = models.IntegerField(db_column='dataSourceId') # Field name made lowercase.
    userid = models.IntegerField(db_column='userId') # Field name made lowercase.
    class Meta:
        db_table = u'dataSourceUsers_gp'

class Datasources(models.Model):
    id = models.IntegerField(primary_key=True)
    xid = models.CharField(unique=True, max_length=150)
    name = models.CharField(max_length=120)
    datasourcetype = models.IntegerField(db_column='dataSourceType') # Field name made lowercase.
    data = models.TextField()
    class Meta:
        db_table = u'dataSources'

class DatasourcesGp(models.Model):
    id = models.IntegerField(primary_key=True)
    xid = models.CharField(unique=True, max_length=150)
    name = models.CharField(max_length=120)
    datasourcetype = models.IntegerField(db_column='dataSourceType') # Field name made lowercase.
    data = models.TextField()
    class Meta:
        db_table = u'dataSources_gp'

class Eventhandlers(models.Model):
    id = models.IntegerField(primary_key=True)
    alias = models.CharField(max_length=765, blank=True)
    eventtypeid = models.IntegerField(db_column='eventTypeId') # Field name made lowercase.
    eventtyperef1 = models.IntegerField(db_column='eventTypeRef1') # Field name made lowercase.
    eventtyperef2 = models.IntegerField(db_column='eventTypeRef2') # Field name made lowercase.
    data = models.TextField()
    xid = models.CharField(unique=True, max_length=150)
    class Meta:
        db_table = u'eventHandlers'

class EventhandlersGp(models.Model):
    id = models.IntegerField(primary_key=True)
    alias = models.CharField(max_length=765, blank=True)
    eventtypeid = models.IntegerField(db_column='eventTypeId') # Field name made lowercase.
    eventtyperef1 = models.IntegerField(db_column='eventTypeRef1') # Field name made lowercase.
    eventtyperef2 = models.IntegerField(db_column='eventTypeRef2') # Field name made lowercase.
    data = models.TextField()
    class Meta:
        db_table = u'eventHandlers_gp'

class Events(models.Model):
    id = models.IntegerField(primary_key=True)
    typeid = models.IntegerField(db_column='typeId') # Field name made lowercase.
    typeref1 = models.IntegerField(db_column='typeRef1') # Field name made lowercase.
    typeref2 = models.IntegerField(db_column='typeRef2') # Field name made lowercase.
    activets = models.BigIntegerField(db_column='activeTs') # Field name made lowercase.
    rtnapplicable = models.CharField(max_length=3, db_column='rtnApplicable') # Field name made lowercase.
    rtnts = models.BigIntegerField(null=True, db_column='rtnTs', blank=True) # Field name made lowercase.
    rtncause = models.IntegerField(null=True, db_column='rtnCause', blank=True) # Field name made lowercase.
    alarmlevel = models.IntegerField(db_column='alarmLevel') # Field name made lowercase.
    message = models.TextField(blank=True)
    ackts = models.BigIntegerField(null=True, db_column='ackTs', blank=True) # Field name made lowercase.
    ackuserid = models.ForeignKey('Users', null=True, db_column='ackUserId', blank=True) # Field name made lowercase.
    enviadoinicio = models.IntegerField(null=True, db_column='enviadoInicio', blank=True) # Field name made lowercase.
    enviadocierre = models.IntegerField(null=True, db_column='enviadoCierre', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'events'

class EventsBak(models.Model):
    id = models.IntegerField(primary_key=True)
    typeid = models.IntegerField(db_column='typeId') # Field name made lowercase.
    typeref1 = models.IntegerField(db_column='typeRef1') # Field name made lowercase.
    typeref2 = models.IntegerField(db_column='typeRef2') # Field name made lowercase.
    activets = models.BigIntegerField(db_column='activeTs') # Field name made lowercase.
    rtnapplicable = models.CharField(max_length=3, db_column='rtnApplicable') # Field name made lowercase.
    rtnts = models.BigIntegerField(null=True, db_column='rtnTs', blank=True) # Field name made lowercase.
    rtncause = models.IntegerField(null=True, db_column='rtnCause', blank=True) # Field name made lowercase.
    alarmlevel = models.IntegerField(db_column='alarmLevel') # Field name made lowercase.
    message = models.TextField(blank=True)
    ackts = models.BigIntegerField(null=True, db_column='ackTs', blank=True) # Field name made lowercase.
    ackuserid = models.ForeignKey('Users', null=True, db_column='ackUserId', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'events_bak'

class EventsGp(models.Model):
    id = models.IntegerField(primary_key=True)
    typeid = models.IntegerField(db_column='typeId') # Field name made lowercase.
    typeref1 = models.IntegerField(db_column='typeRef1') # Field name made lowercase.
    typeref2 = models.IntegerField(db_column='typeRef2') # Field name made lowercase.
    activets = models.BigIntegerField(db_column='activeTs') # Field name made lowercase.
    rtnapplicable = models.CharField(max_length=3, db_column='rtnApplicable') # Field name made lowercase.
    rtnts = models.BigIntegerField(null=True, db_column='rtnTs', blank=True) # Field name made lowercase.
    rtncause = models.IntegerField(null=True, db_column='rtnCause', blank=True) # Field name made lowercase.
    alarmlevel = models.IntegerField(db_column='alarmLevel') # Field name made lowercase.
    message = models.TextField(blank=True)
    ackts = models.BigIntegerField(null=True, db_column='ackTs', blank=True) # Field name made lowercase.
    ackuserid = models.IntegerField(null=True, db_column='ackUserId', blank=True) # Field name made lowercase.
    enviadoinicio = models.IntegerField(null=True, db_column='enviadoInicio', blank=True) # Field name made lowercase.
    enviadocierre = models.IntegerField(null=True, db_column='enviadoCierre', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'events_gp'

class Mailinglistinactive(models.Model):
    mailinglistid = models.ForeignKey('Mailinglists', db_column='mailingListId') # Field name made lowercase.
    inactiveinterval = models.IntegerField(db_column='inactiveInterval') # Field name made lowercase.
    class Meta:
        db_table = u'mailingListInactive'

class Mailinglistmembers(models.Model):
    mailinglistid = models.ForeignKey('Mailinglists', db_column='mailingListId') # Field name made lowercase.
    typeid = models.IntegerField(db_column='typeId') # Field name made lowercase.
    userid = models.IntegerField(null=True, db_column='userId', blank=True) # Field name made lowercase.
    address = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'mailingListMembers'

class Mailinglists(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=120)
    xid = models.CharField(unique=True, max_length=150)
    class Meta:
        db_table = u'mailingLists'

class Mangoviewusers(models.Model):
    mangoviewid = models.ForeignKey('Mangoviews', db_column='mangoViewId') # Field name made lowercase.
    userid = models.ForeignKey('Users', db_column='userId') # Field name made lowercase.
    accesstype = models.IntegerField(db_column='accessType') # Field name made lowercase.
    class Meta:
        db_table = u'mangoViewUsers'

class Mangoviews(models.Model):
    id = models.IntegerField(primary_key=True)
    xid = models.CharField(unique=True, max_length=150)
    name = models.CharField(max_length=300)
    background = models.CharField(max_length=765, blank=True)
    userid = models.ForeignKey('Users', db_column='userId') # Field name made lowercase.
    anonymousaccess = models.IntegerField(db_column='anonymousAccess') # Field name made lowercase.
    data = models.TextField()
    class Meta:
        db_table = u'mangoViews'

class Mensajes(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    tema_id = models.IntegerField(null=True, blank=True)
    asunto = models.CharField(max_length=300, blank=True)
    mensaje = models.TextField(blank=True)
    autor = models.CharField(max_length=300, blank=True)
    imagen = models.CharField(max_length=600)
    fecha = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'mensajes'

class PContactos(models.Model):
    contacto_id = models.IntegerField(unique=True)
    user_id = models.IntegerField(null=True, blank=True)
    contacto_nombre = models.CharField(max_length=150, blank=True)
    contacto_apellido = models.CharField(max_length=60, blank=True)
    contacto_celular = models.CharField(max_length=60, blank=True)
    contacto_mail = models.CharField(max_length=150, blank=True)
    contacto_fechacreacion = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'p_contactos'

class PContactosGrupos(models.Model):
    id = models.IntegerField(primary_key=True)
    contacto_id = models.IntegerField(null=True, blank=True)
    idgrupo = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'p_contactos_grupos'

class PEstudios(models.Model):
    idestudio = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'p_estudios'

class PGrupos(models.Model):
    idgrupo = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=300, blank=True)
    descripcion = models.CharField(max_length=450, blank=True)
    contrasena = models.CharField(max_length=300, blank=True)
    contrasenadesencriptada = models.CharField(max_length=150, blank=True)
    admin = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'p_grupos'

class PLogs(models.Model):
    id = models.IntegerField(primary_key=True)
    fecha = models.DateTimeField(null=True, blank=True)
    iduser = models.IntegerField(null=True, blank=True)
    user = models.CharField(max_length=150, blank=True)
    evento = models.CharField(max_length=750, blank=True)
    descripcion = models.CharField(max_length=750, blank=True)
    class Meta:
        db_table = u'p_logs'

class PMensajes(models.Model):
    id = models.IntegerField(primary_key=True)
    idorigen = models.IntegerField(null=True, blank=True)
    iddestino = models.IntegerField(null=True, blank=True)
    leidoorigen = models.IntegerField(null=True, blank=True)
    leidodestino = models.IntegerField(null=True, blank=True)
    asunto = models.CharField(max_length=300, blank=True)
    mensaje = models.TextField(blank=True)
    eliminadoorigen = models.IntegerField(null=True, blank=True)
    eliminadodestino = models.IntegerField(null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'p_mensajes'

class PMensajessms(models.Model):
    mensajesms_id = models.IntegerField(unique=True)
    mensajesms_grupoid = models.IntegerField(null=True, blank=True)
    mensajesms_texto = models.CharField(max_length=600, blank=True)
    mensajesms_fechacreacion = models.DateTimeField(null=True, blank=True)
    evento_id = models.IntegerField(null=True, blank=True)
    mensajesms_estado = models.IntegerField(null=True, blank=True)
    mensajesms_level = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'p_mensajessms'

class PMensajessmsEnviar(models.Model):
    mensajesenviar_id = models.IntegerField(unique=True)
    evento_id = models.IntegerField(null=True, blank=True)
    mensajesms_id = models.IntegerField(null=True, blank=True)
    contacto_id = models.IntegerField(null=True, blank=True)
    mensajesenviar_estado = models.IntegerField(null=True, blank=True)
    mensajesenviar_fechacreacion = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'p_mensajessms_enviar'

class POcupaciones(models.Model):
    idocupacion = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'p_ocupaciones'

class PPaises(models.Model):
    idpais = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=150)
    class Meta:
        db_table = u'p_paises'

class PProvincias(models.Model):
    idprovincia = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'p_provincias'

class PUsers(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=60)
    nombre = models.CharField(max_length=96, blank=True)
    apellido = models.CharField(max_length=150, blank=True)
    password = models.CharField(max_length=96)
    passwordwap = models.IntegerField(null=True, blank=True)
    email = models.CharField(max_length=384)
    admin = models.CharField(max_length=3)
    edit = models.CharField(max_length=3)
    restrictdate = models.DateField(null=True, blank=True)
    style = models.CharField(max_length=120)
    logueado = models.IntegerField(null=True, blank=True)
    activo = models.IntegerField(null=True, blank=True)
    claveactivacion = models.CharField(max_length=60, blank=True)
    idnacionalidad = models.IntegerField(null=True, blank=True)
    idpais = models.IntegerField(null=True, blank=True)
    idprovincia = models.IntegerField(null=True, blank=True)
    idlocalidad = models.IntegerField(null=True, blank=True)
    idocupacion = models.IntegerField(null=True, blank=True)
    idcargo = models.IntegerField(null=True, blank=True)
    idestudio = models.IntegerField(null=True, blank=True)
    pregunta = models.CharField(max_length=300, blank=True)
    documentotipo = models.CharField(max_length=30, blank=True)
    documentonumero = models.IntegerField(null=True, blank=True)
    sexo = models.CharField(max_length=3, blank=True)
    nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=150, blank=True)
    celular = models.CharField(max_length=150, blank=True)
    accesos = models.IntegerField()
    ultimoacceso = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'p_users'

class PUsersGrupos(models.Model):
    id = models.IntegerField(primary_key=True)
    idusers = models.IntegerField(null=True, blank=True)
    idgrupo = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'p_users_grupos'

class PUsuarios(models.Model):
    idusuario = models.IntegerField(unique=True, db_column='IdUsuario') # Field name made lowercase.
    nombre = models.CharField(max_length=600, db_column='Nombre', blank=True) # Field name made lowercase.
    apellido = models.CharField(max_length=600, db_column='Apellido', blank=True) # Field name made lowercase.
    dni = models.CharField(max_length=60, blank=True)
    class Meta:
        db_table = u'p_usuarios'

class Pointeventdetectors(models.Model):
    id = models.IntegerField(primary_key=True)
    xid = models.CharField(unique=True, max_length=150)
    alias = models.CharField(max_length=765, blank=True)
    datapointid = models.ForeignKey(Datapoints, db_column='dataPointId') # Field name made lowercase.
    detectortype = models.IntegerField(db_column='detectorType') # Field name made lowercase.
    alarmlevel = models.IntegerField(db_column='alarmLevel') # Field name made lowercase.
    statelimit = models.FloatField(null=True, db_column='stateLimit', blank=True) # Field name made lowercase.
    duration = models.IntegerField(null=True, blank=True)
    durationtype = models.IntegerField(null=True, db_column='durationType', blank=True) # Field name made lowercase.
    binarystate = models.CharField(max_length=3, db_column='binaryState', blank=True) # Field name made lowercase.
    multistatestate = models.IntegerField(null=True, db_column='multistateState', blank=True) # Field name made lowercase.
    changecount = models.IntegerField(null=True, db_column='changeCount', blank=True) # Field name made lowercase.
    alphanumericstate = models.CharField(max_length=384, db_column='alphanumericState', blank=True) # Field name made lowercase.
    weight = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'pointEventDetectors'

class Pointhierarchy(models.Model):
    id = models.IntegerField(primary_key=True)
    parentid = models.IntegerField(null=True, db_column='parentId', blank=True) # Field name made lowercase.
    name = models.CharField(max_length=300, blank=True)
    class Meta:
        db_table = u'pointHierarchy'

class PointhierarchyGp(models.Model):
    id = models.IntegerField(primary_key=True)
    parentid = models.IntegerField(null=True, db_column='parentId', blank=True) # Field name made lowercase.
    name = models.CharField(max_length=300, blank=True)
    class Meta:
        db_table = u'pointHierarchy_gp'

class Pointlinks(models.Model):
    id = models.IntegerField(primary_key=True)
    xid = models.CharField(unique=True, max_length=150)
    sourcepointid = models.IntegerField(db_column='sourcePointId') # Field name made lowercase.
    targetpointid = models.IntegerField(db_column='targetPointId') # Field name made lowercase.
    script = models.TextField(blank=True)
    eventtype = models.IntegerField(db_column='eventType') # Field name made lowercase.
    disabled = models.CharField(max_length=3)
    class Meta:
        db_table = u'pointLinks'

class Pointvalueannotations(models.Model):
    pointvalueid = models.ForeignKey('Pointvalues', db_column='pointValueId') # Field name made lowercase.
    textpointvalueshort = models.CharField(max_length=384, db_column='textPointValueShort', blank=True) # Field name made lowercase.
    textpointvaluelong = models.TextField(db_column='textPointValueLong', blank=True) # Field name made lowercase.
    sourcetype = models.IntegerField(null=True, db_column='sourceType', blank=True) # Field name made lowercase.
    sourceid = models.IntegerField(null=True, db_column='sourceId', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'pointValueAnnotations'

class Pointvalues(models.Model):
    id = models.BigIntegerField(primary_key=True)
    datapointid = models.ForeignKey(Datapoints, db_column='dataPointId') # Field name made lowercase.
    datatype = models.IntegerField(db_column='dataType') # Field name made lowercase.
    pointvalue = models.FloatField(null=True, db_column='pointValue', blank=True) # Field name made lowercase.
    ts = models.BigIntegerField()
    class Meta:
        db_table = u'pointValues'

class Provincias(models.Model):
    provincia_id = models.IntegerField(unique=True)
    pais_id = models.IntegerField(null=True, blank=True)
    zona_id = models.IntegerField(null=True, blank=True)
    provincia_nombre = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'provincias'

class Publishers(models.Model):
    id = models.IntegerField(primary_key=True)
    data = models.TextField()
    xid = models.CharField(unique=True, max_length=150)
    class Meta:
        db_table = u'publishers'

class Reportinstancedata(models.Model):
    pointvalueid = models.BigIntegerField(primary_key=True, db_column='pointValueId') # Field name made lowercase.
    reportinstancepointid = models.ForeignKey('Reportinstancepoints', db_column='reportInstancePointId') # Field name made lowercase.
    pointvalue = models.FloatField(null=True, db_column='pointValue', blank=True) # Field name made lowercase.
    ts = models.BigIntegerField()
    class Meta:
        db_table = u'reportInstanceData'

class Reportinstancedataannotations(models.Model):
    pointvalueid = models.ForeignKey('Reportinstancedata', related_name='values',  db_column='pointValueId') # Field name made lowercase.
    reportinstancepointid = models.ForeignKey('Reportinstancedata', db_column='reportInstancePointId') # Field name made lowercase.
    textpointvalueshort = models.CharField(max_length=384, db_column='textPointValueShort', blank=True) # Field name made lowercase.
    textpointvaluelong = models.TextField(db_column='textPointValueLong', blank=True) # Field name made lowercase.
    sourcevalue = models.CharField(max_length=384, db_column='sourceValue', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'reportInstanceDataAnnotations'

class Reportinstanceevents(models.Model):
    eventid = models.IntegerField(primary_key=True, db_column='eventId') # Field name made lowercase.
    reportinstanceid = models.ForeignKey('Reportinstances', db_column='reportInstanceId') # Field name made lowercase.
    typeid = models.IntegerField(db_column='typeId') # Field name made lowercase.
    typeref1 = models.IntegerField(db_column='typeRef1') # Field name made lowercase.
    typeref2 = models.IntegerField(db_column='typeRef2') # Field name made lowercase.
    activets = models.BigIntegerField(db_column='activeTs') # Field name made lowercase.
    rtnapplicable = models.CharField(max_length=3, db_column='rtnApplicable') # Field name made lowercase.
    rtnts = models.BigIntegerField(null=True, db_column='rtnTs', blank=True) # Field name made lowercase.
    rtncause = models.IntegerField(null=True, db_column='rtnCause', blank=True) # Field name made lowercase.
    alarmlevel = models.IntegerField(db_column='alarmLevel') # Field name made lowercase.
    message = models.TextField(blank=True)
    ackts = models.BigIntegerField(null=True, db_column='ackTs', blank=True) # Field name made lowercase.
    ackusername = models.CharField(max_length=120, db_column='ackUsername', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'reportInstanceEvents'

class Reportinstancepoints(models.Model):
    id = models.IntegerField(primary_key=True)
    reportinstanceid = models.ForeignKey('Reportinstances', db_column='reportInstanceId') # Field name made lowercase.
    pointname = models.CharField(max_length=300, db_column='pointName') # Field name made lowercase.
    datatype = models.IntegerField(db_column='dataType') # Field name made lowercase.
    startvalue = models.CharField(max_length=12288, db_column='startValue', blank=True) # Field name made lowercase.
    textrenderer = models.TextField(db_column='textRenderer', blank=True) # Field name made lowercase.
    datasourcename = models.CharField(max_length=120, db_column='dataSourceName') # Field name made lowercase.
    colour = models.CharField(max_length=18, blank=True)
    class Meta:
        db_table = u'reportInstancePoints'

class Reportinstanceusercomments(models.Model):
    reportinstanceid = models.ForeignKey('Reportinstances', db_column='reportInstanceId') # Field name made lowercase.
    username = models.CharField(max_length=120)
    commenttype = models.IntegerField(db_column='commentType') # Field name made lowercase.
    typekey = models.IntegerField(db_column='typeKey') # Field name made lowercase.
    ts = models.BigIntegerField()
    commenttext = models.CharField(max_length=3072, db_column='commentText') # Field name made lowercase.
    class Meta:
        db_table = u'reportInstanceUserComments'

class Reportinstances(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.ForeignKey('Users', db_column='userId') # Field name made lowercase.
    name = models.CharField(max_length=300)
    includeevents = models.IntegerField(db_column='includeEvents') # Field name made lowercase.
    includeusercomments = models.CharField(max_length=3, db_column='includeUserComments') # Field name made lowercase.
    reportstarttime = models.BigIntegerField(db_column='reportStartTime') # Field name made lowercase.
    reportendtime = models.BigIntegerField(db_column='reportEndTime') # Field name made lowercase.
    runstarttime = models.BigIntegerField(null=True, db_column='runStartTime', blank=True) # Field name made lowercase.
    runendtime = models.BigIntegerField(null=True, db_column='runEndTime', blank=True) # Field name made lowercase.
    recordcount = models.IntegerField(null=True, db_column='recordCount', blank=True) # Field name made lowercase.
    preventpurge = models.CharField(max_length=3, db_column='preventPurge', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'reportInstances'

class Reports(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.ForeignKey('Users', db_column='userId') # Field name made lowercase.
    name = models.CharField(max_length=300)
    data = models.TextField()
    class Meta:
        db_table = u'reports'

class Scheduledevents(models.Model):
    id = models.IntegerField(primary_key=True)
    alias = models.CharField(max_length=765, blank=True)
    alarmlevel = models.IntegerField(db_column='alarmLevel') # Field name made lowercase.
    scheduletype = models.IntegerField(db_column='scheduleType') # Field name made lowercase.
    returntonormal = models.CharField(max_length=3, db_column='returnToNormal') # Field name made lowercase.
    disabled = models.CharField(max_length=3)
    activeyear = models.IntegerField(null=True, db_column='activeYear', blank=True) # Field name made lowercase.
    activemonth = models.IntegerField(null=True, db_column='activeMonth', blank=True) # Field name made lowercase.
    activeday = models.IntegerField(null=True, db_column='activeDay', blank=True) # Field name made lowercase.
    activehour = models.IntegerField(null=True, db_column='activeHour', blank=True) # Field name made lowercase.
    activeminute = models.IntegerField(null=True, db_column='activeMinute', blank=True) # Field name made lowercase.
    activesecond = models.IntegerField(null=True, db_column='activeSecond', blank=True) # Field name made lowercase.
    activecron = models.CharField(max_length=75, db_column='activeCron', blank=True) # Field name made lowercase.
    inactiveyear = models.IntegerField(null=True, db_column='inactiveYear', blank=True) # Field name made lowercase.
    inactivemonth = models.IntegerField(null=True, db_column='inactiveMonth', blank=True) # Field name made lowercase.
    inactiveday = models.IntegerField(null=True, db_column='inactiveDay', blank=True) # Field name made lowercase.
    inactivehour = models.IntegerField(null=True, db_column='inactiveHour', blank=True) # Field name made lowercase.
    inactiveminute = models.IntegerField(null=True, db_column='inactiveMinute', blank=True) # Field name made lowercase.
    inactivesecond = models.IntegerField(null=True, db_column='inactiveSecond', blank=True) # Field name made lowercase.
    inactivecron = models.CharField(max_length=75, db_column='inactiveCron', blank=True) # Field name made lowercase.
    xid = models.CharField(unique=True, max_length=150)
    class Meta:
        db_table = u'scheduledEvents'

class Systemsettings(models.Model):
    settingname = models.CharField(max_length=96, primary_key=True, db_column='settingName') # Field name made lowercase.
    settingvalue = models.TextField(db_column='settingValue', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'systemSettings'

class Temas(models.Model):
    tema_id = models.IntegerField(unique=True)
    tema_aquien = models.IntegerField(null=True, blank=True)
    tema_nombre = models.CharField(max_length=120, blank=True)
    class Meta:
        db_table = u'temas'

class Usercomments(models.Model):
    userid = models.ForeignKey('Users', db_column='userId') # Field name made lowercase.
    commenttype = models.IntegerField(db_column='commentType') # Field name made lowercase.
    typekey = models.IntegerField(db_column='typeKey') # Field name made lowercase.
    ts = models.BigIntegerField()
    commenttext = models.CharField(max_length=3072, db_column='commentText') # Field name made lowercase.
    class Meta:
        db_table = u'userComments'

class Userevents(models.Model):
    eventid = models.ForeignKey(Events, db_column='eventId') # Field name made lowercase.
    userid = models.ForeignKey('Users', db_column='userId') # Field name made lowercase.
    silenced = models.CharField(max_length=3)
    class Meta:
        db_table = u'userEvents'

class Userevents(models.Model):
    eventid = models.IntegerField(primary_key=True, db_column='eventId') # Field name made lowercase.
    userid = models.IntegerField(db_column='userId') # Field name made lowercase.
    silenced = models.CharField(max_length=3)
    class Meta:
        db_table = u'userevents'

class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=120)
    password = models.CharField(max_length=90)
    email = models.CharField(max_length=765)
    phone = models.CharField(max_length=120, blank=True)
    admin = models.CharField(max_length=3)
    disabled = models.CharField(max_length=3)
    lastlogin = models.BigIntegerField(null=True, db_column='lastLogin', blank=True) # Field name made lowercase.
    selectedwatchlist = models.IntegerField(null=True, db_column='selectedWatchList', blank=True) # Field name made lowercase.
    homeurl = models.CharField(max_length=765, db_column='homeUrl', blank=True) # Field name made lowercase.
    receivealarmemails = models.IntegerField(db_column='receiveAlarmEmails') # Field name made lowercase.
    receiveownauditevents = models.CharField(max_length=3, db_column='receiveOwnAuditEvents') # Field name made lowercase.
    class Meta:
        db_table = u'users'

class UsersGp(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=120)
    password = models.CharField(max_length=90)
    email = models.CharField(max_length=765)
    phone = models.CharField(max_length=120, blank=True)
    admin = models.CharField(max_length=3)
    disabled = models.CharField(max_length=3)
    lastlogin = models.BigIntegerField(null=True, db_column='lastLogin', blank=True) # Field name made lowercase.
    selectedwatchlist = models.IntegerField(null=True, db_column='selectedWatchList', blank=True) # Field name made lowercase.
    homeurl = models.CharField(max_length=765, db_column='homeUrl', blank=True) # Field name made lowercase.
    receivealarmemails = models.IntegerField(db_column='receiveAlarmEmails') # Field name made lowercase.
    receiveownauditevents = models.CharField(max_length=3, db_column='receiveOwnAuditEvents') # Field name made lowercase.
    class Meta:
        db_table = u'users_gp'

class Watchlistpoints(models.Model):
    watchlistid = models.ForeignKey('Watchlists', db_column='watchListId') # Field name made lowercase.
    datapointid = models.ForeignKey(Datapoints, db_column='dataPointId') # Field name made lowercase.
    sortorder = models.IntegerField(db_column='sortOrder') # Field name made lowercase.
    class Meta:
        db_table = u'watchListPoints'

class Watchlistusers(models.Model):
    watchlistid = models.ForeignKey('Watchlists', db_column='watchListId') # Field name made lowercase.
    userid = models.ForeignKey(Users, db_column='userId') # Field name made lowercase.
    accesstype = models.IntegerField(db_column='accessType') # Field name made lowercase.
    class Meta:
        db_table = u'watchListUsers'

class Watchlists(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.ForeignKey(Users, db_column='userId') # Field name made lowercase.
    name = models.CharField(max_length=150, blank=True)
    class Meta:
        db_table = u'watchLists'

