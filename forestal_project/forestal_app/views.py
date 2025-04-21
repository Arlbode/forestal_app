from django.shortcuts import render, redirect
from .models import Postura
from .forms import PosturaForm, RegisterForm, EspecieForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField

@login_required
def dashboard(request):
    posturas = Postura.objects.all()
    return render(request, 'forestal_app/dashboard.html', {'posturas': posturas})

@login_required
def registro_postura(request):
    form = PosturaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'forestal_app/registro_postura.html', {'form': form})

@login_required
def ver_mapa(request):
    posturas = Postura.objects.all()
    return render(request, 'forestal_app/mapa.html', {'posturas': posturas})

@login_required
def registrar_especie(request):
    if request.method == 'POST':
        form = EspecieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registro_postura')
    else:
        form = EspecieForm()
    return render(request, 'forestal_app/registro_especie.html', {'form': form})

@login_required
def listar_posturas(request):
    # Obtener parámetro de ordenamiento de la URL
    orden = request.GET.get('orden', 'estado')  # Por defecto ordenar por estado
    
    # Definir el ordenamiento
    if orden == 'fecha':
        posturas = Postura.objects.all().order_by('fecha_siembra', 'especie__nombre_comun')
    else:
        # Orden personalizado para que los estados aparezcan en el orden definido
        posturas = Postura.objects.annotate(
            orden_estado=Case(
                When(estado='Adquirida', then=Value(1)),
                When(estado='En Transporte', then=Value(2)),
                When(estado='Almacenada', then=Value(3)),
                When(estado='Sembrada', then=Value(4)),
                output_field=IntegerField(),
            )
        ).order_by('orden_estado', 'especie__nombre_comun')
    
    context = {
        'posturas': posturas,
        'orden_actual': orden,
    }
    return render(request, 'forestal_app/listar_posturas.html', context)


def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'forestal_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'forestal_app/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
