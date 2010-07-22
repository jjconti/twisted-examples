ID = 41 # identidad del dispositivo
RD = 42 # lectura de registros
WR = 43 # escritura de un registro
RR = 44 # lectura de un registro
WB = 45 # escritura de una bobina
RB = 46 # lectura de una bobina

VALID_FUNCS = [ID, RD, WR, WB]

LR = 00 # control de errores

NOERR = 00
ERRREG = 91
ERRVAL = 92

LOGDIR = '/home/juanjo/python/twisted/teco/logs'

IDLE, WAITING = range(2)

ROOT_PATH = '/home/juanjo/python/twisted/teco/'
#ROOT_PATH = 'D:\escr\line'
