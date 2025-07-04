import json

from django.contrib.admin.models import LogEntry, ADDITION, DELETION
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from django.utils.encoding import force_str as force_text
from appsireca.funciones import ip_client_address
from appsireca.models import AccesoModulo, Banco
from appsireca.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    try:
        if request.method == 'POST':
            action = request.POST['action']
            if action == 'agregar':
                try:
                    data = {'title': ''}
                    nombre = str(request.POST['nombre']).upper()
                    if request.POST['estado'] == '1':
                        estado = True
                    else:
                        estado = False
                    if int(request.POST['id'])==0:
                        if Banco.objects.filter(nombre__icontains=nombre).exists():
                            return HttpResponse(json.dumps({'result': 'bad', 'message': 'El banco ya se encuentra registrada'}),
                                                content_type="application/json")
                        mensaje = 'Nuevo banco'
                        banco = Banco(nombre=nombre,estado=estado)

                    else:
                        mensaje = 'Actualizado banco'
                        banco = Banco.objects.get(id=int(request.POST['id']))
                        banco.nombre = nombre
                        banco.estado = estado

                    banco.save()

                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(banco).pk,
                        object_id=banco.id,
                        object_repr=force_text(banco),
                        action_flag=ADDITION,
                        change_message=mensaje + ' (' + client_address + ')')
                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as ex:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(ex)}),
                                        content_type="application/json")


            if action == 'eliminar':
                try:
                    banco=Banco.objects.get(pk=int(request.POST['id']))
                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(banco).pk,
                        object_id=banco.id,
                        object_repr=force_text(banco),
                        action_flag=DELETION,
                        change_message=str('banco eliminado por el usuario ') + str(request.user.username) + ' (' + client_address + ')')

                    banco.delete()

                    return HttpResponse(json.dumps({'result': 'ok'}), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'buscardata':
                try:
                    data = {'title': ''}

                    banco = Banco.objects.get(pk=int(request.POST['id']))
                    data['banco'] = [
                        {'id': banco.id,
                         "nombre": str(banco.nombre),"estado": "1" if banco.estado else "2"
                         }]

                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            if action == 'serverSide':
                try:
                    lista = []
                    filtrado = False
                    draw = int(request.POST.get('draw', 1))
                    start = int(request.POST.get('start', 0))
                    length = int(request.POST.get('length', 10))
                    busqueda = str(request.POST['search[value]']) if 'search[value]' in request.POST else None

                    listabanco = Banco.objects.filter()
                    registros_total = listabanco.count()
                    if busqueda:
                        search = busqueda
                        if search:
                            ss = search.split(' ')
                            while '' in ss:
                                ss.remove('')
                            if len(ss) == 1:
                                listabanco = listabanco.filter(
                                    nombre__icontains=search).order_by('nombre')
                                filtrado = True
                            else:
                                listabanco = listabanco.filter(
                                    Q(nombre__icontains=ss[0]) & Q(
                                        nombres__icontains=ss[1])).order_by('nombre')
                                filtrado = True

                    if request.POST['columns[0][search][value]'] != '':
                        search = request.POST['columns[0][search][value]']
                        if search:
                            ss = search.split(' ')
                            while '' in ss:
                                ss.remove('')
                            if len(ss) == 1:
                                listabanco = listabanco.filter(
                                    nombre__icontains=search).order_by('nombre')
                                filtrado = True
                            else:
                                listabanco = listabanco.filter(
                                    Q(nombre__icontains=ss[0]) & Q(
                                        nombre__icontains=ss[1])).order_by('nombre')
                                filtrado = True

                    if request.POST['columns[1][search][value]'] != '':
                        url = request.POST['columns[1][search][value]']
                        listabanco = listabanco.filter(url__icontains=url)

                        filtrado = True


                    listabanco = listabanco.order_by('nombre')
                    registros = listabanco[start:start + length] if length != -1 else listabanco
                    registros_filtrado = listabanco.count()

                    for d in registros:
                        htmlAcciones = ''

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="editar(' + str(
                            d.id) + ');"><i class="dw dw-edit-2"></i>  Editar</a></li>'

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="eliminarbanco(' + str(
                            d.id) + ',\'' + str(
                            d.nombre).upper() + '\');"><i class="dw dw-delete-3"></i>  Eliminar</a></li>'


                        lista.append({
                            'nombre': str(d.nombre),
                            'estado': str("ACTIVO" if d.estado else "INACTIVO"),
                              'acciones': f'''
                                        <div class="dropdown">
                                            <button class="btn btn-primary dropdown-toggle" type="button" id="dropdownMenu2" data-bs-toggle="dropdown" aria-expanded="false">
                                                Acciones
                                            </button>
                                            <ul class="dropdown-menu" aria-labelledby="dropdownMenu2">
                                                {htmlAcciones}
                                            </ul>
                                        </div>
                                    '''
                        })

                    estado = [{"id": 1, "nombre": "ACTIVO"},
                                     {"id": 2, "nombre": "INACTIVO"}]
                    respuesta = {
                        'draw': draw,
                        'recordsTotal': registros_total,
                        'recordsFiltered': registros_filtrado,
                        'data': lista,
                        'filtro-select-estado': list(estado),
                        'placeholderBusqueda': 'Buscar el nombre del modulo',
                        'result': 'ok',
                        'filtrado': filtrado
                    }

                    return HttpResponse(json.dumps(respuesta), content_type="application/json")
                except Exception as e:
                    print(e)
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")

        else:
            data = {'title':'Bancos'}
            addUserData(request, data)
            data['permisopcion'] = AccesoModulo.objects.get(id=int(request.GET['acc']))

            return render(request, "mantenimiento/bancobs.html", data)

    except Exception as e:
        print('Error excepcion cursos '+str(e))
        return render(request, "error.html", data)