class [[ serializer_name.capitalize() ]]Serializer:
    """
    Serializer Object para [[ serializer_name.lower() ]].

    Este Serializer se utiliza para transferir datos entre capas del sistema, 
    como entre la capa de dominio y vistas en Django REST Framework (DRF).
    """

    # Ejemplo de atributos. Personaliza según tus necesidades.
    id:  serializers.IntegerField(read_only=True)
    name: serializers.CharField()
    email: serializers.EmailField()
        
    external_id: serializers.CharField()  # Identificador externo, como un UUID público
    slug: serializers.SlugField()  # Identificador único legible para URLs
    title: serializers.CharField()  # Título de la entidad
    content: serializers.CharField()  # Contenido breve o resumen
    price: serializers.DecimalField(max_digits=10, decimal_places=2)  # Precio o valor numérico
    quantity: serializers.IntegerField()  # Cantidad disponible o asociada
    rating: serializers.FloatField()  # Valoración media (ej. 4.5 estrellas)
    is_active: serializers.BooleanField(default=True)  # Estado activo/inactivo
    is_featured: serializers.BooleanField(default=False)  # Si es destacado/promocionado
    created_at: serializers.DateTimeField(read_only=True)  # Fecha de creación
    updated_at: serializers.DateTimeField(read_only=True)  # Fecha de última modificación
    deleted_at: serializers.DateTimeField(allow_null=True)  # Fecha de eliminación o "soft delete"
    parent_id: serializers.IntegerField(allow_null=True)  # Llave foránea hacia una entidad padre
    owner_id: serializers.IntegerField(allow_null=True)  # Llave foránea hacia el usuario propietario
    tags: serializers.ListField(child=serializers.CharField(), allow_null=True)  # Lista de etiquetas (relación Many-to-Many)
    image_url: serializers.URLField(allow_null=True)  # URL hacia una imagen asociada
    video_url: serializers.URLField(allow_null=True)  # URL hacia un video asociado
    latitude: serializers.FloatField(allow_null=True)  # Coordenada de latitud
    longitude: serializers.FloatField(allow_null=True)  # Coordenada de longitud
    location_name: serializers.CharField(allow_null=True)  # Nombre del lugar (dirección o ciudad)
    created_by: serializers.IntegerField(allow_null=True)  # Usuario que creó la entidad
    updated_by: serializers.IntegerField(allow_null=True)  # Usuario que actualizó la entidad
    order_status: serializers.ChoiceField(choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], allow_null=True)  # Estado de la orden (e.g., "PENDING", "COMPLETED")
    total_price: serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)  # Precio total de la orden
    items: serializers.ListField(child=serializers.DictField(), allow_null=True)  # Lista de artículos asociados    

