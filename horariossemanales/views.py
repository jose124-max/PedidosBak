from django.shortcuts import render
from .models import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from Sucursal.models import Sucursales
from django.views import View
from django.db import transaction
from django.http import JsonResponse

@method_decorator(csrf_exempt, name='dispatch')
class CrearHorarioSucursal(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            nombreh = request.POST.get('nombreh', '')
            hordescripcion = request.POST.get('hordescripcion', '')
            idsucursal = request.POST.get('idsucursal', '')
            detalle = json.loads(request.POST.get('detalle', '[]'))
            sucursal= Sucursales.objects.get(id_sucursal=idsucursal)
            sucursal.id_horarios=Horariossemanales.objects.create(
                nombreh=nombreh,
                hordescripcion=hordescripcion,
                tipohorario='A',
            )
            sucursal.save()
            for det in detalle['Detalles']:
                id_horarios = sucursal.id_horarios
                print(id_horarios)
                print(f"hla uwu")
                dia = det['dia']
                hora_inicio = det['hora_inicio']
                hora_fin=det['hora_fin']
                DetalleHorariosSemanales.objects.create(
                    id_horarios = id_horarios,
                    dia =dia,
                    horainicio = hora_inicio,
                    horafin = hora_fin
                )
            return JsonResponse({'mensaje': 'Horario agregado con exito'})
        
        except Exception as e:
            print( str(e))
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class DetallesHorarioView(View):
    def get(self, request, *args, **kwargs):
        try:
            id_horario = kwargs.get('id_horario')
            detalles = DetalleHorariosSemanales.objects.filter(id_horarios=id_horario)
            detalles_list = [{'dia': nombre_dia(detalle.dia), 'hora_inicio': detalle.horainicio, 'hora_fin': detalle.horafin} for detalle in detalles]
            return JsonResponse({'detalles': detalles_list})
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
def nombre_dia(dia):
    if dia=='L':
        return 'Lunes'
    if dia=='M':
        return 'Martes'
    if dia=='X':
        return 'Miercoles'
    if dia=='J':
        return 'Jueves'
    if dia=='V':
        return 'Viernes'
    if dia=='S':
        return 'Sabado'
    if dia=='D':
        return 'Domingo'
