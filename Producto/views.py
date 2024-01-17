from django.http import JsonResponse
from django.db.models import Max, ExpressionWrapper, IntegerField
from django.views import View
from .models import *
from Login.models import Cuenta
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from PIL import Image, UnidentifiedImageError
from Login.models import Cuenta
from Combos.models import Combo
from django.db import transaction
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator,EmptyPage
from horariossemanales.models import Horariossemanales
import json
from django.db.models import Max, F
from django.core.serializers import serialize
from decimal import Decimal

@method_decorator(csrf_exempt, name='dispatch')
class CrearTipoProducto(View):
    #@method_decorator(login_required)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
            #    return JsonResponse({'error': 'No tienes permisos para crear un tipo de producto'}, status=403)
            data = json.loads(request.body)
            tp_nombre = data.get('tp_nombre')
            descripcion = data.get('descripcion')

            tipo_producto = TiposProductos.objects.create(tpnombre=tp_nombre, descripcion=descripcion,sestado=1)
            tipo_producto.save()

            return JsonResponse({'mensaje': 'Tipo de producto creado con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class tipoProductoExist(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            tpnombre = data.get('tpnombre')

            obt=TiposProductos.objects.filter(tpnombre=tpnombre).first()
            if obt is not None:
                return JsonResponse({'mensaje': '1'})
            return JsonResponse({'mensaje': '0'})
        except Exception as e:
            return JsonResponse({'error xd': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class CategoriaExist(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            catnombre = data.get('catnombre')

            obt=Categorias.objects.filter(catnombre=catnombre).first()
            if obt is not None:
                return JsonResponse({'mensaje': '1'})
            return JsonResponse({'mensaje': '0'})
        except Exception as e:
            return JsonResponse({'error xd': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class CrearCategoria(View):
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
                #return JsonResponse({'error': 'No tienes permisos para crear una categoría'}, status=403)

            id_tipo_producto = request.POST.get('id_tipoproducto')
            cat_nombre = request.POST.get('catnombre')
            descripcion = request.POST.get('descripcion')

            imagen_archivo = request.FILES.get('imagencategoria')
            image_64_encode=None
            if imagen_archivo:
                try:
                    image_read = imagen_archivo.read()
                    image_64_encode = base64.b64encode(image_read)
                    image_encoded = image_64_encode.decode('utf-8')
                except UnidentifiedImageError as img_error:
                    return JsonResponse({'error': f"Error al procesar imagen: {str(img_error)}"}, status=400)

            tipo_producto = TiposProductos.objects.get(id_tipoproducto=id_tipo_producto)

            categoria = Categorias(
                id_tipoproducto=tipo_producto,
                catnombre=cat_nombre,
                descripcion=descripcion,
                imagencategoria=image_64_encode,
                sestado=1
            )
            categoria.save()

            return JsonResponse({'mensaje': 'Categoría creada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class ListaTiposYCategorias(View):
    def get(self, request, *args, **kwargs):
        try:
            tipos_productos = TiposProductos.objects.filter(sestado=1)
            data = []

            for tipo_producto in tipos_productos:
                categorias = Categorias.objects.filter(id_tipoproducto=tipo_producto)
                categorias_data = []

                for categoria in categorias:
                    imagencategoria = categoria.imagencategoria
                    imagencategoria_base64 = None

                    if imagencategoria:
                        imagencategoria_base64 = self.convertir_imagen_a_base64(imagencategoria)

                    categoria_data = {
                        'id_categoria': categoria.id_categoria,
                        'imagencategoria': imagencategoria_base64,
                        'catnombre': categoria.catnombre,
                        'descripcion': categoria.descripcion
                    }

                    categorias_data.append(categoria_data)

                tipo_producto_data = {
                    'id_tipoproducto': tipo_producto.id_tipoproducto,
                    'tpnombre': tipo_producto.tpnombre,
                    'descripcion': tipo_producto.descripcion,
                    'sestado':tipo_producto.sestado,
                    'categorias': categorias_data
                }

                data.append(tipo_producto_data)

            return JsonResponse({'tipos_y_categorias': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def convertir_imagen_a_base64(self, imagen):
        return base64.b64encode(imagen).decode('utf-8') if imagen else None
@method_decorator(csrf_exempt, name='dispatch')
class ListaTiposProductos(View):
    def get(self, request, *args, **kwargs):
        try:
            tipos_productos = TiposProductos.objects.filter(sestado=1)
            data = []
            for tipo_producto in tipos_productos:
                tipo_producto_data = {
                    'id_tipoproducto': tipo_producto.id_tipoproducto,
                    'tpnombre': tipo_producto.tpnombre,
                    'descripcion': tipo_producto.descripcion,
                }

                data.append(tipo_producto_data)

            return JsonResponse({'tipos_productos': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')
class ListaCategorias(View):
    def get(self, request, *args, **kwargs):
        try:
            categorias = Categorias.objects.filter(sestado=1)
            data = []

            for categoria in categorias:
                imagencategoria = categoria.imagencategoria
                imagencategoria_base64 = None

                if imagencategoria:
                    try:
                        byteImg = base64.b64decode(imagencategoria)
                        imagencategoria_base64 = base64.b64encode(byteImg).decode('utf-8')
                    except Exception as img_error:
                        print(f"Error al procesar imagen: {str(img_error)}")

                tipo_producto_data = {
                    'id_tipoproducto': categoria.id_tipoproducto.id_tipoproducto,
                }

                categoria_data = {
                    'id_categoria': categoria.id_categoria,
                    'imagencategoria': imagencategoria_base64,
                    'catnombre': categoria.catnombre,
                    'descripcion': categoria.descripcion,
                    'id_tipoproducto': tipo_producto_data
                }

                data.append(categoria_data)

            return JsonResponse({'categorias': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
#@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class EditarTipoProducto(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
                #return JsonResponse({'error': 'No tienes permisos para crear editar un tipo de producto'}, status=403)
            tipo_producto_id = kwargs.get('tipo_producto_id') 
            tipo_producto = TiposProductos.objects.get(id_tipoproducto=tipo_producto_id)
            tipo_producto.tpnombre = request.POST.get('tpnombre', tipo_producto.tpnombre)
            tipo_producto.descripcion = request.POST.get('descripcion', tipo_producto.descripcion)
            if(request.POST.get('sestado')):
                tipo_producto.sestado = request.POST.get('sestado')
            tipo_producto.save()

            return JsonResponse({'mensaje': 'Tipo de producto editado con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
#@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class EditarCategoria(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
                #return JsonResponse({'error': 'No tienes permisos para crear editar una categoría'}, status=403)
            categoria_id = kwargs.get('categoria_id')
            categoria = Categorias.objects.get(id_categoria=categoria_id)
            imagencategoria = request.FILES.get('imagencategoria')
            nombre= request.POST.get('catnombre')
            if(nombre):
                categoria.catnombre =nombre
            descripcion = request.POST.get('descripcion')
            if(descripcion):
                categoria.descripcion=descripcion
            estado= request.POST.get('sestado')
            if(estado):
                categoria.sestado =estado
            tipo= request.POST.get('id_tipoproducto', categoria.id_tipoproducto.id_tipoproducto)
            if tipo:
                categoria.id_tipoproducto=TiposProductos.objects.get(id_tipoproducto=tipo)
            if imagencategoria:
                try:
                    image_read = imagencategoria.read()
                    image_64_encode = base64.b64encode(image_read)
                    image_encoded = image_64_encode.decode('utf-8')
                    categoria.imagencategoria=image_64_encode
                except UnidentifiedImageError as img_error:
                    return JsonResponse({'error': f"Error al procesar imagen: {str(img_error)}"}, status=400)
            
            categoria.save()
            return JsonResponse({'mensaje': 'Categoría editada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class CrearUnidadMedida(View):
    #@method_decorator(login_required)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
           #if cuenta.rol != 'S':
            #    return JsonResponse({'error': 'No tienes permisos para crear una unidad de medida'}, status=403)
            data = json.loads(request.body)
            nombre_um = data.get('nombre_um')
            unidad_medida = UnidadMedida.objects.create(nombreum=nombre_um,sestado=1)
            unidad_medida.save()
            return JsonResponse({'mensaje': 'Unidad de medida creada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')


class ListarUnidadesMedida(View):
    def get(self, request, *args, **kwargs):
        try:
            unidades_medida = UnidadMedida.objects.filter(sestado=1)
            data = []

            for unidad in unidades_medida:
                unidad_data = {
                    'id_um': unidad.idum,
                    'nombre_um': unidad.nombreum,
                }

                data.append(unidad_data)

            return JsonResponse({'unidades_medida': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
@method_decorator(csrf_exempt, name='dispatch')


class CrearProducto(View):
    #@method_decorator(login_required)
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
            #    return JsonResponse({'error': 'No tienes permisos para crear un producto'}, status=403)
            id_categoria = request.POST.get('id_categoria')
            id_um = request.POST.get('id_um')
            imagen_p = request.FILES.get('imagen_p')
            puntosp = request.POST.get('puntos_p')
            nombreproducto = request.POST.get('nombre_producto')
            descripcionproducto = request.POST.get('descripcion_producto')
            preciounitario = request.POST.get('precio_unitario')
            iva = request.POST.get('iva')
            ice = request.POST.get('ice')
            irbpnr = request.POST.get('irbpnr')
            image_64_encode=None
            if imagen_p:
                try:
                    image_read = imagen_p.read()
                    image_64_encode = base64.b64encode(image_read)
                    image_encoded = image_64_encode.decode('utf-8')
                except UnidentifiedImageError as img_error:
                    return JsonResponse({'error': f"Error al procesar imagen: {str(img_error)}"}, status=400)

            categoria = Categorias.objects.get(id_categoria=id_categoria)
            unidad_medida = UnidadMedida.objects.get(idum=id_um)

            producto = Producto.objects.create(
                id_categoria=categoria,
                id_um=unidad_medida,
                imagenp=image_64_encode,
                puntosp=puntosp,
                codprincipal=obtener_siguiente_codprincipal(),
                nombreproducto=nombreproducto,
                descripcionproducto=descripcionproducto,
                preciounitario=preciounitario,
                iva=iva,
                ice=ice,
                irbpnr=irbpnr,
                sestado = 1
            )
            producto.save()

            return JsonResponse({'mensaje': 'Producto creado con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
#@method_decorator(login_required, name='dispatch')
class EditarUnidadMedida(View):
    @transaction.atomic
    def post(self, request, unidad_id, *args, **kwargs):
        try:
            #cuenta = Cuenta.objects.get(nombreusuario=request.user.username)
            #if cuenta.rol != 'S':
                #return JsonResponse({'error': 'No tienes permisos para editar una unidad de medida'}, status=403)

            unidad = UnidadMedida.objects.get(idum=unidad_id)

            unidad.nombreum = request.POST.get('nombreum', unidad.nombreum)
            unidad.sestado = request.POST.get('sestado', unidad.sestado)
            unidad.save()

            return JsonResponse({'mensaje': 'Unidad de medida editada con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
#@method_decorator(login_required, name='dispatch')
class EditarProducto(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            producto_id = kwargs.get('producto_id')
            producto = Producto.objects.get(id_producto=producto_id)
            producto.id_categoria = Categorias.objects.get(id_categoria=request.POST.get('id_categoria', producto.id_categoria.id_categoria))
            producto.id_um = UnidadMedida.objects.get(idum=request.POST.get('id_um', producto.id_um.idum))
            producto.puntosp = request.POST.get('puntosp', producto.puntosp)
            producto.codprincipal = request.POST.get('codprincipal', producto.codprincipal)
            producto.nombreproducto = request.POST.get('nombreproducto', producto.nombreproducto)
            producto.descripcionproducto = request.POST.get('descripcionproducto', producto.descripcionproducto)
            producto.preciounitario = request.POST.get('preciounitario', producto.preciounitario)
            producto.iva = request.POST.get('iva', producto.iva)
            producto.ice = request.POST.get('ice', producto.ice)
            producto.irbpnr = request.POST.get('irbpnr', producto.irbpnr)

            imagen_producto = request.FILES.get('imagenp')
            if imagen_producto:
                try:
                    image_read = imagen_producto.read()
                    image_64_encode = base64.b64encode(image_read)
                    image_encoded = image_64_encode.decode('utf-8')
                    producto.imagenp = image_64_encode
                except Exception as img_error:
                    return JsonResponse({'error': f"Error al procesar imagen: {str(img_error)}"}, status=400)

            producto.save()

            return JsonResponse({'mensaje': 'Producto editado con éxito'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
<<<<<<< HEAD
=======

>>>>>>> a713a27e1e933ca1072f92d5c4eb79c6ee7cb914
@method_decorator(csrf_exempt, name='dispatch')
class CrearComponente(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
<<<<<<< HEAD
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            costo = request.POST.get('costo')
            tipo = request.POST.get('tipo')
            id_um = request.POST.get('id_um')
            id_categoria = request.POST.get('id_categoria')
            cantidadpadre = Decimal(request.POST.get('cantidad', 0))

            # Verificar que la unidad de medida exista
            unidad_medida = UnidadMedida.objects.get(idum=id_um)
            categoria = Categorias.objects.get(id_categoria=id_categoria)

            if tipo == 'N':
                componente = Componente.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    costo=costo,
                    tipo=tipo,
                    id_um=unidad_medida,
                    id_categoria=categoria,
                    sestado=1
                )

            if tipo == 'F' and cantidadpadre > 0:
                detalle_comp = json.loads(request.POST.get('detalle_comp', '[]'))
                componente = Componente.objects.create(
                    nombre=nombre,
                    descripcion=descripcion,
                    costo=costo,
                    tipo=tipo,
                    id_um=unidad_medida,
                    id_categoria=categoria,
                    sestado=1
                )
                ensamblecomponente = EnsambleComponente.objects.create(
                    id_componentepadre=componente,
                    padrecantidad=cantidadpadre,
                    id_umpadre=unidad_medida  # Ajusta esta línea según tu lógica
                )
                for detalle_data in detalle_comp:
                    componente_hijo = Componente.objects.get(id_componente=detalle_data['id'])
                    um = componente_hijo.id_um
                    detalleensamblecomponente = DetalleEnsambleComponente.objects.create(
                        id_ensamblec=ensamblecomponente,
                        id_componentehijo=componente_hijo,
                        cantidadhijo=detalle_data['cantidad'],
                        id_umhijo=um
                    )

            return JsonResponse({'mensaje': 'Componente creado con éxito'})

=======
            data = json.loads(request.body)

            nombre = data.get('nombre')
            descripcion = data.get('descripcion')
            costo = data.get('costo')
            tipo = data.get('tipo')
            id_um = data.get('id_um')

            unidad_medida = UnidadMedida.objects.get(idum=id_um)

            componente = Componente.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                costo=costo,
                tipo=tipo,
                id_um=unidad_medida
            )

            return JsonResponse({'mensaje': 'Componente creado con éxito', 'id_componente': componente.id_componente})
>>>>>>> a713a27e1e933ca1072f92d5c4eb79c6ee7cb914
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class ListarComponentes(View):
    def get(self, request, *args, **kwargs):
        try:
<<<<<<< HEAD
            # Obtener todos los componentes
            componentes = Componente.objects.all()

            # Convertir los componentes a formato JSON
            lista_componentes = []
            

            for componente in componentes:
                tipo_producto_data = {
                    'id_categoria': componente.id_categoria.id_categoria,
                    'catnombre': componente.id_categoria.catnombre,
                }
=======
            componentes = Componente.objects.all()

            lista_componentes = []
            for componente in componentes:
>>>>>>> a713a27e1e933ca1072f92d5c4eb79c6ee7cb914
                componente_data = {
                    'id_componente': componente.id_componente,
                    'nombre': componente.nombre,
                    'descripcion': componente.descripcion,
<<<<<<< HEAD
                    'costo': '$'+str(componente.costo).replace('€', ''),
                    'tipo': componente.tipo,
                    'id_um': componente.id_um.idum,
                    'id_categoria': tipo_producto_data,
=======
                    'costo': str(componente.costo),
                    'tipo': componente.tipo,
                    'id_um': componente.id_um.idum,
>>>>>>> a713a27e1e933ca1072f92d5c4eb79c6ee7cb914
                    'nombre_um': componente.id_um.nombreum,
                }

                lista_componentes.append(componente_data)

<<<<<<< HEAD
            # Devolver la lista de componentes en formato JSON
            return JsonResponse({'componentes': lista_componentes})
        except Exception as e:
            # Manejar errores aquí
=======
            return JsonResponse({'componentes': lista_componentes})
        except Exception as e:
>>>>>>> a713a27e1e933ca1072f92d5c4eb79c6ee7cb914
            return JsonResponse({'error': str(e)}, status=500)
        

@method_decorator(csrf_exempt, name='dispatch')
class EditarComponente(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
<<<<<<< HEAD
            # Obtener el ID del componente a editar de los argumentos de la URL
            id_componente = kwargs.get('id_componente')

            # Obtener el componente a editar
            componente = Componente.objects.get(id_componente=id_componente)

            # Obtener datos del cuerpo de la solicitud
            data = json.loads(request.body)

            # Actualizar los datos del componente
=======
            id_componente = kwargs.get('id_componente')

            componente = Componente.objects.get(id_componente=id_componente)

            data = json.loads(request.body)

>>>>>>> a713a27e1e933ca1072f92d5c4eb79c6ee7cb914
            componente.nombre = data.get('nombre', componente.nombre)
            componente.descripcion = data.get('descripcion', componente.descripcion)
            componente.costo = data.get('costo', componente.costo)
            componente.tipo = data.get('tipo', componente.tipo)

<<<<<<< HEAD
            # Verificar que la unidad de medida exista
=======
>>>>>>> a713a27e1e933ca1072f92d5c4eb79c6ee7cb914
            id_um = data.get('id_um')
            unidad_medida = UnidadMedida.objects.get(idum=id_um)
            componente.id_um = unidad_medida

<<<<<<< HEAD
            # Guardar los cambios
=======
>>>>>>> a713a27e1e933ca1072f92d5c4eb79c6ee7cb914
            componente.save()

            return JsonResponse({'mensaje': 'Componente editado con éxito', 'id_componente': componente.id_componente})
        except Componente.DoesNotExist:
            return JsonResponse({'error': 'Componente no encontrado'}, status=404)
        except UnidadMedida.DoesNotExist:
            return JsonResponse({'error': 'Unidad de medida no encontrada'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


<<<<<<< HEAD

=======
>>>>>>> a713a27e1e933ca1072f92d5c4eb79c6ee7cb914
class ListarProductos(View):
    def get(self, request, *args, **kwargs):
        try:
            page = int(request.GET.get('page', 1))
            size = int(request.GET.get('size', 8))
            search = request.GET.get('search', '')

            productos = Producto.objects.filter(nombreproducto__icontains=search)

            paginator = Paginator(productos, size)

            try:
                productos_pagina = paginator.page(page)
            except EmptyPage:
                productos_pagina = []

            lista_productos = []
            lista_horario = []
            for producto in productos_pagina:
                imagen_base64 = None
                if producto.imagenp:
                    try:
                        byteImg = base64.b64decode(producto.imagenp)
                        imagen_base64 = base64.b64encode(byteImg).decode('utf-8')
                    except Exception as img_error:
                        print(f"Error al procesar imagen: {str(img_error)}")
                horariosz = HorarioProducto.objects.filter(id_producto=producto.id_producto)
                for horarioss in horariosz:
                    datos_horario = {
                        'id_horarioproducto': horarioss.id_horarioproducto,
                        'id_horarios': horarioss.id_horarios.id_horarios,  # Cambiado para obtener el campo deseado
                        'id_sucursal': horarioss.id_sucursal.id_sucursal,
                    }
                    lista_horario.append(datos_horario)
                datos_producto = {
                    'id_producto': producto.id_producto,
                    'id_categoria': producto.id_categoria.id_categoria,
                    'id_um': producto.id_um.idum,
                    'puntosp': producto.puntosp,
                    'codprincipal': producto.codprincipal,
                    'nombreproducto': producto.nombreproducto,
                    'descripcionproducto': producto.descripcionproducto,
                    'preciounitario': str(producto.preciounitario),
                    'iva': producto.iva,
                    'ice': producto.ice,
                    'irbpnr': producto.irbpnr,
                    'horarios': lista_horario,
                    'imagenp': imagen_base64,
                }
                lista_horario = []

                lista_productos.append(datos_producto)

            return JsonResponse({'productos': lista_productos, 'total': paginator.count}, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
def obtener_siguiente_codprincipal():
    max_cod_producto = Producto.objects.aggregate(max_cod=Max(ExpressionWrapper(F('codprincipal'), output_field=IntegerField())))

    max_cod_combo = Combo.objects.aggregate(max_cod=Max(ExpressionWrapper(F('codprincipal'), output_field=IntegerField())))

    ultimo_numero = max(int(max_cod_producto['max_cod'] or 0), int(max_cod_combo['max_cod'] or 0))
    siguiente_numero = ultimo_numero + 1

    siguiente_codprincipal = f'{siguiente_numero:025d}'

    return siguiente_codprincipal
