from twisted.protocols.basic import LineOnlyReceiver

from twisted.internet.protocol import Factory
from twisted.internet import reactor

from sys import stdout

#from twisted.python import log
#log.startLogging(stdout)

class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        print 'R: ' + line
        
    def connectionMade(self):
        self.transport.write(":CONECTADO\r\n") 
        
class TModBusFactory(Factory):
    protocol = TModBus

reactor.listenTCP(8007, TModBusFactory())
reactor.run()

