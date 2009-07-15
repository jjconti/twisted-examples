from twisted.protocols.basic import LineOnlyReceiver

from twisted.internet.protocol import Protocol, ClientCreator, ClientFactory
from twisted.internet import reactor
from sys import stdout
#from twisted.python import log
#log.startLogging(stdout)
    
def gotProtocol(p):
    p.sendLine(":123456789")    # saludo inicial
    #reactor.callLater(1, p.sendLine, ":909090909090")
    #reactor.callLater(2, p.transport.loseConnection)

class CModBus(LineOnlyReceiver):
    
    def lineReceived(self, line):
        print line
        self.sendLine(':0142' + self.factory.nuevoEstado() + '40.030.020.010.0111100')
        
    def sendLine(self, line):
        print 'S: ' + line
        LineOnlyReceiver.sendLine(self, line)        
 
class CModBusFactory(ClientFactory):
    
    protocol = CModBus
    
    def __init__(self):
        self.ea1 = 12.0
        self.ea1_d = 0.5
        self.ea2 = 11.0
        self.ea2_d = 0.2
        self.ea3 = 22.0
        self.ea3_d = -0.2
        self.ea4 = 30.0
        self.ea4_d = 0 
        
    def nuevoEstado(self):
        r = "%04.1f%04.1f%04.1f%04.1f" % (self.ea1, self.ea2, self.ea3, self.ea4)
        self.ea1 += self.ea1_d
        self.ea2 += self.ea2_d
        self.ea3 += self.ea3_d
        self.ea4 += self.ea4_d                        
        # some random lies
        if self.ea1 > 30:
            self.ea1_d = -0.2
        if self.ea1 < 10:
            self.ea1_d = 0.3
        if self.ea2 > 20:
            self.ea2_d = -0.1
        if self.ea2 < 10:
            self.ea2_d = 0.2
        if self.ea3 > 30:
            self.ea3_d = -0.2
        if self.ea3 < 10:
            self.ea3_d = 0.3
        if self.ea4 > 20:
            self.ea4_d = -0.1
        if self.ea4 < 10:
            self.ea4_d = 0.2
                    
        return r
                                                  
    def startedConnecting(self, connector):
        print 'Started to connect.'
    
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
    
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason

reactor.connectTCP('localhost', 8007, CModBusFactory())
reactor.run()


