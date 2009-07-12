from twisted.protocols.basic import LineOnlyReceiver

from twisted.internet.protocol import Protocol, ClientCreator
from twisted.internet import reactor
from sys import stdout
#from twisted.python import log
#log.startLogging(stdout)

import random
def r(i):
    return str(i + random.randint(1,9))
    
def gotProtocol(p):
    p.sendLine(":123456789")
    #reactor.callLater(1, p.sendLine, ":909090909090")
    #reactor.callLater(2, p.transport.loseConnection)

class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        print line
        self.sendLine(':0142' + "".join((r(x) for x in [12.3, 12.3, 12.3, 12.3, 30.0, 32.0, 33.0, 34.0])) + '111100')
        
    def sendLine(self, line):
        print 'S: ' + line
        LineOnlyReceiver.sendLine(self, line)        
        
c = ClientCreator(reactor, TModBus)
c.connectTCP("localhost", 8007)#.addCallback(gotProtocol)
reactor.run()

