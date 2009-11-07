from twisted.protocols.basic import LineOnlyReceiver

from twisted.internet.protocol import Protocol, ClientCreator, ClientFactory
from twisted.internet import reactor
from sys import stdout
#from twisted.python import log
#log.startLogging(stdout)
import random

class CModBus(LineOnlyReceiver):

    def connectionMade(self):
        # Saludo inicial
        sitio = raw_input("Ingresar CDL (3 letras): ")
        sitio = (sitio + 'JJC')[:3].upper()
        self.sendLine(":0090" + sitio + "00")
        
    def lineReceived(self, line):
        print line
        if line.startswith(':0142'):
            self.sendLine(':0142' + self.factory.nuevoEstado() + '111100')
        elif line.startswith(':0143'):
            c = line[5:7]
            valor = int(line[7:9])
            if c == '01':
                self.factory.c1 = valor
            elif c == '02':
                self.factory.c2 = valor
            elif c == '03':
                self.factory.c3 = valor
            elif c == '04':
                self.factory.c4 = valor
            self.sendLine(line)
            
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
        self.c1 = 12
        self.c2 = 23
        self.c3 = 33
        self.c4 = 36
        
    def nuevoEstado(self):
        r = "%04.1f"*8 % (self.ea1, self.ea2, self.ea3, self.ea4,
                          self.c1, self.c2, self.c3, self.c4)
        self.ea1 += self.ea1_d
        self.ea2 += self.ea2_d
        self.ea3 += self.ea3_d
        self.ea4 += self.ea4_d                        
        # some random lies
        if self.ea1 > 30:
            self.ea1_d = -0.2 * random.choice([0,1,1])
        if self.ea1 < 12:
            self.ea1_d = 0.3 * random.choice([0,0,1])
        if self.ea2 > 20:
            self.ea2_d = -0.1 * random.choice([0,1,1])
        if self.ea2 < 10:
            self.ea2_d = 0.2 * random.choice([0,1,0])
        if self.ea3 > 30:
            self.ea3_d = -0.2 * random.choice([0,0,1])
        if self.ea3 < 12:
            self.ea3_d = 0.3 * random.choice([0,1,1,0,0,0])
        if self.ea4 > 20:
            self.ea4_d = -0.1 * random.choice([0,1,0,0])
        if self.ea4 < 10:
            self.ea4_d = 0.2 * random.choice([0,1,0])
                    
        return r
                                                  
    def startedConnecting(self, connector):
        print 'Started to connect.'
    
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
    
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason

reactor.connectTCP('localhost', 8007, CModBusFactory())
reactor.run()


