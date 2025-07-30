@dataclass
class [[ entity_name.capitalize() ]]Entity:
    """
    Entidad del dominio para [[ entity_name.lower() ]].

    Esta clase representa la lógica de negocio central y las reglas asociadas 
    con [[ entity_name.lower() ]] en el sistema.
    """
    #campos id
    id: Optional[int] = None  # ID relacionado con la base de datos
    uuid: Optional[UUID] = None

    name: str  # Nombre obligatorio
    email: str  # Email obligatorio

    # Descomentar si se quiere hacer una validacion estricta
    #def __post_init__(self):
    #    self.validate()   

    def validate(self) -> None:
        """
        Valida la entidad antes de guardar o procesar.
        Lanza excepciones si las reglas de negocio no se cumplen.
        - Consistencia interna de los atributos
        - Validaciones intrínsecas al momento de creación/modificación
        """
        if not self.name or len(self.name) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres.")
        if self.description and len(self.description) > 500:
            raise ValueError("La descripción no puede superar los 500 caracteres.")

    def update(self, data:dict, addMode:bool = False) -> None:
        """
        Actualiza los atributos de la entidad con valores nuevos.
        si addMode = True permite añadir campos nuevos
        """
        # Actualizar cada campo proporcionado en 'data'
        for key, value in data.items():
            if hasattr(self, key) or addMode:
                setattr(self, key, value)             

        self.validate()    

    def to_dict(self) -> dict:
        """
        Convierte la entidad a un diccionario.
        """
        return self.__dict__

    @staticmethod
    def from_dict(data: dict) -> "[[ entity_name.capitalize() ]]Entity":
        """
        Crea una instancia de la entidad a partir de un diccionario.
        """

        # aqui quitaremos de 'data' los campos no deseados para la entity

        #retornar la entity
        return [[ entity_name.capitalize() ]]Entity(**data)
        

'''
Ejemplos de campos adicionales:

external_id: Optional[str] = None  # Identificador externo, como un UUID público
slug: Optional[str] = None  # Identificador único legible para URLs
title: str  # Título de la entidad
content: Optional[str] = None  # Contenido detallado o descripción extensa
price: Optional[float] = None  # Precio o valor numérico
quantity: Optional[int] = None  # Cantidad disponible o asociada
rating: Optional[float] = None  # Valoración media (ej. 4.5 estrellas)
is_active: bool = True  # Estado activo/inactivo
is_featured: Optional[bool] = None  # Si es destacado/promocionado
updated_at: Optional[str] = None  # Fecha de última modificación (ISO 8601)
deleted_at: Optional[str] = None  # Fecha de eliminación o "soft delete"
parent_id: Optional[int] = None  # Llave foránea hacia una entidad padre
owner_id: Optional[int] = None  # Llave foránea hacia el usuario propietario
tags: Optional[List[str]] = None  # Lista de etiquetas (relación Many-to-Many)
image_url: Optional[str] = None  # URL hacia una imagen asociada
video_url: Optional[str] = None  # URL hacia un video asociado
latitude: Optional[float] = None  # Coordenada de latitud
longitude: Optional[float] = None  # Coordenada de longitud
location_name: Optional[str] = None  # Nombre del lugar (dirección o ciudad)
created_by: Optional[int] = None  # Usuario que creó la entidad
updated_by: Optional[int] = None  # Usuario que actualizó la entidad
order_status: Optional[str] = None  # Estado de la orden (e.g., "PENDING", "COMPLETED")
total_price: Optional[float] = None  # Precio total de la orden
items: Optional[List[Dict]] = None  # Lista de artículos asociados
'''