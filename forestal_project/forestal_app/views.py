from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Avg
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User


from .models import Postura, EscaneoPostura
from .forms import PosturaForm, RegisterForm, EspecieForm


# ----------- DASHBOARD Y AUTENTICACIÓN -----------

@login_required
def dashboard(request):
    posturas = Postura.objects.select_related('especie', 'responsable').all()
    return render(request, 'forestal_app/dashboard.html', {'posturas': posturas})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'forestal_app/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'forestal_app/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# ----------- POSTURAS -----------

@login_required
def registro_postura(request):
    if request.method == 'POST':
        form = PosturaForm(request.POST)
        if form.is_valid():
            postura = form.save(commit=False)
            postura.responsable = request.user
            postura.save()
            return redirect('listar_posturas')
    else:
        form = PosturaForm()
    return render(request, 'forestal_app/registro_postura.html', {'form': form})
    

@login_required
def editar_postura(request, id):
    postura = get_object_or_404(Postura, pk=id)

    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "No tienes permisos para editar esta postura.")
        return HttpResponseForbidden("No autorizado.")

    estado_anterior = postura.estado

    if request.method == 'POST':
        form = PosturaForm(request.POST, instance=postura)
        if form.is_valid():
            postura_editada = form.save(commit=False)
            postura_editada.responsable = request.user
            postura_editada.save()

        if estado_anterior != postura_editada.estado:
            postura_editada.guardar_historial_estado(
                postura_editada.estado,
                request.user,
                latitud=postura_editada.latitud,
                longitud=postura_editada.longitud
            )

            return redirect('detalle_postura', id=postura.id)
    else:
        form = PosturaForm(instance=postura)

    return render(request, 'forestal_app/editar_postura.html', {'form': form, 'postura': postura})


@login_required
@login_required
def listar_posturas(request):
    orden = request.GET.get('orden', '')
    filtro_responsable = request.GET.get('responsable', '')
    
    posturas = Postura.objects.select_related('responsable').all()

    if filtro_responsable:
        posturas = posturas.filter(responsable__id=filtro_responsable)

    if orden == 'estado':
        orden_custom = {
            'Adquirida': 1,
            'En Transporte': 2,
            'Almacenada': 3,
            'Sembrada': 4
        }
        posturas = posturas.order_by(
            Case(
                *[When(estado=estado, then=Value(orden_valor)) for estado, orden_valor in orden_custom.items()],
                default=Value(5),
                output_field=IntegerField()
            ),
            'responsable__username'
        )
    elif orden == 'fecha':
        posturas = posturas.order_by('-fecha_adquisicion', 'responsable__username')
    else:
        posturas = posturas.order_by('responsable__username')

    # Agrupación por responsable
    from itertools import groupby
    from operator import attrgetter

    posturas_agrupadas = {}
    for responsable, grupo in groupby(posturas, key=attrgetter('responsable')):
        posturas_agrupadas[responsable] = list(grupo)

    responsables = User.objects.filter(postura__isnull=False).distinct()

    return render(request, 'forestal_app/listar_posturas.html', {
        'posturas_agrupadas': posturas_agrupadas,
        'orden_actual': orden,
        'responsables': responsables,
        'responsable_seleccionado': filtro_responsable
    })

@login_required
def detalle_postura(request, id):
    postura = get_object_or_404(Postura, pk=id)
    return render(request, 'forestal_app/detalle_postura.html', {'postura': postura})


# ----------- ESPECIES -----------

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


# ----------- MAPA -----------

@login_required
def mapa_posturas(request):
    responsable_id = request.GET.get('responsable', '')
    responsables = User.objects.filter(postura__isnull=False).distinct()

    posturas = Postura.objects.select_related('especie', 'responsable')
    if responsable_id:
        posturas = posturas.filter(responsable__id=responsable_id)

    # Centrado por defecto (puedes ajustar a un punto central más dinámico si lo deseas)
    centro_mapa = [8.1, -81.0]  # Panamá por ejemplo
    if posturas.exists():
        centro_mapa = [
            posturas.aggregate(avg=Avg('latitud'))['avg'],
            posturas.aggregate(avg=Avg('longitud'))['avg']
        ]

    return render(request, 'forestal_app/mapa.html', {
        'posturas': posturas,
        'responsables': responsables,
        'responsable_seleccionado': responsable_id,
        'centro_mapa': centro_mapa,
    })

# ----------- ESCANEOS -----------

@login_required
def escanear_postura_view(request):
    return render(request, 'forestal_app/escanear_postura.html')


@csrf_exempt
def registrar_escaneo(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        postura_id = data.get('postura_id')
        lat = data.get('latitud')
        lng = data.get('longitud')

        if not all([postura_id, lat, lng]):
            return JsonResponse({'status': 'Faltan datos'}, status=400)

        postura = get_object_or_404(Postura, id=postura_id)

        EscaneoPostura.objects.create(
            postura=postura,
            usuario=request.user if request.user.is_authenticated else None,
            latitud=lat,
            longitud=lng
        )
        return JsonResponse({'status': 'ok'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'status': f'Error: {str(e)}'}, status=500)


@login_required
def api_postura_info(request, postura_id):
    postura = get_object_or_404(Postura, pk=postura_id)
    data = {
        "id": postura.id,
        "especie": postura.especie.nombre_comun,
        "estado": postura.estado,
        "responsable": postura.responsable.username if postura.responsable else None,
        "latitud": str(postura.latitud),
        "longitud": str(postura.longitud),
        "fecha_adquisicion": postura.fecha_adquisicion.strftime('%d/%m/%Y') if postura.fecha_adquisicion else None,
        "fecha_siembra": postura.fecha_siembra.strftime('%d/%m/%Y') if postura.fecha_siembra else None,
    }
    return JsonResponse(data)

#----Exportar informe a PDF
@login_required
def exportar_posturas_pdf(request):
    # Obtener todas las posturas registradas
    posturas = Postura.objects.all()

    # Crear la respuesta HTTP para el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_posturas.pdf"'

    # Crear el objeto canvas
    pdf = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Encabezado principal en negrita y más grande
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawCentredString(width / 2, height - 50, "Informe de Posturas Registradas")

    # Espacio antes del contenido
    y_position = height - 90

    # Fuente para el contenido general
    pdf.setFont("Helvetica", 12)

    for postura in posturas:
        pdf.drawString(100, y_position, f"Postura ID: {postura.id}")
        pdf.drawString(100, y_position - 20, f"Especie: {postura.especie.nombre_comun}")
        pdf.drawString(100, y_position - 40, f"Latitud: {postura.latitud}")
        pdf.drawString(100, y_position - 60, f"Longitud: {postura.longitud}")

        fecha_adquisicion = f"Fecha de Adquisición: {postura.fecha_adquisicion}" if postura.fecha_adquisicion else "Fecha de Adquisición: No disponible"
        fecha_siembra = f"Fecha de Siembra: {postura.fecha_siembra}" if postura.fecha_siembra else "Fecha de Siembra: No sembrada"
        pdf.drawString(100, y_position - 80, fecha_adquisicion)
        pdf.drawString(100, y_position - 100, fecha_siembra)

        pdf.drawString(100, y_position - 120, f"Estado: {postura.estado}")

        if postura.responsable:
            pdf.drawString(100, y_position - 140, f"Responsable: {postura.responsable.username}")
        else:
            pdf.drawString(100, y_position - 140, "Responsable: No asignado")

        # Línea separadora
        pdf.line(80, y_position - 155, width - 80, y_position - 155)

        # Actualizar posición
        y_position -= 170

        # Verificar si hay espacio para más posturas
        if y_position < 100:
            pdf.showPage()
            pdf.setFont("Helvetica-Bold", 16)
            pdf.drawCentredString(width / 2, height - 50, "Informe de Posturas Registradas")
            y_position = height - 90
            pdf.setFont("Helvetica", 12)

    # Guardar el archivo PDF
    pdf.save()
    return response