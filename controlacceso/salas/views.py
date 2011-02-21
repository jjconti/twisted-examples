from models import *
from django.shortcuts import render_to_response

def sala_info(request, salaid):
    sala = Sala.objects.get(id=salaid)
    registros = [r.estado() for r in sala.registroacceso_set.all()]
    return render_to_response('sala.html', {'registros': registros, 'sala': sala})            
    
def salas_list(request):
    salas_objects = Sala.objects.all()
    salas = []
    for sala in salas_objects:
        estado = sala.estado()
        salas.append({'id': sala.id, 'ccc': sala.ccc, 'numero': sala.numero_de_sala, 'rfid': estado.rfid, 
                    'puerta_abierta': estado.puerta_abierta, 'movimiento': estado.movimiento, 'color': estado.get_color()})
    return render_to_response('salas.html', {'salas': salas})
