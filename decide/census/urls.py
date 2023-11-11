from django.urls import path, include
from . import views
from .views import CensusImportView
from .views import ExportCensusToCSV
from .views import ExportCensusToJSON


urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('export_census_csv/', ExportCensusToCSV.as_view(), name='export_census_to_csv'),
    path('export_census_json/', ExportCensusToJSON.as_view(), name='export_census_to_json'),
    path('import/', CensusImportView.as_view(), name='import_census'),
]

