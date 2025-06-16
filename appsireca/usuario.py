import json

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import force_str as force_text

from appsireca.funciones import ip_client_address
from appsireca.models import Perfil, AccesoModulo
from appsireca.views import addUserData
from sireca.settings import DEFAULT_PASSWORD


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    try:
        if request.method == 'POST':
            action = request.POST['action']

            if action == 'resetear':
                try:
                    data = {'title': ''}

                    usuario = User.objects.get(pk=int(request.POST['id']))
                    usuario.set_password(DEFAULT_PASSWORD)
                    usuario.save()
                    client_address = ip_client_address(request)
                    LogEntry.objects.log_action(
                        user_id=request.user.pk,
                        content_type_id=ContentType.objects.get_for_model(usuario).pk,
                        object_id=usuario.id,
                        object_repr=force_text(usuario),
                        action_flag=CHANGE,
                        change_message=str('contraseña cambiada por el usuario ') + str(
                            request.user.username) + ' (' + client_address + ')')

                    data['result'] = 'ok'
                    return HttpResponse(json.dumps(data), content_type="application/json")
                except Exception as e:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")


            elif action == 'eliminar':
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

            if action == 'cambiarestado':
                try:
                    data = {'title': ''}
                    usuario = User.objects.get(pk=int(request.POST['id']))
                    if usuario.is_active:
                        usuario.is_active = False
                    else:
                        usuario.is_active = True

                    usuario.save()
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

                    listausuarios = User.objects.filter()
                    registros_total = listausuarios.count()
                    if busqueda:
                        search = busqueda
                        if search:
                            ss = search.split(' ')
                            while '' in ss:
                                ss.remove('')
                            if len(ss) == 1:
                                listausuarios = listausuarios.filter(
                                    username__icontains=search).order_by('username')
                                filtrado = True
                            else:
                                listausuarios = listausuarios.filter(
                                    Q(username__icontains=ss[0]) & Q(
                                        username__icontains=ss[1])).order_by('username')
                                filtrado = True

                    if request.POST['columns[0][search][value]'] != '':
                        search = request.POST['columns[0][search][value]']
                        if search:
                            ss = search.split(' ')
                            while '' in ss:
                                ss.remove('')
                            if len(ss) == 1:
                                listausuarios = listausuarios.filter(
                                    Q(first_name__icontains=search) | Q(last_name__icontains=search)).order_by('username')
                                filtrado = True
                            else:
                                listausuarios = listausuarios.filter(
                                    Q(first_name__icontains=ss[0]) & Q(
                                        last__name__icontains=ss[1])).order_by('username')
                                filtrado = True


                    if request.POST['columns[1][search][value]'] != '':
                        search = request.POST['columns[1][search][value]']
                        if search:
                            ss = search.split(' ')
                            while '' in ss:
                                ss.remove('')
                            if len(ss) == 1:
                                listausuarios = listausuarios.filter(
                                    username__icontains=search).order_by('username')
                                filtrado = True
                            else:
                                listausuarios = listausuarios.filter(
                                    Q(username__icontains=ss[0]) & Q(
                                        username__icontains=ss[1])).order_by('username')
                                filtrado = True


                    listausuarios = listausuarios.order_by('username')
                    registros = listausuarios[start:start + length] if length != -1 else listausuarios
                    registros_filtrado = listausuarios.count()

                    for d in registros:
                        htmlAcciones = ''
                        superusuario=''
                        estado= 'Desactivar Usuario' if d.is_active else 'Activar Usuario'

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="cambiarcontrasena(' + str(
                            d.id) + ',\'' + str(d.username) + '\');"><i class="dw  dw-password"></i>  Resetear Contraseña</a></li>'

                        htmlAcciones += ' <li><a class="dropdown-item" style="cursor: pointer" onclick="activarinactiva(' + str(
                            d.id) + ',\'' + str(d.username) + '\');"><i class="dw dw-alarm-clock"></i>  '+ estado +'</a></li>'

                        superusuario += '<img src="../sireca/static/assets/images/check-mark-green.png"   width="14px" alt="Activo" border="0" />' if d.is_superuser else '<img src="../sireca/static/assets/images/cross.png"   width="14px" alt="Inactivo" border="0" />'

                        lista.append({
                            'nombre': str(d.first_name).upper()+ ' '+ str(d.last_name).upper(),
                            'username': str(d.username),
                            'email':str(d.email),
                            'superusuario':superusuario,
                            'estado': str("ACTIVO" if d.is_active else "INACTIVO"),
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
                        'placeholderBusqueda': 'Buscar ',
                        'result': 'ok',
                        'filtrado': filtrado
                    }

                    return HttpResponse(json.dumps(respuesta), content_type="application/json")
                except Exception as e:
                    print(e)
                    return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}),
                                        content_type="application/json")

        else:
            data = {'title':'Usuarios'}
            addUserData(request, data)
            data['permisopcion'] = AccesoModulo.objects.get(id=int(request.GET['acc']))
            data['DEFAULT_PASSWORD'] = DEFAULT_PASSWORD

            return render(request, "mantenimiento/usuariobs.html", data)

    except Exception as e:
        print('Error excepcion cursos '+str(e))
        return render(request, "error.html", data)