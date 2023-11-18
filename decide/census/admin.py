from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from .models import Census
from store.models import Vote
from django.db import models

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


class HasVotedFilter(admin.SimpleListFilter):
    title = ('Votado')
    parameter_name = 'has_voted'

    def lookups(self, request, model_admin):
        return (
            ('true', ('Sí')),
            ('false', ('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(voter_id__in=Vote.objects.filter(voting_id=models.OuterRef('voting_id')).values('voter_id'))
        elif self.value() == 'false':
            return queryset.exclude(voter_id__in=Vote.objects.filter(voting_id=models.OuterRef('voting_id')).values('voter_id'))
        return queryset


class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id', 'creation_date', 'additional_info', 'get_status', 'get_total_voters', 'has_voted')
    search_fields = ('voter_id', )
    list_filter = ('voting_id', 'creation_date', StatusFilter, HasVotedFilter)

    def get_status(self, obj):
        return obj.get_status()

    get_status.admin_order_field = 'creation_date'

    def get_total_voters(self, obj):
        return obj.get_total_voters()

    get_total_voters.admin_order_field = 'creation_date'

    def has_voted(self, obj):
        return obj.has_voted()

    has_voted.boolean = True

admin.site.register(Census, CensusAdmin)
