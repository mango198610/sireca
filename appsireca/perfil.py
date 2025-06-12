import json

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_str as force_text

from appsireca.funciones import ip_client_address, MiPaginador
from appsireca.models import Perfil, ModuloPerfil, Modulo, PerfilPersona, AccesoModulo
from appsireca.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    try:
        if request.method == 'POST':
            action = request.POST['action']
            if action == 'agregar':
                try:
                    data = {'title': ''}
                    nombre = request.POST['nombre']
                    if request.POST['estado'] == '1':
                        estado = True
                    else:
                        estado = False
                    if int(request.POST['id'])==0:
                        if Perfil.objects.filter(nombre=request.POST['nombre']).exists():
                            return HttpResponse(json.dumps({'result': 'bad', 'message': 'El perfil ya se encuentra registrada'}),
                                                content_type="application/json")
                        mensaje = 'Nuevo perfil'
                        perfil = Perfil(nombre=nombre, estado=estado)

                    else:
                        mensaje = 'Actualizar Perfil'
                        perfil = Perfil.objects.get(id=int(request.POST['id']))
                        perfil.nombre = request.POST['nombre']
                        perfil.estado = estado

                    perfil.save()

                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(perfil).pk,
                        object_id=perfil.id,
                        object_repr=force_text(perfil),
                        action_flag=ADDITION if int(request.POST['id'])==0 else CHANGE,
                        change_message=mensaje + ' (' + client_address + ')')
                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as ex:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(ex)}),
                                        content_type="application/json")


            if action == 'eliminar':
                try:
                    perfil=Perfil.objects.get(pk=int(request.POST['id']))
                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(perfil).pk,
                        object_id=perfil.id,
                        object_repr=force_text(perfil),
                        action_flag=DELETION,
                        change_message=str('perfil eliminado por el usuario ') + str(request.user.username) + ' (' + client_address + ')')

                    perfil.delete()

                    return HttpResponse(json.dumps({'result': 'ok'}), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'buscardata':
                try:
                    data = {'title': ''}

                    perfil = Perfil.objects.get(pk=int(request.POST['id']))
                    data['perfil'] = [
                        {'id': perfil.id,
                         "nombre": str(perfil.nombre),"estado": "1" if perfil.estado else "2"
                         }]

                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'buscarmoduloasignados':
                try:
                    data = {'title': ''}

                    perfil = Perfil.objects.get(pk=int(request.POST['id']))
                    data['modulos'] = [
                        {'id': modulo.modulo.id,
                         "nombre": str(modulo.modulo.nombre)
                         } for modulo in ModuloPerfil.objects.filter(perfil=perfil,modulo__estado=True)]

                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'modulos':
                try:
                    ss = request.POST['q'].split(' ')

                    while '' in ss:
                        ss.remove('')
                    if len(ss) == 1:

                        modulos = Modulo.objects.filter(nombre__icontains=request.POST['q'],estado=True).order_by(
                            'nombre')
                    else:

                        modulos = Modulo.objects.filter(
                            Q(nombre__icontains=ss[0]) & Q(
                                nombre__icontains=ss[1]),estado=True).order_by(
                            'nombre')

                    paging = MiPaginador(modulos, 30)
                    p = 1
                    try:
                        if 'page' in request.POST:
                            p = int(request.POST['page'])
                        page = paging.page(p)
                    except:
                        page = paging.page(p)

                    lista = [{"id": d.id, "nombre": str(d)} for d in
                             page.object_list]

                    return HttpResponse(json.dumps({'result': 'ok', 'items': lista, 'page': p}),
                                        content_type="application/json")

                except Exception as ex:
                    return HttpResponse(json.dumps({"result": "bad", "message": ex}), content_type="application/json")


            elif action == 'asignarmodulo':
                try:
                    data = {'title': ''}
                    perfil = Perfil.objects.get(id=int(request.POST['id']))
                    listamoduloantes = perfil.moduloperfil()
                    listamoduloingreso =  list(map(int,request.POST.getlist('cmbasignarmodulo')))


                    for d in listamoduloingreso:
                        modulo = Modulo.objects.get(id=int(d))
                        if not  ModuloPerfil.objects.filter(perfil=perfil, modulo=modulo).exists():
                            moduloperfil = ModuloPerfil(perfil=perfil, modulo=modulo)
                            moduloperfil.save()
                        listaperfilpersona = PerfilPersona.objects.filter(perfil=perfil)
                        for a in listaperfilpersona:
                            perfilpersona = PerfilPersona.objects.get(perfil=perfil, persona=a.persona)
                            if not AccesoModulo.objects.filter(perfilpersona=perfilpersona,
                                                               modulo=modulo).exists():
                                accesomodulo = AccesoModulo(perfilpersona=perfilpersona, modulo=modulo,
                                                            ingresar=True,
                                                            editar=True, ver=True, eliminar=False)
                                if request.user.is_superuser:
                                    accesomodulo.eliminar = True
                                accesomodulo.save()

                    # verificar si se quito un modulo del perfil
                    ideliminados = list(set(listamoduloantes) - set(list(listamoduloingreso)))
                    ModuloPerfil.objects.filter(perfil=perfil, modulo__id__in=ideliminados).delete()
                    AccesoModulo.objects.filter(perfilpersona__perfil=perfil, modulo__id__in=ideliminados).delete()


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

                    listaperfil = Perfil.objects.filter()
                    registros_total = listaperfil.count()
                    if busqueda:
                        search = busqueda
                        if search:
                            ss = search.split(' ')
                            while '' in ss:
                                ss.remove('')
                            if len(ss) == 1:
                                listaperfil = listaperfil.filter(
                                    nombre__icontains=search).order_by('nombre')
                                filtrado = True
                            else:
                                listaperfil = listaperfil.filter(
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
                                listaperfil = listaperfil.filter(
                                    nombre__icontains=search).order_by('nombre')
                                filtrado = True
                            else:
                                listaperfil = listaperfil.filter(
                                    Q(nombre__icontains=ss[0]) & Q(
                                        nombre__icontains=ss[1])).order_by('nombre')
                                filtrado = True


                    listaperfil = listaperfil.order_by('nombre')
                    registros = listaperfil[start:start + length] if length != -1 else listaperfil
                    registros_filtrado = listaperfil.count()

                    for d in registros:
                        htmlAcciones = ''

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="editar(' + str(
                            d.id) + ');"><i class="dw dw-edit-2"></i>  Editar</a></li>'

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="asignarmodulo(' + str(
                            d.id) + ',\'' + str(
                            d.nombre).upper() + '\');"><i class="dw dw-menu"></i>  Asignar Módulo</a></li>'

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="eliminarperfil(' + str(
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
                        'placeholderBusqueda': 'Buscar el nombre del perfil',
                        'result': 'ok',
                        'filtrado': filtrado
                    }

                    return HttpResponse(json.dumps(respuesta), content_type="application/json")
                except Exception as e:
                    print(e)
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")

        else:
            data = {'title':'Perfil'}
            addUserData(request, data)
            data['permisopcion'] = AccesoModulo.objects.get(id=int(request.GET['acc']))

            return render(request, "mantenimiento/perfilbs.html", data)

    except Exception as e:
        print('Error excepcion cursos '+str(e))
        return render(request, "error.html", data)