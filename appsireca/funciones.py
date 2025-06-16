import json

import unicodedata
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import HttpResponse

from appsireca.models import Canton
from sireca.settings import LETRAS_ABECEDARIO_MIN


def elimina_tildes(cadena):
    s = ''.join((c for c in unicodedata.normalize('NFD',str(cadena)) if unicodedata.category(c) != 'Mn'))
    return s
class MiPaginador(Paginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True, rango=5):
        super(MiPaginador,self).__init__(object_list, per_page, orphans=orphans, allow_empty_first_page=allow_empty_first_page)
        self.rango = rango
        self.paginas = []
        self.primera_pagina = False
        self.ultima_pagina = False

    def rangos_paginado(self, pagina):
        left = pagina - self.rango
        right = pagina + self.rango
        if left<1:
            left=1
        if right>self.num_pages:
            right = self.num_pages
        self.paginas = range(left, right+1)
        self.primera_pagina = True if left>1 else False
        self.ultima_pagina = True if right<self.num_pages else False
        self.ellipsis_izquierda = left-1
        self.ellipsis_derecha = right+1

def ip_client_address(request):
    try:
        # case server externo
        client_address = request.META['HTTP_X_FORWARDED_FOR']
    except:
        # case localhost o 127.0.0.1
        client_address = request.META['REMOTE_ADDR']
    return client_address


def calculate_username(persona, variant=''):
    s = persona.nombres.lower().split(' ')
    while '' in s:
        s.remove('')
    if len(s) > 1:
        if persona.apellido2:
            usernamevariant = s[0][0] + s[1][0] + elimina_tildes(persona.apellido1.lower())+elimina_tildes(persona.apellido2.lower())[0]
        else:
            usernamevariant = s[0][0] + s[1][0] + elimina_tildes(persona.apellido1.lower())[0]
    else:
        if persona.apellido2:
            usernamevariant = s[0][0] + elimina_tildes(persona.apellido1.lower())+elimina_tildes(persona.apellido2.lower())[0]
        else:
            usernamevariant = s[0][0] + elimina_tildes(persona.apellido1.lower())[0]
    usernamevariant = usernamevariant.replace(' ', '').replace(u'Ñ', 'n').replace(u'ñ', 'n')
    if variant != '':
        usernamevariant += str(variant)
    if User.objects.filter(username=usernamevariant).count() == 0:
        return usernamevariant
    else:
        if '_' in usernamevariant:
            numero = len(usernamevariant.split('_')[1])
            return calculate_username(persona, '_' + usernamevariant.split('_')[1] + LETRAS_ABECEDARIO_MIN[numero])
        else:
            return calculate_username(persona, '_'+LETRAS_ABECEDARIO_MIN[User.objects.filter(username=usernamevariant).count()-1])

def buscarcanton(idprovincia, strnombre):
    listCan = [{"id": 0, "nombre": "Seleccionar el Cantón"}]
    try:
        model = (
            Canton.objects.filter(provincia_id=idprovincia)
            if idprovincia > 0
            else Canton.objects.filter(nombre__icontains=strnombre)
        )
        for g in model.order_by("nombre"):
            listCan.append({"id": g.id, "nombre": g.nombre})
        return listCan
    except Exception as e:
        return listCan

