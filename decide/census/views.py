from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.views import View
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

import csv
import json
from django.http import HttpResponse

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

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
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

