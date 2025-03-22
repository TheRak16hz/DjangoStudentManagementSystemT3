from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
from accounts.forms import CustomUserCreationForm
import logging
from accounts.models import Estudiante
from .forms import StaffForm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializer import StaffSerializer
from .models import Staff
from django.contrib.auth.hashers import check_password, make_password
from .decoratos import staff_required


def home(request):
    if 'staff_id' in request.session:
        return redirect('staff_dashboard')
    elif 'user_id' in request.session:
        return redirect('user_dashboard')
    return render(request, 'home.html')

def dashboard(request):
    print(request.session['user_cedula'])
    estudiante = Estudiante.objects.filter(cedula=request.session['user_cedula']).first()  # Filtrar por cédula del usuario logueado
    print(estudiante)
    return render(request, 'users/users_dashboard.html', {'estudiante': estudiante})


logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            cedula = form.cleaned_data.get('cedula')
            email = form.cleaned_data.get('email')

            # Verificar si ya existe un usuario con esa cédula o correo
            if CustomUser.objects.filter(cedula=cedula).exists():
                messages.error(request, 'La cédula ya está registrada.')
            elif CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está registrado.')
            else:
                try:
                    form.save()
                    messages.success(request, 'Usuario registrado exitosamente.')
                    return redirect('login')
                except Exception as e:
                    messages.error(request, f'Error al registrar el usuario: {str(e)}')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        cedula = request.POST['cedula']
        password = request.POST['password']
        user = authenticate(request, cedula=cedula, password=password)
        if user is not None:
            request.session['user_cedula'] = user.cedula
            request.session['user_id'] = user.id
            print(user.id)
            login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Cédula o contraseña incorrectas')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

# staff

def login_staff(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        #print(password)

        try:
            staff = Staff.objects.get(user=username)
            if staff.check_password(password):
                # Guardar toda la información necesaria en la sesión
                request.session['staff_id'] = staff.id
                request.session['staff_name'] = staff.nombre
                request.session['staff_cedula'] = staff.cedula
                request.session['staff_correo'] = staff.correo
                request.session['staff_user'] = staff.user
                request.session['staff_role'] = staff.role
                request.session['staff_status'] = staff.status

                messages.success(request, 'Inicio de sesión exitoso.')
                return redirect('staff_dashboard')
            else:
                messages.error(request, 'Contraseña incorrecta.')
        except Staff.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
    return render(request, 'staff/login_staff.html')


def logout_staff(request):
    if 'staff_id' in request.session:
        del request.session['staff_id']
        del request.session['staff_name']
        messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('home')

@staff_required
def staff_dashboard(request):
    staff_name = request.session.get('staff_name', 'Staff')
    return render(request, 'staff/staff_dashboard.html', {'staff_name': staff_name})

@api_view(['POST'])
def register_staff(request):
    serializer = StaffSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Staff registrado exitosamente."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

