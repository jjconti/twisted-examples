LR = 00 # control de errores

NOERR = 00
ERRREG = 91
ERRVAL = 92

LOGDIR = 'logs'

IDLE, WAITING = range(2)

ROOT_PATH = '/home/juanjo/python/twisted/teco/'
#ROOT_PATH = 'D:\escr\line'

# SITIOS es un diccionario donde la clave es el CCC y el valor el puerto
# en el que pregunta el Mango m2m u otro cliente Modbus.
SITIOS = {'SFE': 504}
# ROBOTS es un diccionario donde la clave es el CCC y el valor la cantidad
# de robots que tiene un sitio.
ROBOTS = {'SFE': 2}
