from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import Census

class StatusFilter(admin.SimpleListFilter):
    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('activo', 'Activo'),
            ('desactivado', 'Desactivado'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'activo':
            return queryset.filter(creation_date__gte=(timezone.now() - timedelta(days=7)))
        elif self.value() == 'desactivado':
            return queryset.exclude(creation_date__gte=(timezone.now() - timedelta(days=7)))
        return queryset

class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id', 'creation_date', 'additional_info', 'get_status', 'get_total_voters')
    search_fields = ('voter_id', )
    list_filter = ('voting_id', 'creation_date', StatusFilter)  # Usamos la clase StatusFilter

    def get_status(self, obj):
        return obj.get_status()

    get_status.admin_order_field = 'creation_date'  # Campo utilizado para ordenar

    def get_total_voters(self, obj):
        return obj.get_total_voters()

    get_total_voters.admin_order_field = 'creation_date'  # Campo utilizado para ordenar

admin.site.register(Census, CensusAdmin)
