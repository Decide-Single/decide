from django.urls import path, include
from . import views
from .views import CensusImportView
from .views import CensusExportView
from .views import ExportCensusToCSV
from .views import ExportCensusToJSON
from .views import ExportCensusToXLSX
from .views import ExportCensusToXML


urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('export/export_census_csv/', ExportCensusToCSV.as_view(), name='export_census_to_csv'),
    path('export/export_census_json/', ExportCensusToJSON.as_view(), name='export_census_to_json'),
    path('export/export_census_xlsx/', ExportCensusToXLSX.as_view(), name='export_census_to_xlsx'),
    path('export/export_census_xml/', ExportCensusToXML.as_view(), name='export_census_to_xml'),
    path('export/', CensusExportView.as_view(), name='export_census'),
    path('import/', CensusImportView.as_view(), name='import_census'),
]

