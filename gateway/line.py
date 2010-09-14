from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory
from twisted.python import log
from twisted.python.logfile import DailyLogFile

from constants import LOGDIR
from config import slaves, robots
from collections import deque

class MyObserver(log.FileLogObserver):

    timeFormat = '%Y-%m-%d %H:%M:%S'

log.startLoggingWithObserver(MyObserver(DailyLogFile('log.txt', LOGDIR)).emit)

from listenTCP import ModbusAsciiFramer, ClientDecoder


#from twittytwister import twitter
#twitclient = twitter.Twitter('kimera_status', 'LiCe2010')
class TModBus(LineOnlyReceiver):

    def get_ccc(self):
        try:
            return self.sitio.ccc
        except:
            return ' - '

    def lineReceived(self, line):
        try:
            self.process(line)
        except Exception as e:
            log.msg("Error al procesar mensaje desde el G24" + str(e), system=self.get_ccc())

    def connectionMade(self):
        self.factory.clients.append(self)
        self.deferreds = deque()
        self.mensajes = {}
        self.sitio = None
        self.delayedCall = None
        self.peer = self.transport.getPeer()
        log.msg("Nuevo cliente: %s:%d" % (self.peer.host, self.peer.port), system=' - ')
        log.msg("Total: %d" % len(self.factory.clients), system=' - ')

    def connectionLost(self, reason):
        if self in self.factory.clients:
            try:
                self.sitio.online = False
                #twitclient.update('Se desconecto el cliente %s' % self.sitio.ccc)
            except:
                pass
            self.factory.clients.remove(self)
        else:
            log.msg("El cliente ya fue eliminado.", system=self.get_ccc())

    def process(self, line):

        if not line.startswith(':'):
            log.msg("Error en mensaje: no empieza con :", system=self.get_ccc())
        elif line[3] == '9':   # mensaje del G24 - Saludo inicial
            log.msg("G24 dice: %s" % line, system=self.get_ccc())
            ccc = line[5:8]
            log.msg("SITIO %s" % ccc, system=self.get_ccc())
            #twitclient.update('Se ha conectado el sitio %s' % ccc)
            # Verificar si ya hay un G24 registrado para ese sitio
            for c in self.factory.clients:
                if c.sitio and c.sitio.ccc == ccc:
                    log.msg("%s ya estaba conectado. Borrando anterior." % ccc, system=self.get_ccc())
                    c.transport.loseConnection()
                    self.factory.clients.remove(c)
                    break
            try:
                self.sitio = slaves[ccc]
                self.sitio.online = True
                self.sitio.transport = self
                self.canal_ocupado = False
            except Exception:
                log.msg("El sitio %s no existe en la base de datos." % ccc, system=self.get_ccc())
        else:
            # TODO: check LRC
            # si el LRC esta mal, repreguntar
            line = line + '\r\n'
            asciiFramer = ModbusAsciiFramer(ClientDecoder())
            asciiFramer.processIncomingPacket(line, self.sendBack)

    def sendLine(self, line):
        # Si la linea ya viene con \r\n, se la quieto por que
        # sendLine se lo agrega.
        log.msg("=> %s" % line, system=self.get_ccc())
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
            log.msg("Error de RX: robot: %s -  funcion: %s"
                    % (unit_id, function_code), system=self.get_ccc())

    def sendLineWithDeferred(self, line, unit_id, function_code):
        #if not robots[self.sitio.ccc][d.unit_id - 1].online:
        #    robot.cuenta_reintentos
        d = Deferred()
        d.line = line
        d.unit_id = unit_id
        d.function_code = function_code
        old = self.mensajes.get((unit_id, function_code))
        if old:
            log.msg("Error de TX: robot: %s - funcion: %s"
                    % (unit_id, function_code), system=self.get_ccc())
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
