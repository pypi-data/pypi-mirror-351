from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse

# Import domain-specific exceptions
from [[ app_name.lower() ]].domain.exceptions import EntityNotFoundError

# Import entity-specific forms
from [[ app_name.lower() ]].[[ entity_name.lower() ]]_forms import [[ entity_name.capitalize() ]]CreateForm, [[ entity_name.capitalize() ]]EditForm, [[ entity_name.capitalize() ]]ViewForm

# Import domain-specific services
from [[ app_name.lower() ]].domain.services import (
    list_[[ entity_name.lower() ]],
    create_[[ entity_name.lower() ]],
    retrieve_[[ entity_name.lower() ]],
    update_[[ entity_name.lower() ]],
    delete_[[ entity_name.lower() ]],
)

# Import infrastructure-specific repositories
from [[ app_name.lower() ]].infrastructure.[[ entity_name.lower() ]]_repository import [[ entity_name.capitalize() ]]Repository


def [[ entity_name.lower() ]]_list(request):
    """
    Generic view to display a list of all [[ entity_name.lower() ]] instances.
    """

    [[ entity_name.lower() ]]List = [] #inicialize list

    # Get data from the repository
    try:
        repository = [[ entity_name.capitalize() ]]Repository()
        [[ entity_name.lower() ]]List = list_[[ entity_name.lower() ]](repository=repository)

    except ValueError as e:
        # Handling domain-specific errors
        messages.error(request,  str(e))

    #  Render the view with the data
    return render(request, '[[ app_name.lower() ]]/[[ entity_name.lower() ]]_web_list.html', {
        '[[ entity_name.lower() ]]List': [[ entity_name.lower() ]]List
    })


def [[ entity_name.lower() ]]_create(request):
    """
    Generic view to create a new [[ entity_name.lower() ]] instance using a service.
    """

    if request.method == "POST":

        # Validate form data
        form = [[ entity_name.capitalize() ]]CreateForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data
            repository = [[ entity_name.capitalize() ]]Repository()

            try:
                # Call the creation service
                create_[[ entity_name.lower() ]](repository=repository, data=form_data)

                # Display success message and redirect
                messages.success(request, f"Successfully created [[ entity_name.lower() ]].")
                return redirect('[[ entity_name.lower() ]]_list')

            except ValueError as e:
                # Handling domain-specific errors
                form.add_error(None, str(e))
        else:
            messages.error(request, "There were errors in the form. Please correct them.")
    else:
        # Empty form for GET requests
        form = [[ entity_name.capitalize() ]]CreateForm()

    # Render the template with the form
    return render(request, '[[ app_name.lower() ]]/[[ entity_name.lower() ]]_web_create.html', {'form': form}) 


def [[ entity_name.lower() ]]_edit(request, id=None):
    """
    Generic view to edit an existing [[ entity_name.lower() ]] instance using a service.
    """

    if id is None:
        # Redirect if ID is not present
        return redirect('[[ entity_name.lower() ]]_list')

    repository = [[ entity_name.capitalize() ]]Repository()

    try:
        # Obtain service data
        [[ entity_name.lower() ]] = retrieve_[[ entity_name.lower() ]](repository=repository, entity_id=id)

    except EntityNotFoundError as e:
        # Handling domain-specific errors
        messages.error(request,  str(e))
        return redirect('[[ entity_name.lower() ]]_list')

    except ValueError as e:
        # Handling domain-specific errors
        messages.error(request,  str(e))
        return redirect('[[ entity_name.lower() ]]_list')

    if request.method == "POST":

        # Validate form data
        form = [[ entity_name.capitalize() ]]EditForm(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data

            try:
                # remove readonly parameters from data
                form_data.pop('id', None)

                # Call the update service
                update_[[ entity_name.lower() ]](repository=repository, entity_id=id, data=form_data)

                # Display success message
                messages.success(request, f"Successfully updated [[ entity_name.lower() ]].")

                # Redirect to the list of [[ entity_name.lower() ]]s
                return redirect('[[ entity_name.lower() ]]_list')

            except EntityNotFoundError as e:
                form.add_error(None, str(e))

            except ValueError as e:
                form.add_error(None, str(e))

        else:
            messages.error(request, "There were errors in the form. Please correct them.")

    # request.method == "GET":
    else:  
        # Initialize the form with existing data
        form = [[ entity_name.capitalize() ]]EditForm(initial={
            'id': [[ entity_name.lower() ]]['id'],            
            'name': [[ entity_name.lower() ]]['name'],
            'email': [[ entity_name.lower() ]]['email']
        })

    # Render the template with the form
    return render(request, '[[ app_name.lower() ]]/[[ entity_name.lower() ]]_web_edit.html', {'form': form})


def [[ entity_name.lower() ]]_detail(request, id=None):
    """
    Generic view to display details of a specific [[ entity_name.lower() ]] instance.
    """
    if id is None:
        return redirect('[[ entity_name.lower() ]]_list')

    repository = [[ entity_name.capitalize() ]]Repository()
    try:
        # Get entity data from the service
        [[ entity_name.lower() ]] = retrieve_[[ entity_name.lower() ]](repository=repository, entity_id=id)

    except EntityNotFoundError as e:
        # Handling domain-specific errors
        messages.error(request,  str(e))
        return redirect('[[ entity_name.lower() ]]_list')

    except ValueError as e:
        # Handling domain-specific errors
        messages.error(request,  str(e))
        return redirect('[[ entity_name.lower() ]]_list')

    # Render details with a read-only form
    form = [[ entity_name.capitalize() ]]ViewForm(initial={
        'name': [[ entity_name.lower() ]]['name'],
        'email': [[ entity_name.lower() ]]['email']
    })

    return render(request, '[[ app_name.lower() ]]/[[ entity_name.lower() ]]_web_detail.html', {'form': form})


def [[ entity_name.lower() ]]_delete(request, id=None):
    """
    Generic view to delete an existing [[ entity_name.lower() ]] instance using a service.
    """
    if id is None:
        messages.error(request, "Non Valid id to delete")
        return redirect('[[ entity_name.lower() ]]_list')

    repository = [[ entity_name.capitalize() ]]Repository()
    try:
        # Call the disposal service
        delete_[[ entity_name.lower() ]](repository=repository, entity_id=id)
        messages.success(request, f"Successfully deleted [[ entity_name.lower() ]].")

    except EntityNotFoundError as e:
        # Handling domain-specific errors
        messages.error(request,  str(e))
        
    except ValueError as e:
        # Handling domain-specific errors
        messages.error(request,  str(e))

    return redirect('[[ entity_name.lower() ]]_list')

