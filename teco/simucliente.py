from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor
from sys import stdout
#from twisted.python import log
#log.startLogging(stdout)

def gotProtocol(p):
    p.sendLine(":123456789")
    reactor.callLater(1, p.sendLine, ":909090909090")
    reactor.callLater(10, p.sendLine, ":90904444490")
    reactor.callLater(12, p.transport.loseConnection)

class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        print 'ccccccccccc'
        print line
        
    def sendLine(self, line):
        print 'S: ' + line
        LineOnlyReceiver.sendLine(self, line)        

class TModBusClientFactory(ReconnectingClientFactory):
    def startedConnecting(self, connector):
        print 'Started to connect.'
    
    def buildProtocol(self, addr):
        print 'Connected.'
        return TModBus()
    
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)
       
reactor.connectTCP("localhost", 8007, TModBusClientFactory())
reactor.run()

