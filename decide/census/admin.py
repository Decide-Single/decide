from django.contrib import admin
from .models import Census

class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id', 'sex', 'locality', 'vote_date', 'has_voted', 'vote_result', 'vote_method')
    list_filter = ('voting_id', 'sex', 'locality', 'vote_date', 'has_voted', 'vote_result', 'vote_method') 
    search_fields = ('voter_id', 'locality') 

admin.site.register(Census, CensusAdmin)
