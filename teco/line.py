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
#log.startLogging(stdout)

from twisted.internet.task import LoopingCall

from twisted.internet.threads import deferToThread

import re
# DB Django
import sys

sys.path = sys.path + ['/home/juanjo/python/twisted/teco/dproj']
sys.path = sys.path + ['D:\escr\line\dproj']
from dproj.piel.models import *
#print len(Robot.objects.filter(nombre__startswith='juanjo'))
# Django Templates
from django.template.loader import render_to_string

#JSON Encoder
try:
    import json
except:
    import simplejson as json

jsonencoder = json.JSONEncoder(skipkeys=True, ensure_ascii=False)

class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        try:
            self.process(line)
        except Exception, e:
            print "Se recibio un valor erroneo en line.", e
        
    def connectionMade(self):
        #self.factory.clients.append(self)
        self.state = IDLE
        self.factory.clients[id(self)] = {'self': self, 'sitio': None}
        self.peer = self.transport.getPeer()
        print "Nuevo cliente: %s:%d" % (self.peer.host, self.peer.port) #LOG
        print "Total: %d" % (len(self.factory.clients),)
        deferToThread(Evento(tipo='I', texto="Nuevo cliente: %s:%d" % (self.peer.host, self.peer.port)).save)
    
    def connectionLost(self, reason):
        if id(self) in self.factory.clients:
            #if self.factory.clients[id(self)]['mbport']:
            #    self.factory.clients[id(self)]['mbport'].loseConnection()
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
                    deferToThread(Evento(tipo='W', texto="%s ya estaba conectado. Borrando anterior." % sitio).save)
                    self.factory.clients[k]['self'].transport.loseConnection()
                    #if self.factory.clients[id(self)]['mbport']:
                    #    self.factory.clients[id(self)]['mbport].loseConnection()
                    del self.factory.clients[k] #move(sitios[sitio])
                    break
            try:
                self.sitio = Sitio.objects.get(ccc=sitio)
                self.factory.clients[id(self)]['sitio'] = self.sitio    #dejar uno solo
                Evento(tipo='I', texto="Se conecto el sitio %s" % self.sitio).save()

                # Escuchar Modbus IP en un puerto dado
                #self.factory.clients[id(self)]['mbport'] = escucharModbusIP(self.sitio)
                modbustab[self.sitio.ccc] = ({}, id(self), self.sitio)
                escucharModbusIP(self.sitio.ccc)
            except Sitio.DoesNotExist:
                print "El sitio %s no existe en la base de datos." % sitio
                deferToThread(Evento(tipo='A', texto="El sitio %s no existe en la base de datos." % sitio).save)
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
                elif func == WB:
                    self.process_write_reg(disp, body)  # aparentemente no hay nada
                                                        # distinto entre escribir una
                                                        # bobina y un registro
    def process_id(self, disp, body):
        print "Dispositivo %s: %s" % (disp, body)
        
    mascaras = {}
    for r in RobotTipo.objects.all():
        print r.mascara
        print r.id
        mascaras[r.id] = re.compile(str(r.mascara.strip()))
    def process_read(self, disp, body):
        robot = factory.clients[id(self)]['sitio'].robot_set.get(mbdir=disp)
        m = TModBus.mascaras[robot.tipo.id].match(body)
        if m:
            try:
                d = m.groupdict()
                modbustab[self.sitio.ccc][0][disp] = d
                #fctory.clients[id(self)]['last'][robot.mbdir] = d
                d['robot'] = robot
                v = Valor(**d)
                v.save()
                print "Guradado en al BD", self.sitio, disp, d
            except Exception, e:
                print "Error al intentar guardar los datos en la BD.", e

            sitio = factory.clients[id(self)]['sitio']
            
            d.pop('robot')
            if lectores.get(robot):
                print len(lectores[robot]), "lectores"
                j = unicode(jsonencoder.encode(d))
                for l in lectores[robot].values():
                    #l.callRemote('actualizarValores', u','.join([v.ea1, v.ea2, v.ea3, v.ea4, v.re1, v.re2,
                    #                                             v.re3, v.re4, v.sd1, v.sd2, v.sd3, v.sd4, v.ed1, v.ed2]))
                    print "Enviando al browser", j
                    l.callRemote('actualizarValores2', j)
                    #l.callRemote('actualizarValores2', u'{"ea1": 1}')
                    
            if graficos.get(robot):
                print len(graficos[robot]), "graficos"
                j = unicode(jsonencoder.encode(d))
                for g in graficos[robot].values():
                    #g.callRemote("nuevoValor", u",".join([v.ea1, v.ea2, v.ea3, v.ea4, v.re1, v.re2,
                    #                                  v.re3, v.re4, v.sd1, v.sd2, v.sd3, v.sd4]))
                    g.callRemote('nuevoValor2', j)
            self.state = IDLE
            
    def process_write_reg(self, disp, body):
        robot = factory.clients[id(self)]['sitio'].robot_set.get(mbdir=disp)
        sitio = factory.clients[id(self)]['sitio']

        #011100
        reg = int(body[:2])
        val = int(body[2:4])
        err = int(body[4:6])
        if err == NOERR:
            pass
        elif err == ERRREG:
            print "Error en el registro %s" % (reg,)
        elif err == ERRVAL:
            print "Error en el valor %s" % (val,)

        if lectores.get(robot):
            for l in lectores[robot].values():
                if err == NOERR:
                    print "sin errores al escribir elr egistro"*2
                    l.callRemote('enableChange')
                if err == ERRREG:
                    l.callRemote('errorMesg', 'Error de registro')                        
                if err == ERRVAL:
                    l.callRemote('errorMesg', 'Error en el valor')                        
    def ask_id(self, disp):
        self.sendLine(':%02d%d%02d' % (disp, ID, LR))
    
    def ask_read(self, disp):
        self.sendLine(':%02d%d%02d' % (disp, RD, LR))
        self.state = WAITING

    def ask_write_reg(self, disp, reg, val):
        print "Se cambiara el reg", reg, "valor", val
        line = ':%02d%d%02d%02d%02d' % (disp, WR, reg, val, LR)
        print "Enviando: %s" % line
        self.sendLine(line)
            
    def ask_write_bob(self, disp, bob, val):
        if val not in (0,1):
            return
        print "Se cambiara la bobina", bob, "valor", val
        line = ':%02d%d%02d%d%02d' % (disp, WB, bob, val, LR)
        print "Enviando: %s" % line
        self.sendLine(line)
        
class TModBusFactory(Factory):
    protocol = TModBus
    writeBuffer = {}    # clave prolocolo, valor triplete para ask_write_reg
    
    def paso(self):
        print "Clientes actualmente conectados: ", len(self.clients)
        for k,c in self.clients.items():
            if k in terminales: # si se esta usando la terminal, no consultar
                continue
            n = 1
            if c['sitio']:
                for r in c['sitio'].robot_set.all():
                    rmbdir = int(r.mbdir)
                    def f(r, cl):
                        print "Se preguntara al robot ", r, cl['sitio'].ccc
                        cl['self'].ask_read(r)
                    reactor.callLater(5*n, f, rmbdir, c)

                    if c['sitio'].ccc.startswith('VM'):
                        print "Este sitio es una valija."
                        reactor.callLater(5*n + 10, f, rmbdir, c)   #HARDCODED
                        
                    n += 1
            if k in self.writeBuffer:    # hay elementos para escribir en este sitio
                print "Calendarizando escritura."
                def f(cl, t, d, r, v):
                    if t == WR:
                        cl['self'].ask_write_reg(d, r, v)
                    elif t == WB:
                        cl['self'].ask_write_bob(d, r, v)
                reactor.callLater(0, f, c, *self.writeBuffer[k])
                self.writeBuffer.pop(k)
                
    def stopFactory(self):
        self.lc.stop()    
       
    def __init__(self):
        #self.clients = []
        self.clients = {}
        self.lc = LoopingCall(self.paso)
        #self.lc.start(60)
        self.lc.start(20)        

factory = TModBusFactory()
#reactor.listenTCP(9007, factory)
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
from nevow import static, flat, rend, athena, loaders, tags as T
from nevow import inevow
from nevow.athena import LivePage, LiveElement, expose
from nevow.loaders import xmlfile

lectores = {}

# RENDERHTTP se llama cuando se consumieron todos los segmentos
class TempElement(LiveElement):
        
    jsClass = u'TempDisplay.TempWidget'

    def __init__(self, sitio='', robot=''):
        self.sitio = sitio
        self.robot = robot
        self.client = [c for c in factory.clients.values() if c['sitio'].ccc == robot.sitio.ccc][0]['self']
        d = {'robot': self.robot}
        d.update(self.robot.config_dict())
        s = render_to_string('tero.html', d).encode('utf-8')
        self.docFactory = loaders.xmlstr(s)
        super(TempElement, self).__init__()

    def read(self):
        print "Se apreto el boton read"
        # TODO: verificar que sea un sitio valido
        if lectores.get(self.robot):
            if id(self) in lectores[self.robot].keys():
                del lectores[self.robot][id(self)]
            else:
                lectores[self.robot][id(self)] = self
        else:
            lectores[self.robot] = {id(self): self}
    read = expose(read)

    def change(self, consigna, val):
        print "Se apreto el bonton change"
        try:
            consigna = int(consigna)
            val = int(val)
            disp = int(self.robot.mbdir)
        except:
            print "Excepcion algun valor no era un entero compatible."
            return
        # si no se despacho un cambio para un sitio y llega un nuevo
        # cambio, se pisa al anterior.
        print "llenando el buffer."
        factory.writeBuffer[id(self.client)] = (WR, disp, consigna, val)
    change = expose(change)

    def changeSD(self, consigna, val):
        '''
        val es el valor a cambiar.
        '''
        print "Se apreto el bonton change de SD"
        try:
            consigna = int(consigna)
            val = 1 - int(val)  # 0 -> 1, 1 ->0
            disp = int(self.robot.mbdir)
        except:
            print "Excepcion algun valor no era un entero compatible."
            return
        # si no se despacho un cambio para un sitio y llega un nuevo
        # cambio, se pisa al anterior.
        print "llenando el buffer."
        factory.writeBuffer[id(self.client)] = (WB, disp, consigna, val)
    changeSD = expose(changeSD)
    
class TerPage(LivePage):

    addSlash = True
    
    docFactory = loaders.stan(T.html[
        T.head(render=T.directive('liveglue')),
        T.body(render=T.directive('myElement'))])

    def __init__(self, sitio='', robot='', *args, **kwargs):
        self.sitio = sitio
        self.robot = robot
        LivePage.__init__ (self, *args, **kwargs)
        
    def beforeRender(self, ctx):
        d = self.notifyOnDisconnect()
        d.addErrback(self.disconn)

    def disconn(self, reason):
        if lectores.get(self.robot):
            if id(self.element) in lectores[self.robot].keys():
                del lectores[self.robot][id(self.element)]

    def render_myElement(self, ctx, data):
        self.element = TempElement(self.sitio, self.robot)
        self.element.setFragmentParent(self)
        return ctx.tag[self.element]

    def childFactory(self, ctx, name):
        return TerPage(name)

graficos = {}

class GraphElement(LiveElement):

    jsClass = u'GraphDisplay.GraphWidget'

    def __init__(self, sitio='', robot=''):
        self.sitio = sitio
        self.robot = robot
        d = robot.config_dict(True) # True: solo los graficables
        s = render_to_string('graph.html', {'robot': robot,
                                            'analogicas': d['entradasanalogicas'] + d['registros'],
                                            'digitales': d['entradasdigitales'] + d['salidasdigitales']}
                            ).encode('utf-8')
        self.docFactory = loaders.xmlstr(s)        
        super(GraphElement, self).__init__()
        
    def start(self):
        print "Se apreto el bonton start"
        # TODO: verificar que sea un sitio valido
        if graficos.get(self.robot):
            if id(self) in graficos[self.robot].keys():
                del graficos[self.robot][id(self)]
            else:
                graficos[self.robot][id(self)] = self
        else:
            graficos[self.robot] = {id(self): self}
    start = expose(start)
    
class GraphPage(LivePage):

    addSlash = True
    
    docFactory = loaders.stan(T.html[
        T.head(render=T.directive('liveglue')),
        T.body(render=T.directive('myElement'))])
    
    def __init__(self, sitio='', robot= '', *args, **kwargs):
        self.sitio = sitio
        self.robot = robot
        LivePage.__init__ (self, *args, **kwargs)
        
    def beforeRender(self, ctx):
        d = self.notifyOnDisconnect()
        d.addErrback(self.disconn)

    def afterRender(self, ctx):
        d = self.robot.confignames_dict(True)   # True: solo los graficables
        self.element.callRemote('inicializar', d)
        
    def disconn(self, reason):
        if graficos.get(self.robot):
            if id(self.element) in graficos[self.robot].keys():
                del graficos[self.robot][id(self.element)]

    def render_myElement(self, ctx, data):
        request = inevow.IRequest(ctx)
        print request.prepath
        self.element = GraphElement(self.sitio, self.robot)
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
        
        if lectores.get(self.robot):
            if id(self.element1) in lectores[self.robot].keys():
                del lectores[id(self.element1)]
            
        if graficos.get(self.robot):
            if id(self.element2) in graficos[self.robot].keys():
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

        
class IndexPage(rend.Page):


    def __init__ ( self, *args, **kwargs ):
        rend.Page.__init__ ( self, *args, **kwargs )

    def renderHTTP(self, ctx):
        return '<a href="/sitios/">sitios</a><br/><a href="/celu/">celu</a>'

    def child_sitios(self, ctx):
        return SitiosPage()

    def child_celu(self, ctx):
        return CeluPage()
    
    def child_ter(self, ctx):
        return TerPage()

    def child_graph(self, ctx):
        return GraphPage()

    def child_todo(self, ctx):
        return TodoPage()

    def child_imgs(self, ctx):
            return static.File(os.path.join(ROOT_PATH, 'imgs')) 
            
class SitiosPage(rend.Page):

    addSlash = True
    
    def renderHTTP(self, ctx):
        return render_to_string('sitios.html', {'clientes': factory.clients.values()}).encode('utf-8')
        
    def childFactory(self, ctx, name):
        # si name esta conectado
        return SitioPage(name)        

class CeluPage(rend.Page):

    addSlash = True
    
    def renderHTTP(self, ctx):
        #return render_to_string('celu.html', {'clientes': factory.clients.values()}).encode('utf-8')
        return render_to_string('celu.html', {'sitios': Sitio.objects.all()}).encode('utf-8')
        
    def childFactory(self, ctx, name):
        # si name esta conectado
        return SitioCeluPage(name)
    
class SitioPage(rend.Page):

    addSlash = True
    
    def __init__ (self, name, *args, **kwargs):
        self.name = name    # VERIFICAR QUE SEA UN SITIO DE LA BD Y QUE ESTE ONLINE
        try:
            self.sitio = Sitio.objects.get(ccc=self.name)
        except Sitio.DoesNotExist:
            self.sitio = None
        rend.Page.__init__ ( self, *args, **kwargs )
        
    def renderHTTP(self, ctx):
        if not self.sitio:
            return ''
        return render_to_string('sitio.html', {'sitio': self.sitio }).encode('utf-8')
        
    def childFactory(self, ctx, name):
        return RobotPage(name, self.sitio)       

class SitioCeluPage(rend.Page):

    addSlash = True
    
    def __init__ (self, name, *args, **kwargs):
        self.name = name    # VERIFICAR QUE SEA UN SITIO DE LA BD Y QUE ESTE ONLINE
        try:
            self.sitio = Sitio.objects.get(ccc=self.name)
        except Sitio.DoesNotExist:
            self.sitio = None
        rend.Page.__init__ ( self, *args, **kwargs )
        
    def renderHTTP(self, ctx):
        if not self.sitio:
            return ''
        valores = []
        for r in self.sitio.robot_set.all():
            valores.append(Valor.objects.filter(robot=r).order_by('-id')[0])
            #valores.append(r.last_valor)

        if self.sitio.ccc.startswith('VM'):
            html = 'sitioceluvalija.html'   # hack, esto debe estar en la bd
        else:
            html = 'sitiocelu.html'
        return render_to_string(html, {'sitio': self.sitio,
                                                    'valores': valores}).encode('utf-8')
    
class RobotPage(rend.Page):

    addSlash = True
    
    def __init__ (self, name, sitio, *args, **kwargs):
        self.name = name
        self.sitio = sitio
        try:
            self.robot = Robot.objects.get(sitio=self.sitio, mbdir=self.name)
        except Robot.DoesNotExist:
            self.robot = None
        
        rend.Page.__init__ ( self, *args, **kwargs )
        
    def renderHTTP(self, ctx):
        if self.robot:
            try:            
                count = Valor.objects.filter(robot=self.robot).count()
            except Valor.DoesNotExist:
                return ''
            #valores = Valor.objects.filter(robot=self.robot)[count -20:count]
            valores = []
            return render_to_string('robot.html', {'sitio': self.sitio,
                                                   'robot': self.robot, 
                                                   'valores': valores }).encode('utf-8')
        else:
            return ''
                    
    def child_grafica(self, ctx):
        return GraphPage(sitio=self.sitio, robot=self.robot)

    def child_control(self, ctx):
        return TerPage(sitio=self.sitio, robot=self.robot)     
            
from nevow import appserver
site = appserver.NevowSite(IndexPage())
reactor.listenTCP(8009, site)
reactor.listenTCP(8080, site)

# DB Pool
#dbpool = adbapi.ConnectionPool('MySQLdb', host='10.0.0.10', port=3306, db='kimera_kimera', user='kimera', passwd='kimera')

#from django.template import Template, Context
#rendered = render_to_string('my_template.html', { 'foo': 'bar' })
#print rendered

# Modbus
from pymodbus.server.async import ModbusServerFactory, _logger
from pymodbus.datastore import ModbusServerContext, ModbusSequentialDataBlock
import logging

from decimal import Decimal as D
def por10(x):
    '''
    Multiplica por 10 y devuelve un entero.
    '''
    return int(D(x) * 10)

from operator import itemgetter

modbustab = {}  # clave ccc, valor tupla (ultimosdatos, id protocolo, sitio)
class MyDataBlock(ModbusSequentialDataBlock):
    
    def __init__(self, tipo, ccc, address=None, values=None):
        '''
        Initializes the datastore
        '''
        self.ccc = ccc
        self.tipo = tipo
        self.address = 0
        self.values = [0] * 30 #pymodbus lo usa!
        self.default_value = None

    def checkAddress(self, address, count=1):
        return True
    
    def getValues(self, address, count=1):
        print "get", self.tipo, address, count
        res = []
        #data = [x['last'] for x in factory.clients.values() if x.sitio == self.sitio][0]
        data = modbustab[self.ccc][0]
        #for robot in self.clientdata['self'].sitio.robot_set.order_by('mbdir').all():#sorted(data.keys()):
        for robot in modbustab[self.ccc][2].robot_set.order_by('mbdir').all():#sorted(data.keys()):
            mbdir = int(robot.mbdir)
            items = data.get(mbdir)
            if items:
                #                      [ea1. ea2, ea3... ea10]
                p = [por10(y) for y in [items.get(self.tipo + str(i), -1) for i in range(1,11)]] # registros ordenados
                res.extend(p)
            else:   # si un robot no reporto datos, completar sus registros con -1
                res.extend([-1] * 10)
        print res[address:address+count]            
        return res[address:address+count]            
    
    def setValues(self, address, values):
        print "Set Value address", address, "values", values
        disp, reg = divmod(address, 10)
        disp += 1
        reg += 1
        value = values[0]
        if type(value) == bool:
            value = int(value)
        else:
            value = value / 10
        print "disp", disp, "reg", reg, "value", value

        c = modbustab[self.ccc][1]
        if self.tipo == 're':
            factory.writeBuffer[c] = (WR, disp, reg, value)
        elif self.tipo == 'sd':
            factory.writeBuffer[c] = (WB, disp, reg, value)
        print "Fin del set"            


class MyDataBlock2(ModbusSequentialDataBlock):
    
    def __init__(self, tipo, clientdata, uid, address=None, values=None):
        '''
        Initializes the datastore
        '''
        self.uid = uid
        self.clientdata = clientdata
        self.tipo = tipo
        self.address = 0
        self.values = [0] * 30 #pymodbus lo usa!
        self.default_value = None

    def checkAddress(self, address, count=1):
        return True
    
    def getValues(self, address, count=1):
        print "get", self.tipo, address, count
        res = []
        # Seleccionando a mano los datos para el sitio SJR
        data = self.clientdata['last']
        mbdir = "%02.d" % self.uid
        items = data.get(mbdir)
        if items:
            #                      [ea1. ea2, ea3... ea10]
            p = [por10(y) for y in [items.get(self.tipo + str(i), 0) for i in range(1,11)]] # registros ordenados
            res.extend(p)
        else:   # si un robot no reporto datos, completar sus registros con -1
            res.extend([0] * 10)
        print res[address:address+count]            
        return res[address:address+count]            
    
    def setValues(self, address, values):
        print "Set Value address", address, "values", values
        disp, reg = divmod(address, 10)
        disp += 1
        reg += 1
        value = values[0]
        if type(value) == bool:
            value = int(value)
        else:
            value = value / 10
        print "disp", disp, "reg", reg, "value", value
        
        if self.tipo == 're':
            factory.writeBuffer[id(self.clientdata['self'])] = (WR, disp, reg, value)
        elif self.tipo == 'sd':
            factory.writeBuffer[id(self.clientdata['self'])] = (WB, disp, reg, value)
        print "Fin del set"            
modbuses = []   # probablemente se deba borrar, ya que solo llena la mem
def escucharModbusIP(ccc):
    print "Empezando a escuchar" *3
    context = ModbusServerContext(d=MyDataBlock('ed', ccc),
                                  c=MyDataBlock('sd', ccc),
                                  i=MyDataBlock('ea', ccc),
                                  h=MyDataBlock('re', ccc))
    mbfactory = ModbusServerFactory(context)
    modbuses.append(mbfactory)
    return reactor.listenTCP(modbustab[ccc][2].port, mbfactory)
    #print "Abierto el puerto", clientdata['sitio'].port
    #_logger.setLevel(logging.DEBUG)

# Que empiece la fiesta
reactor.run()
