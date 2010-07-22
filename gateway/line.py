from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import Factory
from twisted.internet import reactor

from constants import *
from twisted.python import log
from twisted.python.logfile import DailyLogFile
log.startLogging(DailyLogFile('log.txt', LOGDIR))

from pymodbus.transaction import ModbusSocketFramer, ModbusAsciiFramer
from pymodbus.factory import ServerDecoder, ClientDecoder

from queue import Queue

socketFramer = ModbusSocketFramer(ServerDecoder())
asciiFramer = ModbusAsciiFramer(ClientDecoder())
slaves = {}

class Sitio(object):
    pass

class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        print "reciboooooooo", line
        self.process(line)

    def connectionMade(self):
        #self.factory.clients.append(self)
        self.deferreds = Queue()
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
            sitio = line[5:8]
            print "SITIO", sitio
            #
            # verificar si ya hay un G24 registrado para ese sitio
            #
            for k,v in self.factory.clients.items():
                if v['sitio'] and sitio == v['sitio'].ccc:
                    print "%s ya estaba conectado. Borrando anterior." % sitio
                    self.factory.clients[k]['self'].transport.loseConnection()
                    del self.factory.clients[k] #move(sitios[sitio])
                    break
            try:
                slaves[sitio] = self

                self.sitio = Sitio()
                self.sitio.ccc =  sitio
                self.factory.clients[id(self)]['sitio'] = self.sitio
                self.sitio.online = True
                self.canal_ocupado = False
                # Escuchar Modbus IP en un puerto dado
                # Ver si todos estos datos se necesitan
                modbustab[self.sitio.ccc] = {'canal': self}
                #mbproxy.new_sitio(self.sitio)
                #escucharModbusIP(self.sitio)
            except Sitio.DoesNotExist:
                print "El sitio %s no existe en la base de datos." % sitio
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
        if not self.deferreds.empty():
            self.deferreds.get().callback(response)
            # Si hay promesas en la cola, sacar y mandar linea
            if not self.deferreds.empty():
                self.sendLine(self.deferreds.get().line)
        # enviar a Mango

    def sendLineWithDeferred(self, line):
        d = Deferred()
        d.line = line
        self.deferreds.put(d)
        if self.state == IDLE:
            self.state = WAITING
            self.sendLine(line)
            self.delayedCall = reactor.callLater(10, self.checkOcupacionCanal)
        return d

    def checkOcupacionCanal(self, disp):
        if self.state == WAITING:
            print "Liberando el canal ", self.sitio.ccc
            self.deferreds.get()
            self.state = IDLE
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

modbustab = {}  # clave ccc, valor tupla (ultimosdatos, id protocolo, sitio)

class AdminDataBlock(ModbusSequentialDataBlock):
    '''
    Representa si los robots estan o no en linea.
    0: on line
    1: off line

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
                sitio = Sitio.objects.get(port=500+int(self.context.slave))
                if address == 0:
                    res.append(sitio.online)
                for r in sitio.robot_set.order_by('mbdir').all():
                    #print r.mbdir, r.online
                    errores = modbuses[sitio.ccc].store[r.mbdir].errores
                    if errores > 3:
                        robotonline = 1
                    else:
                        robotonline = 0
                    # si el sitio no esta on line, tampoco el robot
                    res.append(max(sitio.online, robotonline))
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
                           sitio=None   #ccc?
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
        packet = asciiFramer.buildPacket(request)
        print "ASCII", packet
        # Send like to slave using ascii Modbus
        response = slaves[self.ccc].sendLineWithDeferred(packet)
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
