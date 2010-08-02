'''
Gateway Modbus TCP a Modbus Seriel
'''
from line import *
from listenTCP import *
from constants import SITIOS
from pymodbus.server.async import ModbusServerFactory
from pymodbus.datastore import ModbusServerContext, ModbusSlaveContext
from twisted.internet import reactor

# Servidor para los G24 que hablan Modbus Serie ASCII
factory = TModBusFactory()
reactor.listenTCP(9007, factory)
reactor.listenTCP(8007, factory)
##########################################################

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
for ccc,port in SITIOS.items():
    if ccc not in modbuses.keys():
        mbfactory = ModbusServerFactory2(None) # None store
        mbfactory.protocol.ccc = ccc
        modbuses[ccc] = mbfactory
        if port != 500:
            reactor.listenTCP(port, mbfactory)

# Que empiece la fiesta
reactor.run()
