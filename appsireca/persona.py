import json

from django.contrib.admin.models import LogEntry, CHANGE, ADDITION, DELETION
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_str as force_text

from appsireca.funciones import ip_client_address
from appsireca.models import Persona, Canton, Parroquia, AccesoModulo, Sexo, Nacionalidad, Provincia, Perfil
from appsireca.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    try:
        if request.method == 'POST':
            action = request.POST['action']
            if action == 'agregar':
                try:
                    data = {'title': ''}
                    if int(request.POST['id'])==0:
                        if Persona.objects.filter(identificacion=request.POST['txtidentificacion']).exists():
                            return HttpResponse(json.dumps({'result': 'bad', 'message': 'La Persona ya se encuentra registrada'}),
                                                content_type="application/json")
                        mensaje = 'Nueva persona'


                    else:
                        mensaje = 'Actualizado modulo'
                        persona = Persona.objects.get(id=int(request.POST['id']))
                        persona.nombre = request.POST['nombre']
                        persona.estado = True

                    persona.save()

                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(persona).pk,
                        object_id=persona.id,
                        object_repr=force_text(persona),
                        action_flag=ADDITION if int(request.POST['id'])==0 else CHANGE,
                        change_message=mensaje + ' (' + client_address + ')')
                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as ex:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(ex)}),
                                        content_type="application/json")


            if action == 'eliminar':
                try:
                    persona=Persona.objects.get(pk=int(request.POST['id']))
                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(persona).pk,
                        object_id=persona.id,
                        object_repr=force_text(persona),
                        action_flag=DELETION,
                        change_message=str('persona eliminado por el usuario ') + str(request.user.username) + ' (' + client_address + ')')

                    persona.delete()

                    return HttpResponse(json.dumps({'result': 'ok'}), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'buscardata':
                try:
                    data = {'title': ''}

                    persona = Persona.objects.get(pk=int(request.POST['id']))
                    data['persona'] = [
                        {'id': persona.id,
                         "nombre": str(persona.nombre),"estado": "1" if persona.estado else "2"
                         }]

                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")

            elif action == 'buscarcanton':
                try:
                    data = {'title': ''}
                    listCan = []
                    listCan.append({"id": 0, "nombre": "Seleccionar el Cantón"})
                    if Canton.objects.filter(provincia_id=int(request.POST['idprovincia'])).order_by("nombre").exists():
                        for g in Canton.objects.filter(provincia_id=int(request.POST['idprovincia'])).order_by(
                                "nombre"):
                            listCan.append({"id": g.id, "nombre": g.nombre})
                    data['listacantondatos'] = listCan
                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'buscarparroquia':
                try:
                    data = {'title': ''}
                    listaParroquia = []
                    listaParroquia.append({"id": 0, "nombre": "Seleccionar la parroquia"})
                    if Parroquia.objects.filter(canton_id=int(request.POST['idcantonresidencia'])).order_by("nombre").exists():
                        for g in Parroquia.objects.filter(canton_id=int(request.POST['idcantonresidencia'])).order_by("nombre"):
                            listaParroquia.append({"id": g.id, "nombre": g.nombre})
                    data['lsitaparroquia'] = listaParroquia
                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'serverSide':
                try:
                    lista = []
                    filtrado = False
                    draw = int(request.POST.get('draw', 1))
                    start = int(request.POST.get('start', 0))
                    length = int(request.POST.get('length', 10))
                    busqueda = str(request.POST['search[value]']) if 'search[value]' in request.POST else None

                    listapersona = Persona.objects.filter()
                    registros_total = listapersona.count()
                    if busqueda:
                        search = busqueda
                        if search:
                            ss = search.split(' ')
                            while '' in ss:
                                ss.remove('')
                            if len(ss) == 1:
                                listapersona = listapersona.filter(
                                    nombre__icontains=search).order_by('nombre')
                                filtrado = True
                            else:
                                listapersona = listapersona.filter(
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
                                listapersona = listapersona.filter(
                                    nombre__icontains=search).order_by('nombres')
                                filtrado = True
                            else:
                                listapersona = listapersona.filter(
                                    Q(nombre__icontains=ss[0]) & Q(
                                        nombre__icontains=ss[1])).order_by('nombres')
                                filtrado = True

                    if request.POST['columns[1][search][value]'] != '':
                        url = request.POST['columns[1][search][value]']
                        listapersona = listapersona.filter(url__icontains=url)

                        filtrado = True


                    listapersona = listapersona.order_by('nombres')
                    registros = listapersona[start:start + length] if length != -1 else listapersona
                    registros_filtrado = listapersona.count()

                    for d in registros:
                        htmlAcciones = ''

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="editar(' + str(
                            d.id) + ');"><i class="dw dw-edit-2"></i>  Editar</a></li>'

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="eliminarmodulo(' + str(
                            d.id) + ',\'' + str(
                            d.nombres).upper() + '\');"><i class="dw dw-delete-3"></i>  Eliminar</a></li>'


                        lista.append({
                            'nombre': str(d.nombres),
                            'usuario': str(d.usuario.username),
                            'identificacion': str(d.identificacion),
                            'telefono': str(d.telefono if d.telefono else '---'),
                            'fechaingreso': str(d.fechaingreso),
                            'perfiles': [p.perfil.nombre for p in d.perfiles()],
                            'estado': str("ACTIVO" if d.usuario.is_active else "INACTIVO"),
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
            data = {'title':'Persona'}
            addUserData(request, data)
            data['permisopcion'] = AccesoModulo.objects.get(id=int(request.GET['acc']))
            data['listanacionalidad'] = Nacionalidad.objects.filter()
            data['listasexo'] = Sexo.objects.filter()
            data['listaprovincia'] = Provincia.objects.filter()
            data['listaperfil'] = Perfil.objects.filter(estado=True)



            return render(request, "mantenimiento/personabs.html", data)

    except Exception as e:
        print('Error excepcion cursos '+str(e))
        return render(request, "error.html", data)