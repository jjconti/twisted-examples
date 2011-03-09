from models import *
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

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

#@login_required
def salas_list(request, minutos=None, alertas=None, reconocidas=None):
    salas_objects = Sala.objects.all()
    salas = []
    for sala in salas_objects:
        estado = sala.estado()
        if estado:
            try:
                persona = Persona.objects.get(rfid=estado.rfid)
            except Persona.DoesNotExist:
                persona = {'nombre': 'Desconocido', 'legajo': ' - '}
            if minutos == 0:
                masAntiguoQue = True
            else:
                masAntiguoQue = estado.registro.masAntiguoQue(minutos)
            esAlerta = estado.registro.esAlerta()
            reconocido = estado.registro.reconocido
            salas.append({'id': sala.id, 'ccc': sala.ccc, 'nombre': sala.nombre, 'numero': sala.numero_de_sala, 'rfid': estado.rfid, 
                        'puerta_abierta': estado.puerta_abierta, 'movimiento': estado.movimiento, 'color': estado.setTipoYObtenerColor(),
                        'persona': persona, 'timestamp': estado.registro.timestamp, 'registro': estado.registro, 'masAntiguoQue': masAntiguoQue,
                        'esAlerta': esAlerta, 'reconocido': reconocido, 'alerta_verde': estado.esAlertaVerde()})
    salas = [s for s in salas if s['masAntiguoQue']]
    if alertas == 'soloalertas':
        salas = [s for s in salas if s['esAlerta']]
    if reconocidas == 'noreconocidas':
        salas = [s for s in salas if not s['reconocido']]
    return render_to_response('salas.html', {'salas': salas, 'minutos': minutos, 'alertas': alertas, 'reconocidas': reconocidas}, context_instance=RequestContext(request))

def reconocido(request, registroid, valor):
    try:
        registro = RegistroAcceso.objects.get(id=registroid)
    except RegistroAcceso.DoesNotExist:
        return redirect('/')

    if valor == 'si':
        registro.reconocido = True
        registro.save()
    elif valor == 'no':
        registro.reconocido = False
        registro.save()
    print valor
    
    referrer = request.META.get('HTTP_REFERER')

    if referrer:
        return redirect(referrer)
    return redirect('/')
    
def registrar_salida(request, registroid):
    try:
        registro = RegistroAcceso.objects.get(id=registroid)
    except RegistroAcceso.DoesNotExist:
        return redirect('/')
    
    nuevoRegistro = RegistroAcceso(sala=registro.sala, rfid='', puerta_abierta=False, movimiento=False)
    nuevoRegistro.save()

    referrer = request.META.get('HTTP_REFERER')

    if referrer:
        return redirect(referrer)
    return redirect('/')  

def persona_info(request, personaid):
    try:
        persona = Persona.objects.get(id=personaid)
    except Persona.DoesNotExist:
        persona = {'nombre': 'Desconocido', 'legajo': ' - '}
    return render_to_response('persona.html', {'persona': persona})       
