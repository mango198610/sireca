
from django.contrib.auth.models import User
from django.db import models

class Perfil (models.Model):
    nombre= models.CharField(max_length=200)
    icono = models.CharField(max_length=200,null=True)
    estado=models.BooleanField(default=True)
    pertenece=models.IntegerField(default=0)
    nivel = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

    def moduloperfil(self):
        return list(ModuloPerfil.objects.filter().values_list('modulo_id', flat=True))


class Modulo(models.Model):
    nombre= models.CharField(max_length=200)
    url= models.CharField(max_length=200,null=True,blank=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre



class ModuloPerfil(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.perfil) + ' ' + str(self.modulo)


class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"
        ordering = ['nombre']

class Canton(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)
    estado= models.BooleanField(default=True)

    def __str__(self):
         return  self.nombre

    class Meta:
        verbose_name = "Canton"
        verbose_name_plural = "Cantones"
        ordering = ['nombre']


class Sexo(models.Model):
    nombre = models.CharField(max_length=100)
    codigodatabooks=models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = "Sexo"
        verbose_name_plural = "Sexos"

    def save(self, force_insert=False, force_update=False, using=None):
        self.nombre = self.nombre.upper()
        super(Sexo, self).save(force_insert, force_update, using)



class Parroquia(models.Model):
    nombre = models.CharField(max_length=500)
    canton = models.ForeignKey(Canton, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = "Parroquia"
        verbose_name_plural = "Parroquias"
        ordering = ['nombre']

    def save(self, force_insert=False, force_update=False, using=None):
        self.nombre = self.nombre.upper()
        super(Parroquia, self).save(force_insert, force_update, using)


class Pais(models.Model):
    nombre = models.CharField(max_length=100)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = "Pais"
        verbose_name_plural = "Paises"
        ordering = ['nombre']

    @staticmethod
    def flexbox_query(q):
        return Pais.objects.filter(nombre__contains=q)


    def save(self, force_insert=False, force_update=False, using=None):
        self.nombre = self.nombre.upper()
        super(Pais, self).save(force_insert, force_update, using)

class Nacionalidad(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name = "Nacionalidad"
        verbose_name_plural = "Nacionalidades"
        ordering = ['nombre']

    def save(self, force_insert=False, force_update=False, using=None):
        self.nombre = self.nombre.upper()
        super(Nacionalidad, self).save(force_insert, force_update, using)


class TipoIdentificacion(models.Model):
    nombre = models.CharField(max_length=100, null=True)
    estado = models.BooleanField(default=True)


class Persona(models.Model):
    nombres = models.CharField(max_length=100)
    apellido1 = models.CharField(max_length=100, verbose_name="1er Apellido")
    apellido2 = models.CharField(max_length=100, verbose_name="2do Apellido", blank=True, null=True)
    extranjero = models.BooleanField(default=False)
    tipoidentificacion= models.ForeignKey(TipoIdentificacion, blank=True, null=True,on_delete=models.CASCADE)
    identificacion = models.CharField(max_length=13, blank=True, null=True)
    nacionalidad = models.ForeignKey(Nacionalidad, blank=True, null=True, on_delete=models.CASCADE)
    nacimiento = models.DateField(verbose_name=u"Fecha de Nacimiento", blank=True, null=True)
    provincia = models.ForeignKey(Provincia, verbose_name=u"Provincia de Nacimiento", blank=True, null=True,on_delete=models.CASCADE)
    canton = models.ForeignKey(Canton, verbose_name=u"Canton de Nacimiento", blank=True, null=True,on_delete=models.CASCADE)
    sexo = models.ForeignKey(Sexo, blank=True, null=True,on_delete=models.CASCADE)
    madre = models.CharField(max_length=100, blank=True, null=True)
    padre = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=100, verbose_name="Calle Principal", blank=True, null=True)
    direccion2 = models.CharField(max_length=100, verbose_name="Calle Secundaria", blank=True,null=True)
    num_direccion = models.CharField(max_length=15, verbose_name=u"Numero", blank=True,null=True)
    provinciaresid = models.ForeignKey(Provincia, related_name="ProvinciadeResidencia",
                                       verbose_name="Provincia de Residencia", blank=True, null=True,
                                       on_delete=models.CASCADE)
    cantonresid = models.ForeignKey(Canton, related_name="CantondeResidencia", verbose_name="Canton de Residencia",
                                    blank=True, null=True, on_delete=models.CASCADE)
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad de Residencia", blank=True, null=True)
    parroquia = models.ForeignKey(Parroquia, verbose_name="Parroquia", blank=True, null=True,on_delete=models.CASCADE)
    telefono = models.CharField(max_length=50, verbose_name="Telefonos Moviles", blank=True, null=True)
    telefono_conv = models.CharField(max_length=50, verbose_name="Telefonos Fijos", blank=True, null=True)
    email = models.CharField(max_length=200,blank=True, null=True, verbose_name="Correos Electronicos")
    email1 = models.CharField(max_length=200,blank=True, null=True, verbose_name="Correos Electronicos")
    email2 = models.CharField(max_length=200,blank=True, null=True, verbose_name="Correos Electronicos")
    usuario = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(blank=True, null=True)


    def nombre_completo_inverso(self):
        return "%s %s %s" % (self.apellido1, self.apellido2, self.nombres)


    def perfiles(self):
        return PerfilPersona.objects.filter(persona=self)


class PerfilPersona(models.Model):
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, blank=True, null=True, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return str(self.perfil) + ' - ' + str(self.persona)


    def modulosactivo(self):
      return AccesoModulo.objects.filter(perfilpersona=self,ver=True).order_by("modulo__nombre")


class AccesoModulo(models.Model):
    perfilpersona = models.ForeignKey(PerfilPersona, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    ingresar = models.BooleanField(default=True)
    editar = models.BooleanField(default=True)
    ver = models.BooleanField(default=True)
    eliminar = models.BooleanField(default=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return str(self.perfilpersona.perfil.nombre) + ' ' + str(
            self.perfilpersona.persona.nombre_completo_inverso()) + ' ' + str(self.modulo.nombre)


class Banco(models.Model):
    nombre = models.CharField(max_length=1000, null=True)
    estado = models.BooleanField(default=True)