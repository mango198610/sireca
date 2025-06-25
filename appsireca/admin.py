
from django.contrib import admin

from appsireca.models import ModuloPerfil, Perfil, Modulo, AccesoModulo, PerfilPersona, Pais, Provincia, Canton, \
    Parroquia, Persona, Sexo, TipoIdentificacion, Nacionalidad, SectorComercial, ActividadComercial, Cargo

admin.site.register(ModuloPerfil)
admin.site.register(Perfil)
admin.site.register(Modulo)
admin.site.register(AccesoModulo)
admin.site.register(PerfilPersona)
admin.site.register(Pais)
admin.site.register(Provincia)
admin.site.register(Canton)
admin.site.register(Parroquia)
admin.site.register(Persona)
admin.site.register(Sexo)
admin.site.register(TipoIdentificacion)
admin.site.register(Nacionalidad)
admin.site.register(SectorComercial)
admin.site.register(ActividadComercial)
admin.site.register(Cargo)