from django.db import models
from django.core.exceptions import ValidationError
from voting.models import Voting
from django.contrib.auth.models import User

class Census(models.Model):
    """
    Model representing a voting census, associating voters with votings.

    Attributes:
        voting_id (models.IntegerField): The ID of the voting to which the voter belongs.
        voter_id (models.IntegerField): The ID of the user who is voting.

    Methods:
        clean: Validates that both the Voting and User instances exist.
        save: Saves the instance after validation.
    """
    
    voting_id = models.IntegerField()
    voter_id = models.IntegerField()

    def clean(self):
        """
        Validates that the referenced Voting and User objects exist.

        Raises a ValidationError if either the voting or the user do not exist.

        :raises ValidationError: If the referenced voting or user do not exist.
        """
        
        # Comprueba si el Voting y el User existen
        if not Voting.objects.filter(id=self.voting_id).exists():
            raise ValidationError({'voting_id': 'Voting with this ID does not exist.'})

        if not User.objects.filter(id=self.voter_id).exists():
            raise ValidationError({'voter_id': 'User with this ID does not exist.'})

    def save(self, *args, **kwargs):
        """
        Saves the Census object after validation.

        First calls clean to validate the data, then calls the save method of the superclass.

        :param args: Variable arguments.
        :param kwargs: Variable keyword arguments.
        :return: The result of the save method from the superclass.
        """
        
        self.clean()
        return super().save(*args, **kwargs)

