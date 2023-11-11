from django.urls import path, include
from . import views
from .views import CensusImportView
from .views import ExportCensusToCSV

urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('import/', CensusImportView.as_view(), name='import_census'),
    path('export_census/', ExportCensusToCSV.as_view(), name='export_census_to_csv'),
]

