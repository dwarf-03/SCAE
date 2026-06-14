from django.db import models
from usuarios.models import Usuario

class Cliente(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('cc', 'Cédula de Ciudadanía'),
        ('ce', 'Cédula de Extranjería'),
        ('nit', 'NIT'),
        ('pasaporte', 'Pasaporte'),
    ]

    # Usuario del sistema asociado al cliente
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='cliente')
    
    # Tipo y número de documento de identidad
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, default='cc')
    numero_documento = models.CharField(max_length=20, unique=True)
    
    # Información de contacto
    telefono = models.CharField(max_length=20)
    telefono_alternativo = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    
    # Documento de identidad escaneado
    foto_documento = models.ImageField(upload_to='documentos/', blank=True, null=True)
    
    # Indica si el cliente está verificado por un empleado
    verificado = models.BooleanField(default=False)
    
    # Indica si el cliente tiene deudas pendientes
    tiene_deuda = models.BooleanField(default=False)
    
    # Monto total de deuda acumulada
    deuda_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Observaciones internas del cliente
    notas = models.TextField(blank=True, null=True)
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f'{self.usuario.get_full_name()} - {self.numero_documento}'

    @property
    def nombre_completo(self):
        # Retorna el nombre completo del usuario asociado
        return self.usuario.get_full_name()

    @property
    def email(self):
        # Retorna el email del usuario asociado
        return self.usuario.email

    @property
    def total_alquileres(self):
        # Cuenta todos los alquileres del cliente
        return self.alquileres.count()

    @property
    def alquileres_activos(self):
        # Retorna alquileres en curso del cliente
        return self.alquileres.filter(estado='activo').count()


class DocumentoCliente(models.Model):
    TIPO_CHOICES = [
        ('identificacion', 'Identificación'),
        ('contrato', 'Contrato'),
        ('otro', 'Otro'),
    ]

    # Cliente al que pertenece el documento
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='documentos')
    
    # Tipo de documento adjunto
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Archivo del documento
    archivo = models.FileField(upload_to='documentos/clientes/')
    
    # Descripción opcional del documento
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f'{self.cliente} - {self.tipo}'