from django.contrib import admin
from .models import Census

class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id', 'sex', 'locality')
    list_filter = ('voting_id', 'sex', 'locality')
    search_fields = ('voter_id', 'locality')

admin.site.register(Census, CensusAdmin)
