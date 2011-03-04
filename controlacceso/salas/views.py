from models import *
from django.shortcuts import render_to_response

def index(request):
    return render_to_response('index.html', {})

def sala_info(request, salaid):
    sala = Sala.objects.get(id=salaid)
    registros = [r.estado() for r in sala.registroacceso_set.all()]
    for r in registros:
        try:
            r.persona = Persona.objects.get(rfid=r.rfid)
        except Persona.DoesNotExist:
            r.persona = {'nombre': 'Desconocido', 'legajo': ' - '}
    return render_to_response('sala.html', {'registros': registros, 'sala': sala})            
    
def salas_list(request, minutos=None):
    salas_objects = Sala.objects.all()
    salas = []
    for sala in salas_objects:
        estado = sala.estado()
        if estado:
            try:
                persona = Persona.objects.get(rfid=estado.rfid)
            except Persona.DoesNotExist:
                persona = {'nombre': 'Desconocido', 'legajo': ' - '}
            if minutos is None:
                masAntiguoQue = True
            else:
                masAntiguoQue = estado.registro.masAntiguoQue(minutos)
                print masAntiguoQue
            salas.append({'id': sala.id, 'ccc': sala.ccc, 'nombre': sala.nombre, 'numero': sala.numero_de_sala, 'rfid': estado.rfid, 
                        'puerta_abierta': estado.puerta_abierta, 'movimiento': estado.movimiento, 'color': estado.get_color(),
                        'persona': persona, 'timestamp': estado.registro.timestamp, 'masAntiguoQue': masAntiguoQue })
    salas = [s for s in salas if s['masAntiguoQue']]
    print salas
    return render_to_response('salas.html', {'salas': salas})

def persona_info(request, personaid):
    try:
        persona = Persona.objects.get(id=personaid)
    except Persona.DoesNotExist:
        persona = {'nombre': 'Desconocido', 'legajo': ' - '}
    return render_to_response('persona.html', {'persona': persona})       
