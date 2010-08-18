from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory
from twisted.python import log
from twisted.python.logfile import DailyLogFile

from constants import LOGDIR
from config import slaves, robots

from collections import deque
log.startLogging(DailyLogFile('log.txt', LOGDIR))

from listenTCP import asciiFramer

class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        self.process(line)

    def connectionMade(self):
        self.factory.clients.append(self)
        self.deferreds = deque()
        self.mensajes = {}
        self.sitio = None
        self.delayedCall = None
        self.peer = self.transport.getPeer()
        print "Nuevo cliente: %s:%d" % (self.peer.host, self.peer.port) #LOG
        print "Total: %d" % len(self.factory.clients)

    def connectionLost(self, reason):
        if self in self.factory.clients:
            self.sitio.online = False
            self.factory.clients.remove(self)
        else:
            print "El cliente ya fue eliminado."

    def process(self, line):

        if not line.startswith(':'):
            print "Error en mensaje: no empieza con :"  #EXC
        elif line[3] == '9':   # mensaje del G24 - Saludo inicial
            print "G24 dice: ", line
            ccc = line[5:8]
            print "SITIO", ccc
            # Verificar si ya hay un G24 registrado para ese sitio
            for c in self.factory.clients:
                if c.sitio and c.sitio.ccc == ccc:
                    print "%s ya estaba conectado. Borrando anterior." % ccc
                    c.transport.loseConnection()
                    self.factory.clients.remove(c)
                    break
            try:
                self.sitio = slaves[ccc]
                self.sitio.online = True
                self.sitio.transport = self
                self.canal_ocupado = False
            except Exception:
                print "El sitio %s no existe en la base de datos." % ccc
        else:
            # TODO: check LRC
            # si el LRC esta mal, repreguntar
            line = line + '\r\n'
            asciiFramer.processIncomingPacket(line, self.sendBack)

    def sendLine(self, line):
        # Si la linea ya viene con \r\n, se la quieto por que
        # sendLine se lo agrega.
        if line.endswith('\r\n'):
            line = line[:-2]
        LineOnlyReceiver.sendLine(self, line)

    def sendBack(self, response):
        unit_id = response.unit_id
        function_code = response.function_code
        sin_error = True
        # Cuando hay un error en Modbus, el codigo de funcion retornado
        # es el codigo orignal mas 80. 80 en hexa es 128 en decimal:
        if function_code > 128:
            function_code -= 128
            sin_error = False
        d = self.mensajes.get((unit_id, function_code))
        if d:
            # Se encontro una respuesta espera para unit_id, function_code
            del self.mensajes[unit_id, function_code]
            d.callback(response)
            if sin_error:
                robots[self.sitio.ccc][d.unit_id - 1].errores = 0
                slaves[self.sitio.ccc].online = True
            else:
                robots[self.sitio.ccc][d.unit_id - 1].errores += 1
        else:
            # Se recive una rta para una pregunta no hecha o ya respondida
            print "Error de RX:", self.sitio.ccc, unit_id, function_code

    def sendLineWithDeferred(self, line, unit_id, function_code):
        #if not robots[self.sitio.ccc][d.unit_id - 1].online:
        #    robot.cuenta_reintentos
        d = Deferred()
        d.line = line
        d.unit_id = unit_id
        d.function_code = function_code
        old = self.mensajes.get((unit_id, function_code))
        if old:
            print "Error de TX:", self.sitio.ccc, unit_id, function_code
            slaves[self.sitio.ccc].online = False
        self.mensajes[unit_id, function_code] = d
        self.sendLine(line)
        return d

class TModBusFactory(Factory):
    protocol = TModBus
    writeBuffer = {}    # clave prolocolo, valor triplete para ask_write_reg

    def stopFactory(self):
        pass

    def __init__(self):
        self.clients = []
