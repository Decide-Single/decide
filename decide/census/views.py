import csv
import json
import openpyxl

from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from rest_framework import generics
from rest_framework.response import Response
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from openpyxl import load_workbook
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

from datetime import datetime
from base.perms import UserIsStaff
from .models import Census


class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    # Ajusta las vistas para agregar funcionalidad de filtrado

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        sex = request.GET.get('sex')
        locality = request.GET.get('locality')
        vote_date = request.GET.get('vote_date')
        has_voted = request.GET.get('has_voted')
        vote_result = request.GET.get('vote_result')
        vote_method = request.GET.get('vote_method')

        queryset = Census.objects.filter(voting_id=voting_id)

        # Filtrar por campos adicionales
        if sex:
            queryset = queryset.filter(sex=sex)
        if locality:
            queryset = queryset.filter(locality=locality)
        if vote_date:
            queryset = queryset.filter(vote_date=vote_date)
        if has_voted:
            queryset = queryset.filter(has_voted=has_voted.lower() == 'true')
        if vote_result:
            queryset = queryset.filter(vote_result=vote_result)
        if vote_method:
            queryset = queryset.filter(vote_method=vote_method)

        voters = queryset.values_list('voter_id', flat=True)
        return Response({'voters': voters})



class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')

class CensusExportView(View):

    template_name='export_census.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request):
        # Obtener el valor del botón presionado
        export_format = request.POST.get('export_format')

        # Definir las URL correspondientes a cada formato de exportación
        url_mapping = {
        'csv': 'export_census_csv/',
        'json': 'export_census_json/',
        'xlsx': 'export_census_xlsx/',
    }

        if export_format in url_mapping:
            return HttpResponseRedirect(url_mapping[export_format])
        else:
            # Manejar el caso en el que no se seleccionó un formato válido
            return render(request, 'export_census.html', {'error_message': 'Export format not valid.'})


class CensusImportView(View):

    template_name = 'import_census.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            file = request.FILES.get('file')
            if file:
                try:
                    if file.content_type == 'text/csv':
                        decoded_file = file.read().decode('utf-8').splitlines()
                        reader = csv.reader(decoded_file)
                        for index, row in enumerate(reader):
                            voting_id, voter_id = row
                            Census.objects.create(voting_id=voting_id, voter_id=voter_id)
                        return JsonResponse({'message': 'Census imported successfully'}, status=201)

                    elif file.content_type == 'application/json':
                        data = json.loads(file.read().decode('utf-8'))
                        for item in data:
                            voting_id, voter_id = item['voting_id'], item['voter_id']
                            Census.objects.create(voting_id=voting_id, voter_id=voter_id)
                        return JsonResponse({'message': 'Census imported successfully'}, status=201)

                    elif file.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                        workbook = load_workbook(file, read_only=True)
                        sheet = workbook.active

                        for row in sheet.iter_rows(min_row=2, values_only=True):
                            voting_id, voter_id = row
                            Census.objects.create(voting_id=voting_id, voter_id=voter_id)

                        return JsonResponse({'message': 'Census imported successfully'}, status=201)


                    else:
                        return JsonResponse({'error': 'Unsupported file format'}, status=400)
                except Exception as e:
                    return JsonResponse({'error': 'Error trying to create census: {}'.format(str(e))}, status=409)
            else:
                return JsonResponse({'error': 'Invalid or no file provided'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)

class ExportCensusToCSV(View):

    def get(self, request):
        # Obtiene todos los datos del censo que deseas exportar
        census_data = Census.objects.all()

        # Exporta los datos a CSV
        response = self.export_to_csv(census_data)

        return response

    def export_to_csv(self, census_data):
        # Crea una respuesta HTTP con el tipo de contenido adecuado para un archivo CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="census.csv"'

        # Crea un escritor CSV y escribe los encabezados
        writer = csv.writer(response)
        writer.writerow(['Voting ID', 'Voter ID'])

        # Escribe los datos del censo en el archivo CSV
        for census in census_data:
            writer.writerow([census.voting_id, census.voter_id])

        return response

class ExportCensusToJSON(View):

    def get(self, request):
        census_data = Census.objects.all()
        response = self.export_to_json(census_data)
        return response

    def export_to_json(self, census_data):
        # Crear una estructura de datos que se convertirá a JSON
        export_data = []
        for census in census_data:
            export_data.append({
                'voting_id': census.voting_id,
                'voter_id': census.voter_id,
            })

        json_data = json.dumps(export_data, indent=2, default=str)

        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="census.json"'

        return response


class ExportCensusToXLSX(View):

    def get(self, request):
        census_data = Census.objects.all()
        response = self.export_to_excel(census_data)
        return response

    def export_to_excel(self, census_data):
        if not census_data:
            # Manejar el caso en que no haya datos en el censo
            return HttpResponse('No hay datos para exportar a Excel.', status=204)

        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Agrega encabezados dinámicamente basándote en los campos del modelo Census
        headers = [field.name for field in Census._meta.get_fields()]
        worksheet.append(headers)

        # Agrega datos del censo
        for census in census_data:
            data_row = [getattr(census, field) for field in headers]
            worksheet.append(data_row)

        # Genera un nombre de archivo dinámico con la fecha actual
        file_name = f"census_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        workbook.save(response)

        # Cierra el libro de trabajo para liberar recursos
        workbook.close()

        return response