from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Factory
from twisted.internet import reactor
from twisted.python import log
from twisted.python.logfile import DailyLogFile

from constants import LOGDIR, IDLE, WAITING
from config import slaves, robots

from collections import deque
log.startLogging(DailyLogFile('log.txt', LOGDIR))

from listenTCP import asciiFramer

class TModBus(LineOnlyReceiver):

    def lineReceived(self, line):
        print "Linea cruda recibida"
        self.process(line)

    def connectionMade(self):
        self.factory.clients.append(self)
        self.deferreds = deque()
        self.state = IDLE
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
            #
            # verificar si ya hay un G24 registrado para ese sitio
            #
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
            # check LRC
            # si el LRC esta mal, repreguntar
            line = line + '\r\n'
            asciiFramer.processIncomingPacket(line, self.sendBack)

    def sendLine(self, line):
        # si la linea ya viene con \r\n, se la quieto por que
        # sendLine se lo agrega.
        if line.endswith('\r\n'):
            line = line[:-2]
        LineOnlyReceiver.sendLine(self, line)

    def sendBack(self, response):
        #packet = socketFramer.buildPacket(response)
        print "Se recive un mensaje del G24"
        if self.deferreds:
            d = self.deferreds.popleft()
            d.callback(response)
            print "Se responde al Mango"
            # Poner a 0 los errores del robots
            robots[self.sitio.ccc][d.unit_id - 1].errores = 0
            # Si hay promesas en la cola, sacar y mandar linea
            if self.deferreds:
                print "Hay mensajes encolados."
                # Hay mensajes para seguir enviado
                self.delayedCall.reset()
                print "Timeout reseteado"
                self.sendLine(self.deferreds[0].line)
                print "Mensaje enviado"
            else:
                print "Canal vuelve a estado libre"
                self.state = IDLE
        else:
            self.state = IDLE
        # enviar a Mango

    def sendLineWithDeferred(self, line, unit_id):
        print "Mango manda un mensaje"
        d = Deferred()
        d.line = line
        d.unit_id = unit_id
        self.deferreds.append(d)
        if self.state == IDLE:
            print "Canal libre"
            self.state = WAITING
            self.sendLine(line)
            print "Mensaje mandado"
            self.delayedCall = reactor.callLater(10, self.checkOcupacionCanal,
                                                 unit_id)
        else:
            print "Esta ocuapdo el canal, esperando..."
        return d

    def checkOcupacionCanal(self, unit_id):
        "Time out de 10 segundos"
        if self.state == WAITING:
            print "El canal estaba ocupado"
            self.deferreds.popleft()
            print "Se descarta el mensaje que estaba en la cabeza de la cola"
            robots[self.sitio.ccc][unit_id - 1].errores += 1
            # Si hay peticiones encoladas, enviar
            if self.deferreds:
                print "Hay mas elementos en la cola"
                #self.sendLine(self.deferreds.popleft().line)
                self.sendLine(self.deferreds[0].linea)
                print "Vuelvo a poner el reloj a 10 segundos"
                self.delayedCall = reactor.callLater(10,
                                           self.checkOcupacionCanal, unit_id)
            else:
                self.state = IDLE
                print "Liberando el canal ", self.sitio.ccc

class TModBusFactory(Factory):
    protocol = TModBus
    writeBuffer = {}    # clave prolocolo, valor triplete para ask_write_reg

    def stopFactory(self):
        pass

    def __init__(self):
        self.clients = []
