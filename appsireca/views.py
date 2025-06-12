import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from datetime import datetime

from appsireca.models import PerfilPersona


@login_required(redirect_field_name='ret', login_url='/login')
def panel(request):
    try:
        if request.method == 'POST':
            action = request.POST['action']
        else:
            data = {'title': 'Index'}
            ruta = [['/', 'home'], ['/', 'Pages']]
            data['ruta'] = ruta
            addUserData(request, data)

            return render(request ,"panelbs.html" ,  data)
    except Exception as e:
        print("EXCEPCION DE PANEL " + str(e))
        return render(request, "error.html")


def login_user(request):

    if request.method == 'POST':
        try:
            user = authenticate(username=(request.POST['user']).lower(), password=request.POST['pass'])
            if user is not None:
                if not user.is_active:
                    return HttpResponse(json.dumps({'result': 'bad', 'message': 'Usuario no esta Activo'}),
                                        content_type="application/json")
                else:
                    login(request, user)
                    return HttpResponse(json.dumps({'result': 'ok'}), content_type="application/json")
            else:
                return HttpResponse(json.dumps({'result': 'bad', 'message': 'Credenciales Incorrectas'}),
                                    content_type="application/json")


        except Exception as e:
            return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}), content_type="application/json")

    else:
        data ={'title':'Inicio de Session'}
        data['fecha'] = datetime.now()


        return render(request ,"login.html" ,  data)



def addUserData(request, data):
    data['usuario'] = request.user
    perfilpersona = PerfilPersona.objects.filter(persona__usuario=request.user).first()
    data['perfilpersona'] = perfilpersona
    data['listadoPerfil'] = PerfilPersona.objects.filter(persona=perfilpersona.persona)


def logout_user(request):
    if request.method == 'POST':
        try:
            logout(request)
            return HttpResponse(json.dumps({'result': 'ok'}), content_type="application/json")
        except Exception as e:
            return HttpResponse(json.dumps({'result': 'bad', 'message': str(e)}), content_type="application/json")
    else:
        logout(request)
        return HttpResponseRedirect("/")