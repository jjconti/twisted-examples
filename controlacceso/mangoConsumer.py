import MySQLdb
import sys
import time
sys.path.append('/home/kimera/')
from salas.models import RegistroAcceso, Sala

conn = MySQLdb.connect (host = "localhost",
                           user = "root",
                           passwd = "toor",
                           db = "mango")


RFID = 340
PUERTA = 334
MOVIMIENTO = 335

#while True:
c = conn.cursor()
print "pit!"
#time.sleep(10)
data = {}
for point in (RFID, PUERTA, MOVIMIENTO):
    c.execute('select pointValue,ts from pointValues where dataPointId = %d order by ts desc limit 1;' % point)
    value, ts = c.fetchone()
    data[point] = value, ts

lastInSystem = RegistroAcceso.objects.latest()

if lastInSystem.rfid != str(int(data[RFID][0])) or \
   lastInSystem.puerta_abierta != bool(data[PUERTA][0]) or \
   lastInSystem.movimiento != bool(data[MOVIMIENTO][0]):
        sala = Sala.objects.get(id=1)
        registro = RegistroAcceso(sala=sala, rfid=str(int(data[RFID][0])), puerta_abierta=bool(data[PUERTA][0]), movimiento=bool(data[MOVIMIENTO][0]))
        registro.save()
        print registro

c.close()

conn.close()
#for ts, puerta, movimiento, rfid in row:
#    if actual != latest:
#        registro = RegistroAcceso(*)
#        registro.save()
