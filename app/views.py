from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .vm_form import VMForm, get_form_fields_info
from .vm_list import VMList
from . import context_processors
from .register_form import CustomUserCreationForm
from uuid import uuid4
from xml.etree import ElementTree
from xml.dom import minidom
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from app.api.domains import list_dom_info_uuid, list_all_domain, list_dom_info_name


def index(request):
    return render(request, 'app/index.html')


@login_required
def new_vm(request):
    if request.method == "POST":
        form = VMForm(request.POST)
        if form.is_valid():
            vm_data = form.cleaned_data
            vm_name = vm_data['name']
            # selon le RFC4122
            uuid = str(uuid4())

            root = ElementTree.Element("VM")
            ElementTree.SubElement(root, "name").text = vm_name
            ElementTree.SubElement(root, "uuid").text = uuid

            system = ElementTree.SubElement(root, "system")
            for key, value in vm_data.items():
                if key != 'name':
                    ElementTree.SubElement(system, key).text = str(value)

            try:
                xml_str = ElementTree.tostring(root, encoding='unicode')
                xml_pretty = minidom.parseString(xml_str).toprettyxml(indent="    ")

                with open(f'tmp./{vm_name}_{uuid}.xml', 'w') as f:
                    f.write(xml_pretty)

                return HttpResponse(context_processors.CREATE_VM_SUCCESS)
            except Exception as e:
                print(e)
                return HttpResponse(f"{context_processors.CREATE_VM_ERROR} : {e}")
        else:
            fields_info = get_form_fields_info()
            errors = form.errors
            return render(request, 'app/new_vm.html', {'fields_info': fields_info, 'errors': errors, 'form': form})
    else:
        form = VMForm()
        fields_info = get_form_fields_info()
        return render(request, 'app/new_vm.html', {'fields_info': fields_info, 'form': form})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                form.add_error('email', context_processors.ERROR_EMAIL_EXISTS)
                return render(request, 'registration/register.html', {'form': form})
            else:
                user = form.save()
                auth_login(request, user)
                return redirect('index')
        else:
            return render(request, 'registration/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
            if user.check_password(password):
                auth_login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Mot de passe ou email invalide.')
        except user_model.DoesNotExist:
            messages.error(request, 'Mot de passe ou email invalide.')
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})
    else:
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'app/profile.html', {'user': request.user})


@login_required
def informations(request):
    user = request.user
    username = user.username
    email = user.email
    return render(request, 'app/informations.html', {'username': username, 'email': email})


@login_required
def securite(request):
    return render(request, 'app/security.html')


@login_required
def vm_list(request):
    if request.method == 'POST':
        action = request.POST.get('action').upper()
        vm_uuid = request.POST.get('data_id')

        if action == 'CONSOLE VIEW':
            if vm_uuid:
                return redirect('vm_view', vm_uuid=vm_uuid)
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid VM UUID'})

        return JsonResponse({'status': 'success'})

    vms_list = list_all_domain()
    vms = []

    for vm in vms_list:
        if vm is not None:
            vms.append(list_dom_info_name(vm[0]))

    print(vms)

    return render(request, 'app/vm_list.html', {'vms': vms})


@login_required
def vm_view(request, vm_uuid):
    vm = list_dom_info_uuid(vm_uuid)
    print(vm.name)

    websocket_url = f'ws://127.0.0.1:6080'
    return render(request, 'app/view.html', {'websocket_url': websocket_url})

