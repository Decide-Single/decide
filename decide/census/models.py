from django.db import models

class Census(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True, null=True)
    locality = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = (('voting_id', 'voter_id'),)
