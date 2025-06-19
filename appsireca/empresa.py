import json

from django.contrib.admin.models import LogEntry, ADDITION, DELETION
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_str as force_text
from appsireca.funciones import ip_client_address, buscaractividad
from appsireca.models import Empresa, AccesoModulo, SectorComercial, TipoIdentificacion, ActividadComercial
from sireca.settings import ID_TIPO_IDENTIFICACION_RUC

from appsireca.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    try:
        if request.method == 'POST':
            action = request.POST['action']
            if action == 'agregar':
                try:
                    data = {'title': ''}
                    nombre = str(request.POST['txtrazonsocial']).upper()
                    if int(request.POST['cmbestado']) == 1:
                        estado = True
                    else:
                        estado = False

                    if int(request.POST['id'])==0:
                        if Empresa.objects.filter(identificacion= str(request.POST['txtidentificacion'])).exists():
                            return HttpResponse(json.dumps({'result': 'bad', 'message': 'La identifación ya se encuentra registrada'}),
                                                content_type="application/json")


                        mensaje = 'Nuevo Empresa'
                        actividad=int(request.POST.get('cmbactividad')) if int(request.POST.get('cmbactividad')) else None

                        empresa = Empresa(tipoidentificacion_id=int(request.POST['cmbtipoidentificacion']),
                                          identificacion=request.POST['txtidentificacion'],actividad_id=actividad,
                                          nombre=nombre, direccion=str(request.POST['txtdireccion']).upper() ,estado=estado)

                    else:
                        mensaje = 'Actualizado Empresa'
                        empresa = Empresa.objects.get(id=int(request.POST['id']))
                        empresa.nombre = nombre
                        empresa.estado = estado

                    empresa.save()

                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(empresa).pk,
                        object_id=empresa.id,
                        object_repr=force_text(empresa),
                        action_flag=ADDITION,
                        change_message=mensaje + ' (' + client_address + ')')
                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as ex:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(ex)}),
                                        content_type="application/json")


            if action == 'eliminar':
                try:
                    empresa=Empresa.objects.get(pk=int(request.POST['id']))
                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(empresa).pk,
                        object_id=empresa.id,
                        object_repr=force_text(empresa),
                        action_flag=DELETION,
                        change_message=str('Empresa eliminado por el usuario ') + str(request.user.username) + ' (' + client_address + ')')

                    empresa.delete()

                    return HttpResponse(json.dumps({'result': 'ok'}), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'buscardata':
                try:
                    data = {'title': ''}

                    empresa = Empresa.objects.get(pk=int(request.POST['id']))
                    data['Empresa'] = [
                        {'id': empresa.id,
                         "nombre": str(empresa.nombre),"estado": "1" if empresa.estado else "2"
                         }]

                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'actividad':
                try:
                    data = {'title': ''}
                    actividad= buscaractividad(int(request.POST['idsector']),None)
                    lista = [{"id": d.id, "nombre": str(d)} for d in actividad] or [{"id": 0, "nombre": "SIN ACTIVIDAD"}]
                    return HttpResponse(json.dumps({'result': 'ok', 'listactividad': lista}),
                                content_type="application/json")
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

                    listaempresa = Empresa.objects.filter()
                    registros_total = listaempresa.count()
                    if busqueda:
                        search = busqueda
                        if search:
                            ss = search.split(' ')
                            while '' in ss:
                                ss.remove('')
                            if len(ss) == 1:
                                listaempresa = listaempresa.filter(
                                    nombre__icontains=search).order_by('nombre')
                                filtrado = True
                            else:
                                listaempresa = listaempresa.filter(
                                    Q(nombre__icontains=ss[0]) & Q(
                                        nombres__icontains=ss[1])).order_by('nombre')
                                filtrado = True

                    if request.POST['columns[0][search][value]'] != '':
                        ruc = request.POST['columns[0][search][value]']
                        listaempresa = listaempresa.filter(
                            identificacion=ruc).order_by('nombre')
                        filtrado = True

                    if request.POST['columns[1][search][value]'] != '':
                        search = request.POST['columns[1][search][value]']
                        if search:
                            ss = search.split(' ')
                            while '' in ss:
                                ss.remove('')
                            if len(ss) == 1:
                                listaempresa = listaempresa.filter(
                                    nombre__icontains=search).order_by('nombre')
                                filtrado = True
                            else:
                                listaempresa = listaempresa.filter(
                                    Q(nombre__icontains=ss[0]) & Q(
                                        nombre__icontains=ss[1])).order_by('nombre')
                                filtrado = True

                    if request.POST['columns[3][search][value]'] != '':
                        sector = request.POST['columns[3][search][value]']
                        listaempresa = listaempresa.filter(
                            actividad__sector_id=sector).order_by('nombre')
                        filtrado = True

                    if request.POST['columns[3][search][value]'] != '':
                        actividad = request.POST['columns[3][search][value]']
                        listaempresa = listaempresa.filter(
                            actividad_id=actividad).order_by('nombre')
                        filtrado = True


                    listaempresa = listaempresa.order_by('nombre')
                    registros = listaempresa[start:start + length] if length != -1 else listaempresa
                    registros_filtrado = listaempresa.count()

                    for d in registros:
                        htmlAcciones = ''

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="editar(' + str(
                            d.id) + ');"><i class="dw dw-edit-2"></i>  Editar</a></li>'

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="eliminarEmpresa(' + str(
                            d.id) + ',\'' + str(
                            d.nombre).upper() + '\');"><i class="dw dw-delete-3"></i>  Eliminar</a></li>'
                        if d.estado:
                            htmlestado = '<span class="badge bg-success fs-6">ACTIVO</span>'
                        else:
                            htmlestado = '<span class="badge bg-danger fs-6">INACTIVO</span>'

                        lista.append({
                            'ruc': str(d.identificacion),
                            'nombre': str(d.nombre),
                            'direccion': str(d.direccion),
                            'sector': str(d.actividad.sector.nombre) if d.actividad else str('SIN SECTOR'),
                            'actividad': str(d.actividad.nombre) if d.actividad else str('SIN ACTIVIDAD'),
                            'estado': htmlestado,
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
                    sector =[{"id": x.id, "nombre": x.nombre} for x in SectorComercial.objects.filter(estado=True)]
                    actividad =[{"id":x.id, "nombre": x.nombre} for x in ActividadComercial.objects.filter(estado=True).distinct()]

                    respuesta = {
                        'draw': draw,
                        'recordsTotal': registros_total,
                        'recordsFiltered': registros_filtrado,
                        'data': lista,
                        'filtro-select-sector': list(sector),
                        'filtro-select-actividad': list(actividad),
                        'filtro-select-estado': list(estado),
                        'placeholderBusqueda': 'Buscar el nombre ',
                        'result': 'ok',
                        'filtrado': filtrado
                    }

                    return HttpResponse(json.dumps(respuesta), content_type="application/json")
                except Exception as e:
                    print(e)
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")

        else:
            data = {'title':'Empresa'}
            addUserData(request, data)
            data['permisopcion'] = AccesoModulo.objects.get(id=int(request.GET['acc']))
            data['listasector'] = SectorComercial.objects.filter(estado=True)
            data['listatipoidentifcacion'] = TipoIdentificacion.objects.filter(id=ID_TIPO_IDENTIFICACION_RUC,estado=True)
            data['listatipoidentifcacionrep'] = TipoIdentificacion.objects.filter(estado=True)

            return render(request, "mantenimiento/empresa.html", data)

    except Exception as e:
        print('Error excepcion cursos '+str(e))
        return render(request, "error.html", data)