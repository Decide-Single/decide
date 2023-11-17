from django.db import models

class Census(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    VOTE_METHOD_CHOICES = [
        ('IN_PERSON', 'In Person'),
        ('MAIL_IN', 'Mail-In'),
        ('ONLINE', 'Online'),
    ]

    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True, null=True)
    locality = models.CharField(max_length=255, blank=True, null=True)
    vote_date = models.DateField(blank=True, null=True)
    has_voted = models.BooleanField(default=False)
    vote_result = models.CharField(max_length=255, blank=True, null=True)
    vote_method = models.CharField(max_length=10, choices=VOTE_METHOD_CHOICES, blank=True, null=True)
    #test de un cambio para comprobar que va el template

    class Meta:
        unique_together = (('voting_id', 'voter_id'),)
