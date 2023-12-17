from django.db import models
from base.models import BigBigField


class Vote(models.Model):
    """
    A model representing a vote in a voting system.

    Attributes:
        voting_id (PositiveIntegerField): The ID of the voting session this vote is associated with.
        voter_id (PositiveIntegerField): The ID of the voter who cast this vote.
        a (BigBigField): Encrypted data part A representing the vote.
        b (BigBigField): Encrypted data part B representing the vote.
        voted (DateTimeField): The timestamp of when the vote was cast.
    """
    
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()

    a = BigBigField()
    b = BigBigField()

    voted = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns a string representation of the Vote instance.

        Returns:
            str: A string showing the voting ID and the voter ID.
        """
        
        return '{}: {}'.format(self.voting_id, self.voter_id)
