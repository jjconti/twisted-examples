from twisted.protocols.basic import LineOnlyReceiver
from twisted.application import internet, service
from twisted.internet.protocol import Factory
from twisted.internet import reactor

from twisted.enterprise import adbapi

from constants import *
from twisted.python import log
from twisted.python.logfile import DailyLogFile
#log.startLogging(DailyLogFile('log.txt', LOGDIR))
from sys import stdout
log.startLogging(stdout)

from twisted.internet.task import LoopingCall


class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        self.process(line)
        
    def connectionMade(self):
        #self.factory.clients.append(self)
        self.factory.clients[id(self)] = {'self': self, 'sitio': ''}
        self.peer = self.transport.getPeer()
        print "Nuevo cliente: %s:%d" % (self.peer.host, self.peer.port) #LOG
        print "Total: %d" % (len(self.factory.clients),)
    
    def connectionLost(self, reason):
        if id(self) in self.factory.clients:
            del self.factory.clients[id(self)]
        else:
            print "El cliente ya fue eliminado."
        #TODO: do something with reason
        
    def process(self, line):    #FIXME: esta funcion debe detectar errores
        #print "-%s-" % (line,)
        #return
        #print "R: %s:%d %s" % (self.peer.host, self.peer.port, line)  #LOG
        if not line.startswith(':'):
            print "Error en mensaje: no empieza con :"  #EXC
        elif line[3] == '9':   # mensaje del G24 - Saludo inicial
            print "G24 dice: ", line
            sitio = line[5:8]
            print "SITIO", sitio
            # verificar si ya hay un g24 registrado para ese sitio
            for k,v in self.factory.clients.items():
                if sitio == v['sitio']:
                    print "%s ya estaba conectado. Borrando anterior." % sitio
                    self.factory.clients[k]['self'].transport.loseConnection()
                    del self.factory.clients[k] #move(sitios[sitio])
                    break
            self.factory.clients[id(self)]['sitio'] = sitio
            #sitios[sitio] = self    #ver como liberamos el recurso aca
        elif line[3] == '6':
            print "G24 dice: ", line
            sitio = line[5:8]
            print "SITIO", sitio
        else:
            disp = int(line[1:3])   #EXC
            func = int(line[3:5])   #EXC
            body = line[5:]
            #print "D: %01d F: %s B: %s" % (disp, func, body)

            if func not in VALID_FUNCS:
                print "Error: funcion desconida."
            else:
                if func == ID:
                    self.process_id(body)
                elif func == RD:
                    self.process_read(body)
                elif func == WR:
                    self.process_write_reg(body)

    def process_id(self, body):
        print body
        
    def process_read(self, body):
        ea1 = body[:4]
        ea2 = body[4:8]
        ea3 = body[8:12]
        ea4 = body[12:16]
        c1 = body[16:20]
        c2 = body[20:24]
        c3 = body[24:28]
        c4 = body[28:32]
        b1 = body[32:33]
        b2 = body[33:34]
        b3 = body[34:35]
        b4 = body[35:36]                                    
        i1 = body[36:37]
        i2 = body[37:38]
        print ea1, ea2, ea3, ea4, c1, c2, c3, c4, b1, b2, b3, b4, i1, i2
        print "Guardando en bd"
        dbpool.runQuery('''INSERT INTO valores (sitio, dispositivo, a1, a2, a3, a4,
                           c1, c2, c3, c4, b1, b2, b3, b4, i1, i2) VALUES (%s, %s,
                           %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                          (2, 1, ea1, ea2, ea3, ea4, c1, c2, c3, c4, b1, b2, b3, b4, i1, i2))

        sitio = factory.clients[id(self)]['sitio']
        
        if lectores.get(sitio):
            print len(lectores[sitio]), "lectores"
            for l in lectores[sitio].values():
                l.callRemote('actualizarValores', u','.join([ea1, ea2, ea3, ea4, c1, c2,
                                                             c3, c4, b1, b2, b3, b4, i1, i2]))
        if graficos.get(sitio):
            print len(graficos[sitio]), "graficos"
            for g in graficos[sitio].values():
                g.callRemote("nuevoValor", u",".join([ea1, ea2, ea3, ea4, c1, c2,
                                                      c3, c4, b1, b2, b3, b4]))
            
    def process_write_reg(self, body):
        reg = body[2:]
        err = body[2:4]
        if err == NOERR:
            pass
        elif err == ERRREG:
            print "Error en el registro %s" % (reg,)
        elif err == ERRVAL:
            print "Error en el valor %s" % (val,)
                        
    def ask_id(self, disp):
        self.sendLine(':%02d%d%02d' % (disp, ID, LR))
    
    def ask_read(self, disp):
        self.sendLine(':%02d%d%02d' % (disp, RD, LR))

    def ask_write_reg(self, disp, reg, val):
        line = ':%02d%d%02d%02d%02d' % (disp, WR, reg, val, LR)
        print "Enviando: %s" % line
        self.sendLine(line)
            
class TModBusFactory(Factory):
    protocol = TModBus
    
    def paso(self):
        print "Clientes actualmente conectados: ", len(self.clients)
        for c in self.clients.values():
            c['self'].ask_read(1)

    def stopFactory(self):
        self.lc.stop()    
       
    def __init__(self):
        #self.clients = []
        self.clients = {}
        self.lc = LoopingCall(self.paso)
        #self.lc.start(60)
        self.lc.start(5)        

factory = TModBusFactory()
reactor.listenTCP(8007, factory)

from twisted.conch import manhole, manhole_ssh
from twisted.cred import portal, checkers 

#TODO: hacer keys propias
def getManholeFactory(namespace, **passwords):
    realm = manhole_ssh.TerminalRealm()
    def getManhole(_): return manhole.Manhole(namespace) 
    realm.chainedProtocolFactory.protocolFactory = getManhole
    p = portal.Portal(realm)
    p.registerChecker(
    checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords))
    f = manhole_ssh.ConchFactory(p)
    return f

reactor.listenTCP(8888, getManholeFactory(globals(), admin='aaa'))

# WEB
from twisted.web import server, resource

class Demo(resource.Resource):
    isLeaf = 1

    def __init__(self, links) :
        resource.Resource.__init__(self)
        self.links = links
        self.factory = factory

    def render_GET(self, request):
        cliente = request.args['cliente']
        disp = request.args['disp']
        func = request.args['func'].pop()
        if func == 'id':
            self.factory.clients[int(cliente[0])].ask_id(int(disp[0]))
        elif func == 'read':
            self.factory.clients[int(cliente[0])].ask_read(int(disp[0]))
        elif func == 'write':
            reg = request.args['reg']
            val = request.args['val']
            self.factory.clients[int(cliente[0])].ask_write_reg(int(disp[0]), int(reg[0]), int(val[0]))
        return "Paquete enviado! " + func
        
site = server.Site(Demo([])) 
reactor.listenTCP(8008, site)

# Nevow / Athena

from twisted.python.util import sibpath
from nevow import flat, rend, athena, loaders, tags as T
from nevow import inevow
from nevow.athena import LivePage, LiveElement, expose
from nevow.loaders import xmlfile

lectores = {}

class TempElement(LiveElement):
        
    docFactory = xmlfile(sibpath(__file__, 'ter.html'))
    jsClass = u'TempDisplay.TempWidget'

    def __init__(self, sitio=''):
        self.sitio = sitio
        self.client = [c for c in factory.clients.values() if c['sitio'] == sitio][0]['self']
        super(TempElement, self).__init__()

    def read(self):
        print "Se apreto el boton read"
        # TODO: verificar que sea un sitio valido
        if lectores.get(self.sitio):
            if id(self) in lectores[self.sitio].keys():
                del lectores[self.sitio][id(self)]
            else:
                lectores[self.sitio][id(self)] = self
        else:
            lectores[self.sitio] = {id(self): self}
    read = expose(read)

    def change(self, consigna, val):
        print "Se apreto el bonton change"
        if consigna not in ['1', '2', '3', '4'] or len(val) > 2:   # una validacion
            return
        try:
            consigna = int(consigna)
            val = int(val)
        except:
            return
        self.client.ask_write_reg(1, consigna, val)
    change = expose(change)

    
class TerPage(LivePage):
    docFactory = loaders.stan(T.html[
        T.head(render=T.directive('liveglue')),
        T.body(render=T.directive('myElement'))])

    def __init__(self, sitio='', *args, **kwargs):
        self.sitio = sitio
        LivePage.__init__ (self, *args, **kwargs)
        
    def beforeRender(self, ctx):
        d = self.notifyOnDisconnect()
        d.addErrback(self.disconn)

    def disconn(self, reason):
        if lectores.get(self.sitio):
            if id(self.element) in lectores[self.sitio].keys():
                del lectores[id(self.element)]

    def render_myElement(self, ctx, data):
        self.element = TempElement(self.sitio)
        self.element.setFragmentParent(self)
        return ctx.tag[self.element]

    def childFactory(self, ctx, name):
        return TerPage(name)

graficos = {}

class GraphElement(LiveElement):

    docFactory = xmlfile(sibpath(__file__, 'graph.html'))
    jsClass = u'GraphDisplay.GraphWidget'

    def __init__(self, sitio=''):
        self.sitio = sitio
        super(GraphElement, self).__init__()
        
    def start(self):
        print "Se apreto el bonton start"
        # TODO: verificar que sea un sitio valido
        if graficos.get(self.sitio):
            if id(self) in graficos[self.sitio].keys():
                del graficos[self.sitio][id(self)]
            else:
                graficos[self.sitio][id(self)] = self
        else:
            graficos[self.sitio] = {id(self): self}
    start = expose(start)
    
class GraphPage(LivePage):
    docFactory = loaders.stan(T.html[
        T.head(render=T.directive('liveglue')),
        T.body(render=T.directive('myElement'))])
    
    def __init__(self, sitio='', *args, **kwargs):
        self.sitio = sitio
        LivePage.__init__ (self, *args, **kwargs)
        
    def beforeRender(self, ctx):
        d = self.notifyOnDisconnect()
        d.addErrback(self.disconn)

    def disconn(self, reason):
        if graficos.get(self.sitio):
            if id(self.element) in graficos[self.sitio].keys():
                del graficos[id(self.element)]

    def render_myElement(self, ctx, data):
        request = inevow.IRequest(ctx)
        print request.prepath
        self.element = GraphElement(self.sitio)
        self.element.setFragmentParent(self)
        return ctx.tag[self.element]

    def childFactory(self, ctx, name):
        return GraphPage(name)

class TodoPage(LivePage):
    docFactory = loaders.stan(T.html[
        T.head(render=T.directive('liveglue')),
        T.body[T.div(render=T.directive('myElement1')),
               T.div(render=T.directive('myElement2'))]])

    def __init__(self, sitio='', *args, **kwargs):
        self.sitio = sitio
        LivePage.__init__ (self, *args, **kwargs)
        
    def beforeRender(self, ctx):
        d = self.notifyOnDisconnect()
        d.addErrback(self.disconn)

    def disconn(self, reason):
        
        if lectores.get(self.sitio):
            if id(self.element1) in lectores[self.sitio].keys():
                del lectores[id(self.element1)]
            
        if graficos.get(self.sitio):
            if id(self.element2) in graficos[self.sitio].keys():
                del graficos[id(self.element2)]

    def render_myElement1(self, ctx, data):
        self.element1 = TempElement(self.sitio)
        self.element1.setFragmentParent(self)
        return ctx.tag[self.element1]
        
    def render_myElement2(self, ctx, data):
        self.element2 = GraphElement(self.sitio)
        self.element2.setFragmentParent(self)
        return ctx.tag[self.element2]

    def childFactory(self, ctx, name):
        return TodoPage(name)

class EjPage(rend.Page):

    def renderHTTP(self, ctx):
        s = render_to_string('my_template.html', { 'foo': 'bar' })
        return s.encode('utf-8')
        
class IndexPage(rend.Page):

    def __init__ ( self, *args, **kwargs ):
        rend.Page.__init__ ( self, *args, **kwargs )

    def renderHTTP(self, ctx):
        return render_to_string('sitios.html', {'clientes': factory.clients.values()}).encode('utf-8')
            
    def child_ter(self, ctx):
        return TerPage()

    def child_graph(self, ctx):
        return GraphPage()

    def child_todo(self, ctx):
        return TodoPage()

class SitioPage(rend.Page):

    def __init__ (self, *args, **kwargs):
        rend.Page.__init__ ( self, *args, **kwargs )
        
        
from nevow import appserver
site = appserver.NevowSite(IndexPage())
reactor.listenTCP(8009, site)
reactor.listenTCP(8080, site)

# DB Pool
dbpool = adbapi.ConnectionPool('MySQLdb', host='10.0.0.10', port=3306, db='kimera_kimera', user='kimera', passwd='kimera')

# DB Django
import sys
sys.path = sys.path + ['/home/juanjo/python/twisted/teco/dproj']
from dproj.piel.models import Robot
print len(Robot.objects.filter(nombre__startswith='juanjo'))

# Django Templates
from django.template.loader import render_to_string
#from django.template import Template, Context
rendered = render_to_string('my_template.html', { 'foo': 'bar' })
print rendered

reactor.run()
