from twisted.protocols.basic import LineOnlyReceiver
from twisted.application import internet, service
from twisted.internet.protocol import Factory
from twisted.internet import reactor

from twisted.enterprise import adbapi

from sys import stdout

from constants import *
#from twisted.python import log
#log.startLogging(stdout)

from twisted.internet.task import LoopingCall
        
class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        self.process(line)
        
    def connectionMade(self):
        self.factory.clients.append(self)
        self.peer = self.transport.getPeer()
        print "Nuevo cliente: %s:%d" % (self.peer.host, self.peer.port) #LOG
        print "Total: %d" % (len(self.factory.clients),)
    
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
        #TODO: do something with reason
        
    def process(self, line):    #FIXME: esta funcion debe detectar errores
        #print "-%s-" % (line,)
        #return
        #print "R: %s:%d %s" % (self.peer.host, self.peer.port, line)  #LOG
        if not line.startswith(':'):
            print "Error en mensaje: no empieza con :"  #EXC
        else:
            disp = int(line[1:3])   #EXC
            func = int(line[3:5])   #EXC
            body = line[5:]
            #print "D: %01d F: %s B: %s" % (disp, func, body)

            if func not in VALID_FUNCS:
                print "Error: funcion desconida."
            else:
                if func == ID:
                    self.process_id(body)
                elif func == RD:
                    self.process_read(body)
                elif func == WR:
                    self.process_write_reg(body)

    def process_id(self, body):
        print body
        
    def process_read(self, body):
        ea1 = body[:4]
        ea2 = body[4:8]
        ea3 = body[8:12]
        ea4 = body[12:16]
        c1 = body[16:20]
        c2 = body[20:24]
        c3 = body[24:28]
        c4 = body[28:32]
        b1 = body[32:33]
        b2 = body[33:34]
        b3 = body[34:35]
        b4 = body[35:36]                                    
        i1 = body[36:37]
        i2 = body[37:38]
        print ea1, ea2, ea3, ea4, c1, c2, c3, c4, b1, b2, b3, b4, i1, i2
        print "Guardando en bd"
        dbpool.runQuery('''INSERT INTO valores (sitio, dispositivo, a1, a2, a3, a4,
                           c1, c2, c3, c4, b1, b2, b3, b4, i1, i2) VALUES (%s, %s,
                           %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                           (2, 1, ea1, ea2, ea3, ea4, c1, c2, c3, c4, b1, b2, b3, b4, i1, i2))

    def process_write_reg(self, body):
        reg = body[2:]
        err = body[2:4]
        if err == NOERR:
            pass
        elif err == ERRREG:
            print "Error en el registro %s" % (reg,)   #LOG
        elif err == ERRVAL:
            print "Error en el valor %s" % (val,)  #LOG
                        
    def ask_id(self, disp):
        self.sendLine(':%02d%d%02d' % (disp, ID, LR))
    
    def ask_read(self, disp):
        self.sendLine(':%02d%d%02d' % (disp, RD, LR))

    def ask_write_reg(self, disp, reg, val):
        self.sendLine(':%02d%d%02d%02d%02d' % (disp, WR, reg, val, LR))
            
class TModBusFactory(Factory):
    protocol = TModBus
    
    def paso(self):
        for c in self.clients:
            c.ask_read(1)

    def stopFactory(self):
        self.lc.stop()    
       
    def __init__(self):
        self.clients = []
        self.lc = LoopingCall(self.paso)
        self.lc.start(60)        

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

# WEB
from twisted.web import server, resource

class Demo(resource.Resource):
    isLeaf = 1

    def __init__(self, links) :
        resource.Resource.__init__(self)
        self.links = links
        self.factory = factory

    def render_GET(self, request):
        cliente = request.args['cliente']
        disp = request.args['disp']
        func = request.args['func'].pop()
        if func == 'id':
            self.factory.clients[int(cliente[0])].ask_id(int(disp[0]))
        elif func == 'read':
            self.factory.clients[int(cliente[0])].ask_read(int(disp[0]))        
        return "Paquete enviado! " + func
        
site = server.Site(Demo([])) 
reactor.listenTCP(8008, site)

# DB Pool
dbpool = adbapi.ConnectionPool('MySQLdb', db='kimera_kimera', user='kimera_kimera', passwd='kimera_kimera')
#dbcursor = db.cursor() 

reactor.run()
