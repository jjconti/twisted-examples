from twisted.protocols.basic import LineOnlyReceiver

from twisted.internet.protocol import Factory
from twisted.internet import reactor

from constants import *
from twisted.python import log
from twisted.python.logfile import DailyLogFile
log.startLogging(DailyLogFile('log.txt', LOGDIR))

from pymodbus.transaction import ModbusSocketFramer, ModbusAsciiFramer
from pymodbus.factory import ServerDecoder, ClientDecoder

from collections import deque

socketFramer = ModbusSocketFramer(ServerDecoder())
asciiFramer = ModbusAsciiFramer(ClientDecoder())
slaves = {}
robots = {}

class Sitio(object):
    pass

class Robot(object):
    def __init__(self, online=True):
        self.online = online
        self.errores = 0

class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        print "reciboooooooo", line
        self.process(line)

    def connectionMade(self):
        #self.factory.clients.append(self)
        self.deferreds = deque()
        self.state = IDLE
        self.delayedCall = None
        self.factory.clients[id(self)] = {'self': self, 'sitio': None}
        self.peer = self.transport.getPeer()
        print "Nuevo cliente: %s:%d" % (self.peer.host, self.peer.port) #LOG
        print "Total: %d" % (len(self.factory.clients),)

    def connectionLost(self, reason):
        if id(self) in self.factory.clients:
            self.sitio.online = False
            del self.factory.clients[id(self)]
            #mbproxy.del_sitio(self.sitio)
        else:
            print "El cliente ya fue eliminado."

    def process(self, line):

        if not line.startswith(':'):
            print "Error en mensaje: no empieza con :"  #EXC
        elif line[3] == '9':   # mensaje del G24 - Saludo inicial
            print "G24 dice: ", line
            ccc = line[5:8]
            print "SITIO", ccc
            #
            # verificar si ya hay un G24 registrado para ese sitio
            #
            for k,v in self.factory.clients.items():
                if v['sitio'] and ccc == v['sitio'].ccc:
                    print "%s ya estaba conectado. Borrando anterior." % sitio
                    self.factory.clients[k]['self'].transport.loseConnection()
                    del self.factory.clients[k] #move(sitios[sitio])
                    break
            try:
                self.sitio = Sitio()
                self.sitio.ccc =  ccc
                self.sitio.online = True
                self.sitio.transport = self
                slaves[ccc] = self.sitio
                robots[ccc] = [Robot() for x in range(ROBOTS[ccc])]
                self.factory.clients[id(self)]['sitio'] = self.sitio
                self.canal_ocupado = False
            except Exception:
                print "El sitio %s no existe en la base de datos." % ccc
        elif line[3] == '6':
            print "G24 dice: ", line
            sitio = line[5:8]
            print "SITIO", sitio
        else:
            # check LRC
            line = line + '\r\n'
            asciiFramer.processIncomingPacket(line, self.sendBack)

    def sendBack(self, response):
        #packet = socketFramer.buildPacket(response)
        if self.deferreds:
            d = self.deferreds.popleft()
            d.callback(response)
            # Poner a 0 los errores del robots
            robots[self.sitio.ccc][d.unit_id - 1].errores = 0
            # Si hay promesas en la cola, sacar y mandar linea
            if self.deferreds:
                #self.sendLine(self.deferreds.popleft().line)
                self.sendLine(self.deferreds[0].line)
            else:
                self.state = IDLE
        # enviar a Mango

    def sendLineWithDeferred(self, line, unit_id):
        d = Deferred()
        d.line = line
        d.unit_id = unit_id
        self.deferreds.append(d)
        if self.state == IDLE:
            self.state = WAITING
            self.sendLine(line)
            self.delayedCall = reactor.callLater(10, self.checkOcupacionCanal,
                                                 unit_id)
        return d

    def checkOcupacionCanal(self, unit_id):
        if self.state == WAITING:
            print "Liberando el canal ", self.sitio.ccc
            self.deferreds.popleft()
            self.state = IDLE
            robots[self.sitio.ccc][unit_id - 1].errores += 1
            #mbproxy.timeout(self.sitio.ccc, disp)

class TModBusFactory(Factory):
    protocol = TModBus
    writeBuffer = {}    # clave prolocolo, valor triplete para ask_write_reg

    def get_protocol(self, ccc):
        s = [x['self'] for x in self.clients.values() if x['sitio']
                                                     and x['sitio'].ccc == ccc]
        if len(s) == 1:
            return s[0]
        else:
            print "El sitio %s no esta en la fabrica" % ccc

    def stopFactory(self):
        #self.lc.stop()
        pass

    def __init__(self):
        self.clients = {}

factory = TModBusFactory()
reactor.listenTCP(9007, factory)
reactor.listenTCP(8007, factory)

# Modbus
from pymodbus.server.async import ModbusServerFactory, ModbusProtocol
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext, \
                               ModbusSequentialDataBlock
from twisted.internet.defer import Deferred

from decimal import Decimal as D
def por10(x):
    '''
    Multiplica por 10 y devuelve un entero.
    '''
    return int(D(x) * 10)

class AdminDataBlock(ModbusSequentialDataBlock):
    '''
    Representa si los robots estan o no en linea.

    dir 0: G24
    dir 1....: robots
    '''

    def __init__(self, tipo, address=None, values=None):
        '''
        Initializes the datastore
        '''
        self.tipo = tipo
        self.address = 0
        self.values = [0] * 30 #pymodbus lo usa!
        self.default_value = None

    def checkAddress(self, address, count=1):
        return True

    def getValues(self, address, count=1):
        '''

        '''
        res = []
        try:
            if self.tipo == 'ed':
                #if address == 0:
                res.append(slaves[self.sitio].online)
                for r in robots[self.sitio]:
                    #print r.mbdir, r.online
                    if r.errores > 3:
                        r.online = True
                    else:
                        r.online = False
                    # si el sitio no esta on line, tampoco el robot
                    res.append(slaves[self.sitio].online and r.online)
            d = Deferred()
        except Exception,e:
            raise e
        #print res, address, count
        d.callback(res[address:address+count])
        return d    # cambair esto usando maybeDeferred mas afuera

    def setValues(self, address, values, slave=None):
        print "Set Value address", address, "values", values


modbuses = {}

class RobotContext(ModbusSlaveContext):

    def __init__(self, **kwargs):
        super(RobotContext, self).__init__(**kwargs)
        self.esperando = False
        self.errores = 0
        self.di.context = self
        self.co.context = self
        self.ir.context = self
        self.hr.context = self

        self.slave = kwargs.get('slave')
        self.sitio = kwargs.get('sitio')

    def addError(self):
        self.errores += 1
        if self.errores > 3:
            self.setRobotStatus(1)  # robot offline

    def cleanErrors(self):
        self.errores = 0
        self.setRobotStatus(0)

    def setRobotStatus(self, status):
        '''
        Set the asociated robot offline.
        '''
        pass

print "Levantando interfaz Modbus IP de mantenimiento"

contexts = {}
for ccc,port in SITIOS.items():
    context = RobotContext(d=AdminDataBlock('ed'),
                           c=AdminDataBlock('sd'),
                           i=AdminDataBlock('ea'),
                           h=AdminDataBlock('re'),
                           slave=port - 500,
                           sitio=ccc
                          )
    context.slave = "%02d" % (port - 500)
    contexts[context.slave] = context

# Servidor Modbus IP administrativo | estado de sitios y robots

mbfactory = ModbusServerFactory(ModbusServerContext(contexts, single=False))
modbuses['aaa'] = mbfactory
reactor.listenTCP(500, mbfactory)

# Servidores Modbus IP para atender pediciones de masters como Mango m2m

class ModbusProtocol2(ModbusProtocol):
    def execute(self, request):
        print "request", request
        print dir(request)
        packet = asciiFramer.buildPacket(request)
        print "ASCII", packet
        # Send like to slave using ascii Modbus
        response = slaves[self.ccc].transport.sendLineWithDeferred(
                                                       packet, request.unit_id)
        response.addCallback(self._execute, request)

class ModbusServerFactory2(ModbusServerFactory):
    protocol = ModbusProtocol2

# No esperar a que se conecten los robots.
# Empezas a escuchar desde el principio
for ccc,port in SITIOS.items():
    if ccc not in modbuses.keys():
        mbfactory = ModbusServerFactory2(None) # None store
        mbfactory.protocol.ccc = ccc
        modbuses[ccc] = mbfactory
        if port != 500:
            reactor.listenTCP(port, mbfactory)

# Que empiece la fiesta
reactor.run()
