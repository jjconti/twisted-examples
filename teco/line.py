from twisted.protocols.basic import LineOnlyReceiver
from twisted.application import internet, service
from twisted.internet.protocol import Factory
from twisted.internet import reactor

from sys import stdout

#from twisted.python import log
#log.startLogging(stdout)

from twisted.internet.task import LoopingCall

class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        print 'Recived: ' + line
        #self.process(line)
        
    def connectionMade(self):
        self.factory.clients.append(self)
        self.peer = self.transport.getPeer()
        self.transport.write("Bienvenido %s:%d" % (self.peer.host, self.peer.port) + '\r\n')
        self.transport.write("Ya somos %d" % (len(self.factory.clients),) + '\r\n')
    
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        #TODO: do something with reason
        
    def process(self, line):    #FIXME: esta funcion debe detectar errores
        print '-' * 80
        print "Mensaje desde %s:%d" % (self.peer.host, self.peer.port) 
        if not line.startswith(':'):
            print "Error en mensaje: no empieza con :"
        else:
            dispid = line[1:3]
            print "ID de dispositivo: " + dispid
            funcode = line[3:5]
            print "Function Code: " + funcode
        print '-' * 80
        
class TModBusFactory(Factory):
    protocol = TModBus
    
    def paso():
        print "paso 5 segundos"
        
    lc = LoopingCall(paso)
    lc.start(5)

   def stopFactory(self):
       self.lc.stop()    
       
    def __init__(self):
        self.clients = []    

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

reactor.listenTCP(2222, getManholeFactory(globals(), admin='aaa'))

reactor.run()
