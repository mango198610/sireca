import json

from django.contrib.admin.models import LogEntry, ADDITION, DELETION
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_str as force_text
from appsireca.funciones import ip_client_address, buscaractividad
from appsireca.models import Empresa, AccesoModulo, SectorComercial, TipoIdentificacion, ActividadComercial, \
    RepresentanteEmpresa, Cargo, EmpresaOriginador, RepresentanteEmpresaOriginador, TipoOriginador
from sireca.settings import ID_TIPO_IDENTIFICACION_RUC
from django.db import transaction
from appsireca.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')

def view(request):
    try:
        if request.method == 'POST':
            action = request.POST['action']
            if action == 'agregar':
                with (transaction.atomic()):
                    try:
                        data = {'title': ''}
                        nombre = str(request.POST['txtrazonsocial']).upper()
                        if int(request.POST['cmbestado']) == 1:
                            estado = True
                        else:
                            estado = False
                        actividad = int(request.POST.get('cmbactividad')) if int(
                            request.POST.get('cmbactividad')) else None

                        if int(request.POST['id'])==0:
                            if EmpresaOriginador.objects.filter(identificacion= str(request.POST['txtidentificacion'])).exists():
                                return HttpResponse(json.dumps({'result': 'bad', 'message': 'La identifación ya se encuentra registrada'}),
                                                    content_type="application/json")


                            mensaje = 'Nuevo Empresa Originador'

                            empresa = EmpresaOriginador(tipoidentificacion_id=int(request.POST['cmbtipoidentificacion']),
                                              identificacion=request.POST['txtidentificacion'],actividad_id=actividad ,
                                              nombre=nombre, direccion=str(request.POST['txtdireccion']).upper(),empresa_id=int(request.POST['cmbempresapertenece']),tipo_id=int(request.POST['cmbtipoempresa']) ,estado=estado)

                            # Guardar el representante legal

                            representantelegal=RepresentanteEmpresaOriginador(tipoidentificacion_id=int(request.POST['cmbtipoidentificacionrep']) if int(request.POST['cmbtipoidentificacion'])>0 else None,
                                                                    identificacion=request.POST['txtidentificacionrep'],nombre=str(request.POST['txtnombrerep']),
                                                                    apellido1=str(request.POST['txtapellido1']),apellido2=str(request.POST['txtapellido2']),
                                                                    telefonoconvencional=str(request.POST['txttelefconv']),celular=str(request.POST['txtcelular']),cargo_id=int(request.POST['cmbcargo']) if int(request.POST['cmbcargo'])>0 else None,
                                                                    otrocelular=str(request.POST['txtcelular2']),correo=str(request.POST['txtcorreo']),empresa=empresa)

                        else:
                            mensaje = 'Actualizado Empresa Originador'
                            empresa = EmpresaOriginador.objects.get(id=int(request.POST['id']))
                            representantelegal=RepresentanteEmpresaOriginador.objects.filter(empresa=empresa).first()
                            empresa.nombre = nombre
                            empresa.identificacion=request.POST['txtidentificacion']
                            empresa.actividad_id=actividad
                            empresa.direccion=str(request.POST['txtdireccion']).upper()
                            empresa.empresa_id=int(request.POST['cmbempresapertenece'])
                            empresa.tipo_id=int(request.POST['cmbtipoempresa'])
                            empresa.estado = estado
                            #actualizar el representante legal
                            representantelegal.tipoidentificacion_id=int(request.POST['cmbtipoidentificacionrep']) if int(
                                    request.POST['cmbtipoidentificacion']) > 0 else None
                            representantelegal.identificacion=request.POST['txtidentificacionrep']
                            representantelegal.nombre=str(request.POST['txtnombrerep'])
                            representantelegal.apellido1=str(request.POST['txtapellido1'])
                            representantelegal.apellido2=str(request.POST['txtapellido2'])
                            representantelegal.telefonoconvencional=str(request.POST['txttelefconv'])
                            representantelegal.celular=str(request.POST['txtcelular'])
                            representantelegal.otrocelular=str(request.POST['txtcelular2'])
                            representantelegal.correo=str(request.POST['txtcorreo'])
                            representantelegal.empresa=empresa
                            representantelegal.cargo_id = int(request.POST['cmbcargo']) if int(request.POST['cmbcargo']) > 0 else None

                        #preguntar si viene una imagen de la empresa
                        if "imglogo" in request.FILES:
                            empresa.logo=request.FILES["imglogo"]


                        empresa.save()
                        representantelegal.save()

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
                    empresa=EmpresaOriginador.objects.get(pk=int(request.POST['id']))
                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(empresa).pk,
                        object_id=empresa.id,
                        object_repr=force_text(empresa),
                        action_flag=DELETION,
                        change_message=str('Empresa Originador eliminado por el usuario ') + str(request.user.username) + ' (' + client_address + ')')

                    empresa.delete()

                    return HttpResponse(json.dumps({'result': 'ok'}), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            if action == 'eliminarlogo':
                try:
                    empresa=EmpresaOriginador.objects.get(pk=int(request.POST['id']))
                    empresa.logo=''
                    empresa.save()
                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(empresa).pk,
                        object_id=empresa.id,
                        object_repr=force_text(empresa),
                        action_flag=DELETION,
                        change_message=str('Logo Originador eliminado por el usuario ') + str(request.user.username) + ' (' + client_address + ')')

                    return HttpResponse(json.dumps({'result': 'ok'}), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'buscardata':
                try:
                    data = {'title': ''}

                    empresa = EmpresaOriginador.objects.get(pk=int(request.POST['id']))
                    reprempresa=RepresentanteEmpresaOriginador.objects.filter(empresa=empresa).first()
                    modelactiv= ActividadComercial.objects.filter(sector=empresa.actividad.sector) if empresa.actividad.sector else []
                    cargolista=Cargo.objects.filter(estado=True)
                    data['empresa'] = [
                        {'id': empresa.id,
                         "tipoidentificacion": empresa.tipoidentificacion.id,
                         "identificacion":empresa.identificacion,
                         "nombre": str(empresa.nombre),"estado": "1" if empresa.estado else "2",
                         "direccion": str(empresa.direccion),"sector":getattr(getattr(empresa.actividad, 'sector', None), 'id', 0),
                         "actividad":  getattr(empresa.actividad, 'id', 0),
                         "listactividad":[{"id":x.id,"nombre":x.nombre} for x in modelactiv],
                         "listacargo":[{"id":x.id,"nombre":x.nombre} for x in cargolista],
                         "tipoidentificacionrep": reprempresa.tipoidentificacion_id  if reprempresa else '',
                         "identificacionrep": reprempresa.identificacion  if reprempresa else '',
                         "logo":str('../sireca/media'+empresa.logo.url) if empresa.logo else  '',
                         "nombres": reprempresa.nombre  if reprempresa else '',
                         "apellido1": reprempresa.apellido1  if reprempresa else '',
                         "apellido2": reprempresa.apellido2  if reprempresa else '',
                         "telefoconv": reprempresa.telefonoconvencional  if reprempresa else '',
                         "celular": reprempresa.celular  if reprempresa else '',
                         "otrocelular": reprempresa.otrocelular  if reprempresa else '',
                         "email": reprempresa.correo  if reprempresa else '',
                         "cargo": getattr(getattr(reprempresa, 'cargo', None), 'id', '0')
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
                    data={}
                    filtrado = False
                    draw = int(request.POST.get('draw', 1))
                    start = int(request.POST.get('start', 0))
                    length = int(request.POST.get('length', 10))
                    busqueda = str(request.POST['search[value]']) if 'search[value]' in request.POST else None
                    listaempresa = EmpresaOriginador.objects.filter() if request.user.is_superuser else EmpresaOriginador.objects.filter(estado=True,pk=data['perfilpersona'].empresa.id)
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

                    if request.POST['columns[1][search][value]'] != '':
                        ruc = request.POST['columns[1][search][value]']
                        listaempresa = listaempresa.filter(
                            identificacion=ruc).order_by('nombre')
                        filtrado = True

                    if request.POST['columns[2][search][value]'] != '':
                        search = request.POST['columns[2][search][value]']
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

                    if request.POST['columns[4][search][value]'] != '':
                        sector = request.POST['columns[4][search][value]']
                        listaempresa = listaempresa.filter(
                            actividad__sector_id=sector).order_by('nombre')
                        filtrado = True

                    if request.POST['columns[5][search][value]'] != '':
                        actividad = request.POST['columns[5][search][value]']
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

                        if d.logo:
                            htmlogo='<img class="bg-soft-primary rounded img-fluid avatar-40 me-3" src="../sireca/media'+d.logo.url+'" alt="logo">'
                        else:
                            htmlogo = '<img class="bg-soft-primary rounded img-fluid avatar-40 me-3" src="../sireca/static/assets/images/shapes/01.png" alt="logo">'

                        lista.append({
                            'logo':htmlogo,
                            'tiporiginador': str(d.tipo.nombre),
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
                    tipooriginador = [{"id": x.id, "nombre": x.nombre} for x in TipoOriginador.objects.filter(estado=True)]

                    actividad=[]
                    if request.POST['columns[4][search][value]'] != '':
                        actividad =[{"id":x.id, "nombre": x.nombre} for x in ActividadComercial.objects.filter(sector_id=int(request.POST['columns[4][search][value]']),estado=True).distinct()]

                    respuesta = {
                        'draw': draw,
                        'recordsTotal': registros_total,
                        'recordsFiltered': registros_filtrado,
                        'data': lista,
                        'filtro-select-sector': list(sector),
                        'filtro-select-actividad': list(actividad),
                        'filtro-select-estado': list(estado),
                        'filtro-select-tiporiginador': list(tipooriginador),
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
            data = {'title':'Empresa Originador'}
            addUserData(request, data)
            data['permisopcion'] = AccesoModulo.objects.get(id=int(request.GET['acc']))
            data['listasector'] = SectorComercial.objects.filter(estado=True)
            data['listadoempresa'] = Empresa.objects.filter(estado=True) if request.user.is_superuser else Empresa.objects.filter(estado=True,pk=data['perfilpersona'].empresa.id)
            data['listatipoidentifcacion'] = TipoIdentificacion.objects.filter(id=ID_TIPO_IDENTIFICACION_RUC,estado=True)
            data['listatipoidentifcacionrep'] = TipoIdentificacion.objects.filter(estado=True)
            data['listadotipooriginador'] = TipoOriginador.objects.filter(estado=True)
            data['listacargo'] = Cargo.objects.filter(estado=True)

            return render(request, "mantenimiento/originador.html", data)

    except Exception as e:
        print('Error excepcion cursos '+str(e))
        return render(request, "error.html", data)