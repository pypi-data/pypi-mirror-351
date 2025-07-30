from django import forms
from django.core import validators
from django.core.validators import (
    MinLengthValidator,
    MaxLengthValidator,
    RegexValidator,
    EmailValidator,
    MinValueValidator,
    MaxValueValidator,
)


class [[ entity_name.capitalize() ]]BaseForm(forms.Form):
    """
    Base Form
    """

    # Campo de texto y numeros (Nombre)
    name = forms.CharField(
        label="Name",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'minlength': '3',  # HTML5 validación
            'maxlength': '100',  # HTML5 validación
            'pattern': r'^[A-Za-z0-9ñÑáéíóúÁÉÍÓÚ ]*$',  # Expresión regular en el navegador
            'title': 'The name must only contain letters, numbers, and spaces.'  # Mensaje de ayuda                          
        }),
        validators=[
            MinLengthValidator(3, "The name must be at least 3 characters."),
            MaxLengthValidator(100, "The name must not exceed 100 characters."),
            RegexValidator(r'^[A-Za-z0-9ñÑáéíóúÁÉÍÓÚ ]*$', 'The name must only contain letters, numbers, and spaces.'),
        ]
    )

    # Campo de texto (Category)
    category = forms.CharField(
        label='Category',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'minlength': '4',  # Mínima longitud en el navegador
            'maxlength': '250',  # Máxima longitud en el navegador      
            'pattern': r'^[A-Za-z\s]*$',  # Expresión regular en el navegador           
            'title': 'The name can only contain letters and spaces.'
        }),
        validators=[
            MinLengthValidator(4, "The name must be at least 4 characters."),
            MaxLengthValidator(250, "The name must not exceed 250 characters."),
            RegexValidator(r'^[A-Za-z\s]*$', "The name can only contain letters and spaces."),
        ]          
    ) 

    # Campo de correo electrónico
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
        }),
        validators=[
            EmailValidator("Please enter a valid email address."),
        ]
    )

    # Campo de contraseña
    password = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password',
            'minlength': '8',
        }),
        validators=[
            MinLengthValidator(8, "Password must be at least 8 characters long."),
        ]
    )

    # Campo numérico
    age = forms.IntegerField(
        label="Age",
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '18',  # HTML5 validación
            'max': '100',  # HTML5 validación
            'placeholder': 'Enter your age',
        }),
        validators=[
            MinValueValidator(18, "You must be at least 18 years old."),
            MaxValueValidator(100, "The age must not exceed 100."),
        ]
    )

    # Campo de fecha
    birth_date = forms.DateField(
        label="Birth Date",
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',  # HTML5 tipo fecha
        })
    )

    # Selección desplegable
    country = forms.ChoiceField(
        label="Country",
        required=True,
        choices=[
            ('', 'Select your country'),
            ('us', 'United States'),
            ('es', 'Spain'),
            ('mx', 'Mexico'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
        })  
    )

    # Opciones de radio
    gender = forms.ChoiceField(
        label="Gender",
        required=True,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        })
    )

    # Casillas de verificación
    accept_terms = forms.BooleanField(
        label="I accept the terms and conditions",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        error_messages={
            'required': "You must accept the terms and conditions to proceed.",
        }
    )

    def clean_name(self):
        '''
        Esta validacion es solo para el campo 'name'
        '''    
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise forms.ValidationError("The name must be at least 3 characters long.")
        return name    

    def clean_email(self):
        '''
        Esta validacion es solo para el campo 'email'
        '''
        email = self.cleaned_data.get('email')
        if email.endswith('@example.com'):
            raise forms.ValidationError("Emails from example.com are not allowed.")
        return email

    def clean(self):
        '''
        Aqui podemos hacer validaciones que involucren a varios campos
        '''
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")


class [[ entity_name.capitalize() ]]CreateForm([[ entity_name.capitalize() ]]BaseForm):
    """
    Form to create a new instance of [[ entity_name.lower() ]]. Sin modificaciones adicionales.
    """
    #Permitimos que el email sea editable
    [[ entity_name.capitalize() ]]BaseForm.base_fields['email'].widget.attrs.update({
        'readonly': False,
    })


class [[ entity_name.capitalize() ]]EditForm([[ entity_name.capitalize() ]]BaseForm):
    """
    Form to edit an instance of [[ entity_name.lower() ]]. 
    """
    #Agregamos un campo adicional para 'id' Oculto para el POST
    id = forms.IntegerField(
        label='ID',
        required=False,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)     

        #impedimos que el email sea editable 
        self.email.widget.attrs.update({
            'readonly': 'True'
        })


class [[ entity_name.capitalize() ]]ViewForm([[ entity_name.capitalize() ]]BaseForm):
    """
    Readonly form to view an instance of [[ entity_name.lower() ]]
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hacer todos los campos no editables
        for field in self.fields.values():
            field.widget.attrs['disabled'] = True








            
'''
Flujo de Validación en Django Forms

Cuando se llama al método is_valid() de un formulario, Django realiza las siguientes acciones de manera secuencial:

1. Limpiar los datos de entrada crudos
    Antes de cualquier validación, Django toma los datos enviados ( o  en formularios de tipo GET) y los procesa en el objeto . 
    Esto incluye convertir los valores en tipos de datos que Django pueda interpretar.

2. Validación de los campos individuales
    Django valida cada campo del formulario según las reglas especificadas en el formulario o en el modelo asociado. 
    Este proceso incluye:
    
    Validadores básicos del campo:
    - Validación de tipo: Por ejemplo, un campo 'forms.integerField' asegura que el valor sea un entero.
    - Validación de valores requeridos: Si el campo tiene 'required=True' y no se proporciona ningún valor, se genera un error.
    - Validación de longitud: En campos como 'CharField', 'max_length' y 'min_length' son comprobados.
    - Validación de opciones: En campos como 'Choice_Field', el valor debe ser una de las opciones definidas

    Validadores específicos: Los validadores personalizados definidos en el propio campo o como funciones adicionales se ejecutan

3. Métodos 'clean_<nombr_campo>'
    Django busca métodos personalizados para los campos del formulario, siguiendo la convención 'clean_<nombr_campo>'. 
    Si existen, estos métodos se ejecutan después de las validaciones básicas del campo.

    Ejemplo:

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith("@example.com"):
            raise forms.ValidationError("Only example.com emails are allowed.")
        return email

    Los errores generados por estos métodos se almacenan en el atributo 'form.field_name.errors'.

4. Métodos 'clean()' generales
    Una vez que todos los campos han sido validados individualmente, Django llama al método 'clean()'  general del formulario. 
    Este método es útil para validar dependencias entre múltiples campos.
    Por ejemplo:

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")

    Los errores de este método se almacenan en 'form.errors' como errores globales, no asociados a un campo específico.

5. Almacenar los datos validados
    Si no hay errores, los valores procesados y validados se almacenan en el atributo 'form.cleaned_data', 
    que es un diccionario con los datos del formulario que pasaron la validación.

'''