from twisted.protocols.basic import LineOnlyReceiver

from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
import random

class CModBus(LineOnlyReceiver):

    def connectionMade(self):
        self.saludo = False
        # Saludo inicial
        sitio = raw_input("Ingresar CDL (3 letras): ")
        sitio = (sitio + 'JJC')[:3].upper()
        self.sendLine(":0090" + sitio + "00")
        self.saludo = True

    def lineReceived(self, line):
        print line
        self.sendLine(line)

    def sendLine(self, line):
        print 'S: ' + line
        print "Enviar?"
        raw_input()
        LineOnlyReceiver.sendLine(self, line)

class CModBusFactory(ClientFactory):

    protocol = CModBus

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason

reactor.connectTCP('localhost', 8007, CModBusFactory())
reactor.run()


