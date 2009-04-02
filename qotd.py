from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

class QOTD(Protocol):

    def connectionMade(self):
        self.factory.numProtocols = self.factory.numProtocols+1 
        if self.factory.numProtocols > 2:
            self.transport.write("Too many connections, try later") 
            self.transport.loseConnection()
            return
        self.transport.write("An apple a day keeps the doctor away\r\n") 
        self.transport.loseConnection()

    def connectionLost(self, reason):
        self.factory.numProtocols = self.factory.numProtocols-1

# Next lines are magic:
factory = Factory()
factory.numProtocols = 0
factory.protocol = QOTD

# 8007 is the port you want to run under. Choose something >1024
reactor.listenTCP(8007, factory)
reactor.run()

