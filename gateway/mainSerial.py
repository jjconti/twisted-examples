'''
Gateway Modbus TCP a Modbus Seriel
'''
from line import *
from listenTCP import *
from constants import SITIOS
from pymodbus.server.async import ModbusServerFactory
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
from twisted.internet import reactor
from twisted.internet.serialport import SerialPort
from twisted.internet import reactor
import sys


# Servidor para clientes Modbus IP como Mango m2m

modbuses = {}
contexts = {}
for ccc,port in SITIOS.items():
    context = ModbusSlaveContext(d=AdminDataBlock('ed', ccc),
                           c=AdminDataBlock('sd', ccc),
                           i=AdminDataBlock('ea', ccc),
                           h=AdminDataBlock('re', ccc),
                           slave=port - 500,
                           sitio=ccc
                          )
    contexts[port - 500] = context
# Servidor Modbus IP administrativo | estado de sitios y robots

mbfactory = ModbusServerFactory(ModbusServerContext(contexts, single=False))
modbuses['aaa'] = mbfactory
reactor.listenTCP(500, mbfactory)

# No esperar a que se conecten los robots.
# Empezas a escuchar desde el principio
for ccc, port in SITIOS.items():
    if ccc not in modbuses.keys():
        mbfactory = ModbusServerFactory2(None) # None store
        #mbfactory.protocol.ccc = ccc
        mbfactory.ccc = ccc
        modbuses[ccc] = mbfactory
        if port != 500:
            reactor.listenTCP(port, mbfactory)
        print modbuses

# Interfaz administrativa por SSH

from twisted.conch import manhole, manhole_ssh
from twisted.cred import portal, checkers

def getManholeFactory(namespace, **passwords):
    realm = manhole_ssh.TerminalRealm()
    def getManhole(_): return manhole.Manhole(namespace)
    realm.chainedProtocolFactory.protocolFactory = getManhole
    p = portal.Portal(realm)
    p.registerChecker(
    checkers.InMemoryUsernamePasswordDatabaseDontUse(**passwords))
    f = manhole_ssh.ConchFactory(p)
    return f

reactor.listenTCP(2222, getManholeFactory(globals(), admin=''))

# Serial
factory = TModBusSerialFactory()
protocol = factory.buildProtocol(None)
#deviceName = "/dev/ttyUSB0"
deviceName = sys.argv[1]
print sys.argv[1]

port = SerialPort(protocol, deviceName, reactor)


# Que empiece la fiesta
reactor.run()
