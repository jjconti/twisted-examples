from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.server.async import ModbusServerFactory, ModbusProtocol
from pymodbus.transaction import ModbusSocketFramer, ModbusAsciiFramer
from pymodbus.factory import ServerDecoder, ClientDecoder
from twisted.internet.defer import Deferred
from config import slaves, robots

socketFramer = ModbusSocketFramer(ServerDecoder())
asciiFramer = ModbusAsciiFramer(ClientDecoder())


class AdminDataBlock(ModbusSequentialDataBlock):
    '''
    Representa si los robots estan o no en linea.

    dir 0: G24
    dir 1....: robots
    '''

    def __init__(self, tipo, sitio, address=None, values=None):
        '''
        Initializes the datastore
        '''
        self.tipo = tipo
        self.sitio = sitio
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
                if slaves[self.sitio].errores > 10:
                    slaves[self.sitio].online = False
                else:
                    slaves[self.sitio].online = True
                res.append(slaves[self.sitio].online)
                for r in robots[self.sitio]:
                    if r.errores > 2:
                        r.online = False
                    else:
                        r.online = True
                    # si el sitio no esta on line, tampoco el robot
                    res.append(slaves[self.sitio].online and r.online)
            d = Deferred()
        except Exception,e:
            raise e
        d.callback(res[address:address+count])
        return d    # cambair esto usando maybeDeferred mas afuera

class ModbusProtocol2(ModbusProtocol):
    def execute(self, request):
        asciiFramer = ModbusAsciiFramer(ClientDecoder())
        packet = asciiFramer.buildPacket(request)
        # Send like to slave using ascii ModbusServerFactory2
        response = slaves[self.factory.ccc].transport.sendLineWithDeferred(
                                packet, request.unit_id,request.function_code)
        response.addCallback(self._execute, request)

class ModbusServerFactory2(ModbusServerFactory):
    protocol = ModbusProtocol2


