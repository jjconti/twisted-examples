from twisted.protocols.basic import LineOnlyReceiver
from twisted.application import internet, service
from twisted.internet.protocol import Factory
from twisted.internet import reactor

from sys import stdout

#from twisted.python import log
#log.startLogging(stdout)

class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        print 'Recived: ' + line
        self.process(line)
        
    def connectionMade(self):
        self.peer = self.transport.getPeer()
        self.transport.write("Bienvenido %s:%d" % (self.peer.host, self.peer.port) + '\r\n')

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

reactor.listenTCP(8007, TModBusFactory())
reactor.run()
