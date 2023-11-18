from django.db import models
from django.utils import timezone

class Census(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()
    creation_date = models.DateTimeField(default=timezone.now)
    additional_info = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('voting_id', 'voter_id'),)

    def get_status(self):
        return 'Desactivado' if (timezone.now() - self.creation_date).days >= 7 else 'Activo'

    def get_total_voters(self):
        return Census.objects.filter(voting_id=self.voting_id).count()
