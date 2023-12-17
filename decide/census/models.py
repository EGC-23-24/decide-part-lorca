from django.db import models
from django.core.exceptions import ValidationError
from voting.models import Voting
from django.contrib.auth.models import User

class Census(models.Model):
    voting_id = models.IntegerField()
    voter_id = models.IntegerField()

    def clean(self):
        # Comprueba si el Voting y el User existen
        if not Voting.objects.filter(id=self.voting_id).exists():
            raise ValidationError({'voting_id': 'Voting with this ID does not exist.'})

        if not User.objects.filter(id=self.voter_id).exists():
            raise ValidationError({'voter_id': 'User with this ID does not exist.'})

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

