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


# DB Django
import sys

sys.path = sys.path + ['/home/juanjo/python/twisted/teco/dproj']
#sys.path = sys.path + ['C:\Documents and Settings\Teco2006\Escritorio\line\dproj']
from dproj.piel.models import *
#print len(Robot.objects.filter(nombre__startswith='juanjo'))


class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        #try:
        self.process(line)
        #except Exception, e:
        #    print "Se recibio un valor erroneo en line.", e
        
    def connectionMade(self):
        #self.factory.clients.append(self)
        self.factory.clients[id(self)] = {'self': self, 'sitio': None}
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

        # Si se esta accediendo al cliente mediante una terminal
        # las lineas recibidas no son procesadas sino directamente
        # enviadas a la pantalla de la terminal correspondiente.
        if id(self) in terminales:
            terminales[id(self)].terminal.write('R: ' + line)
            terminales[id(self)].terminal.nextLine()
            terminales[id(self)].showPrompt()
            return
        
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
                if v['sitio'] and sitio == v['sitio'].ccc:
                    print "%s ya estaba conectado. Borrando anterior." % sitio
                    self.factory.clients[k]['self'].transport.loseConnection()
                    del self.factory.clients[k] #move(sitios[sitio])
                    break
            try:
                self.sitio = Sitio.objects.get(ccc=sitio)
                self.factory.clients[id(self)]['sitio'] = self.sitio    #dejar uno solo
            except Sitio.DoesNotExist:
                print "El sitio %s no existe en la base de datos." % sitio
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
                    self.process_id(disp, body)
                elif func == RD:
                    self.process_read(disp, body)
                elif func == WR:
                    self.process_write_reg(disp, body)

    def process_id(self, disp, body):
        print "Dispositivo %s: %s" % (disp, body)
        
    import re
    mascaras = {}
    for r in RobotTipo.objects.all():
        print r.mascara
        mascaras[r.id] = re.compile(str(r.mascara))
    def process_read(self, disp, body):
        
        robot = factory.clients[id(self)]['sitio'].robot_set.get(mbdir=disp)
        m = TModBus.mascaras[robot.tipo.id].match(body)
        if m:
            try:
                d = m.groupdict() 
                v = Valor(**d)
                v.save()
                print "Guradado en al BD", self.sitio, disp, d
            except Exception, e:
                print "Error al intentar guardar los datos en la BD.", e

            sitio = factory.clients[id(self)]['sitio'].ccc
            
            if lectores.get(sitio):
                print len(lectores[sitio]), "lectores"
                for l in lectores[sitio].values():
                    l.callRemote('actualizarValores', u','.join([v.ea1, v.ea2, v.ea3, v.ea4, v.c1, v.c2,
                                                                 v.c3, v.c4, v.b1, v.b2, v.b3, v.b4, v.i1, v.i2]))
            if graficos.get(sitio):
                print len(graficos[sitio]), "graficos"
                for g in graficos[sitio].values():
                    g.callRemote("nuevoValor", u",".join([v.ea1, v.ea2, v.ea3, v.ea4, v.c1, v.c2,
                                                      v.c3, v.c4, v.b1, v.b2, v.b3, v.b4]))

    def process_write_reg(self, disp, body):
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
        for k,c in self.clients.items():
            if k in terminales: # en terminales la clave es id(cliente)
                continue
            n = 1
            if c['sitio']:
                for r in c['sitio'].robot_set.all():
                    rmbdir = int(r.mbdir)
                    def f(r):
                        print "Se preguntara al robot ", r
                        c['self'].ask_read(r)
                    reactor.callLater(5*n,f, rmbdir)
                    n += 1
                
    def stopFactory(self):
        self.lc.stop()    
       
    def __init__(self):
        #self.clients = []
        self.clients = {}
        self.lc = LoopingCall(self.paso)
        #self.lc.start(60)
        self.lc.start(15)        

factory = TModBusFactory()
#reactor.listenTCP(8007, factory)
reactor.listenTCP(8017, factory)

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

reactor.listenTCP(8822, getManholeFactory(globals(), admin='aaa'))

# Terminal de comandos
terminales = {}

from twisted.cred import portal, checkers, credentials
from twisted.conch import error, avatar, recvline, interfaces as conchinterfaces
from twisted.conch.ssh import userauth, connection, keys, session, common
from twisted.conch.ssh import factory as sshfactory
from twisted.conch.insults import insults
from twisted.application import service, internet
from zope.interface import implements
import os
import twisted.python

class SecureCommandsProtocol(recvline.HistoricRecvLine):
    def __init__(self, user):
        self.user = user
        self.prompt = '> '
        self.mode = 0
        self.cliente = None
        self.sitio = None

    def connectionMade(self) :
        recvline.HistoricRecvLine.connectionMade(self)
        self.terminal.write("Bienvenido al sistema de control mediante comandos")
        self.terminal.nextLine()
        self.do_help()
        self.showPrompt()

    def connectionLost(self, reason):
        if self.mode == 1:
            del terminales[id(self.cliente)]
            
    def showPrompt(self):
        self.terminal.write(self.prompt)

    def getCommandFunc(self, cmd):
        return getattr(self, 'do_' + cmd, None)

    def lineReceived(self, line):
        line = line.strip()
        if line:
            cmdAndArgs = line.split()
            cmd = cmdAndArgs[0]
            args = cmdAndArgs[1:]
            func = self.getCommandFunc(cmd)
            if func:
                try:
                    func(*args)
                except Exception, e:
                    self.terminal.write("Error: %s" % e)
                    self.terminal.nextLine()
            elif line.startswith(':') and self.mode == 1:   # modo sitio ccc>
                self.cliente.sendLine(line)
            else:
                self.terminal.write("No existe el comando")
                self.terminal.nextLine()
        self.showPrompt()

    def do_help(self, cmd=''):
        "Ayuda de los comandos. Uso: help comando"
        if cmd:
            func = self.getCommandFunc(cmd)
            if func:
                self.terminal.write(func.__doc__)
                self.terminal.nextLine()
                return

        publicMethods = filter(
            lambda funcname: funcname.startswith('do_'), dir(self))
        commands = [cmd.replace('do_', '', 1) for cmd in publicMethods]
        self.terminal.write("Comandos: " + " ".join(commands))
        self.terminal.nextLine()

    def do_eco(self, *args):
        "Eco de una cadena de texto. Uso: eco cadena de texto"
        self.terminal.write(" ".join(args))
        self.terminal.nextLine()

    def do_whoami(self):
        "Prints your user name. Usage: whoami"
        self.terminal.write(self.user.username)
        self.terminal.nextLine()

    def do_quit(self):
        "Finaliza la sesion o sale del sitio. Uso: quit"
        if self.mode == 0:
            self.terminal.write("Hasta luego")
            self.terminal.nextLine()
            self.terminal.loseConnection()
        else:
            self.mode = 0
            self.prompt = "> "
            del terminales[id(self.cliente)]
            self.cliente = None
            self.sitio = None

    def do_clear(self):
        "Limpia la pantalla. Uso: clear"
        self.terminal.reset()

    def do_list(self):
        "Lista los sitios conectados. Uso: list"
        sitios = [c['sitio'].ccc for c in factory.clients.values()]
        self.terminal.write(" ".join(sitios).encode('ascii'))
        self.terminal.nextLine()
        
    def do_sitio(self, ccc):
        "Permite acceder a un sitio. Uso: sitio ccc"
        ccc = ccc.upper()[:3]
        try:
            self.sitio = Sitio.objects.get(ccc=ccc)
        except:
            self.terminal.write("El sitio %s no existe en la bd." % ccc)
            self.terminal.nextLine()
            return
        try:
            self.cliente = [c for c in factory.clients.values() if c['sitio'] == self.sitio][0]['self']
        except:
            self.terminal.write('No se puede enviar comandos. Sitio %s no conectado.' % ccc)
            self.terminal.nextLine()
            return
        self.prompt = "%s> " % ccc
        terminales[id(self.cliente)] = self
        self.mode = 1
        self.terminal.nextLine()
        

class SecureCommandsAvatar(avatar.ConchUser):
    implements(conchinterfaces.ISession)

    def __init__(self, username):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session':session.SSHSession})

    def openShell(self, protocol):
        serverProtocol = insults.ServerProtocol(SecureCommandsProtocol, self)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def execCommand(self, protocol, cmd):
        raise NotImplementedError

    def closed(self):
        pass

class SecureCommandsRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if conchinterfaces.IConchUser in interfaces:
            return interfaces[0], SecureCommandsAvatar(avatarId), lambda: None
        else:
            raise Exception, "No supported interfaces found."

def getRSAKeys():
    if not (os.path.exists('public.key') and os.path.exists('private.key')):
        # generate a RSA keypair
        print "Generating RSA keypair..."
        from Crypto.PublicKey import RSA
        KEY_LENGTH = 1024
        #rsaKey = RSA.generate(KEY_LENGTH, common.entropy.get_bytes)
        rsaKey = RSA.generate(KEY_LENGTH, twisted.python.randbytes.secureRandom)
        publicKeyString = keys.Key(rsaKey).toString('OPENSSH')
        privateKeyString = keys.makePrivateKeyString(rsaKey)
        # save keys for next time
        file('public.key', 'w+b').write(publicKeyString)
        file('private.key', 'w+b').write(privateKeyString)
        print "done."
    else:
        publicKeyString = file('public.key').read()
        privateKeyString = file('private.key').read()
    return publicKeyString, privateKeyString

sshFactory = sshfactory.SSHFactory()
sshFactory.portal = portal.Portal(SecureCommandsRealm())
users = {'admin': 'aaa', 'guest': 'bbb'}
sshFactory.portal.registerChecker(
                 checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))

pubKeyString, privKeyString = getRSAKeys()
sshFactory.publicKeys = {'ssh-rsa': keys.Key.fromString(pubKeyString)}
sshFactory.privateKeys = {'ssh-rsa': keys.Key.fromString(privKeyString)}

reactor.listenTCP(8222, sshFactory)

# Nevow / Athena

from twisted.python.util import sibpath
from nevow import flat, rend, athena, loaders, tags as T
from nevow import inevow
from nevow.athena import LivePage, LiveElement, expose
from nevow.loaders import xmlfile

lectores = {}
# RETORNAR NONE PARA 404
# RENDERHTTP se llama cuando se consumieron todos los segmentos
class TempElement(LiveElement):
        
    docFactory = xmlfile(sibpath(__file__, 'ter.html'))
    jsClass = u'TempDisplay.TempWidget'

    def __init__(self, sitio=''):
        self.sitio = sitio
        self.client = [c for c in factory.clients.values() if c['sitio'].ccc == sitio.ccc][0]['self']
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
        return '<a href="/sitios">sitios</a>'

    def child_sitios(self, ctx):
        return SitiosPage()
                    
    def child_ter(self, ctx):
        return TerPage()

    def child_graph(self, ctx):
        return GraphPage()

    def child_todo(self, ctx):
        return TodoPage()

class SitiosPage(rend.Page):

    addSlash = True
    
    def renderHTTP(self, ctx):
        return render_to_string('sitios.html', {'clientes': factory.clients.values()}).encode('utf-8')
        
    def childFactory(self, ctx, name):
        # si name esta conectado
        return SitioPage(name)        
        
class SitioPage(rend.Page):

    addSlash = True
    
    def __init__ (self, name, *args, **kwargs):
        self.name = name    # VERIFICAR QUE SEA UN SITIO DE LA BD Y QUE ESTE ONLINE
        self.sitio = Sitio.objects.get(ccc=self.name)
        rend.Page.__init__ ( self, *args, **kwargs )
        
    def renderHTTP(self, ctx):
        return render_to_string('sitio.html', {'sitio': self.sitio }).encode('utf-8')
        
    def childFactory(self, ctx, name):
        return RobotPage(name, self.sitio)       
            
class RobotPage(rend.Page):

    addSlash = True
    
    def __init__ (self, name, sitio, *args, **kwargs):
        self.name = name
        self.sitio = sitio
        rend.Page.__init__ ( self, *args, **kwargs )
        
    def renderHTTP(self, ctx):
        print "generando pagina" * 5
        robot = Robot.objects.get(sitio=self.sitio, mbdir=self.name)
        count = Valor.objects.filter(robot=robot).count()
        print "COUNT", count
        valores = Valor.objects.filter(robot=robot)[count -20:count]
        return render_to_string('robot.html', {'sitio': self.sitio, 'robot': robot, 'valores': valores }).encode('utf-8')
        
    def childFactory(self, ctx, name):
        return None
        
from nevow import appserver
site = appserver.NevowSite(IndexPage())
#reactor.listenTCP(8009, site)
reactor.listenTCP(8080, site)

# DB Pool
dbpool = adbapi.ConnectionPool('MySQLdb', host='10.0.0.10', port=3306, db='kimera_kimera', user='kimera', passwd='kimera')

# Django Templates
from django.template.loader import render_to_string
#from django.template import Template, Context
#rendered = render_to_string('my_template.html', { 'foo': 'bar' })
#print rendered

reactor.run()
