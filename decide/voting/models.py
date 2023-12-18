import binascii
from django.db import models
from django.db.models import JSONField

from base import mods
from base.models import Auth, Key
import json


class Question(models.Model):
    """
    Represents a question in a voting system.

    Attributes:
        desc (TextField): The description of the question.
        TYPES (list): The list of possible types for a question.
        type (CharField): The type of the question, chosen from TYPES.
    """

    desc = models.TextField()
    TYPES = [
        ('C', 'Classic question'),
        ('Y', 'Yes/No question'),
        ('M', 'Multiple choice question'),
        ('T', 'Text question'),
        ('R', 'Ranked question'),
    ]
    type = models.CharField(max_length=1, choices=TYPES, default='C')

    def save(self, *args, **kwargs):
        """
        Saves a Question instance and automatically creates Yes/No options if it's a Yes/No question.

        :param args: Variable length argument list.
        :param kwargs: Keyword arguments.
        """

        super().save(*args, **kwargs)
        if self.type == 'Y':
            # Create Yes/No options when a Yes/No question is saved
            QuestionOptionYesNo.objects.get_or_create(
                question=self, option='Si', number=1)
            QuestionOptionYesNo.objects.get_or_create(
                question=self, option='No', number=2)

    def __str__(self):
        """
        Returns a string representation of the Question instance.

        :return: The description of the question.
        :rtype: str
        """

        return self.desc


class QuestionOption(models.Model):
    """
    Represents an option for a question in a voting system.

    Attributes:
        question (ForeignKey): The question to which this option belongs.
        number (PositiveIntegerField): The number of the option.
        option (TextField): The text of the option.
    """

    question = models.ForeignKey(
        Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self):
        """
        Saves a QuestionOption instance with automatic numbering for Classic and Multiple choice questions.

        :return: None
        """

        if not self.number:
            self.number = self.question.options.count() + 2
        if self.question.type in ['C', 'M']:
            return super().save()

    def __str__(self):
        """
        Returns a string representation of the QuestionOption instance.

        :return: The option text and number or a restriction message.
        :rtype: str
        """

        if self.question.type in ['C', 'M']:
            return '{} ({})'.format(self.option, self.number)
        else:
            return 'You cannot create an option for a non-Classic or multiple choice question'


class QuestionOptionRanked(models.Model):
    """
    Represents a ranked option for a question in a voting system.

    Attributes:
        question (ForeignKey): The question to which this ranked option belongs.
        number (PositiveIntegerField): The number of the ranked option.
        option (TextField): The text of the ranked option.
        preference (PositiveIntegerField): The preference number for the option.
    """

    question = models.ForeignKey(
        Question, related_name='ranked_options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()
    preference = models.PositiveIntegerField(blank=True, null=True)

    def save(self):
        """
        Saves a QuestionOptionRanked instance with automatic numbering for Ranked questions.

        :return: None
        """

        if not self.number:
            self.number = self.question.ranked_options.count() + 1
        if self.question.type == 'R':
            return super().save()

    def __str__(self):
        """
        Returns a string representation of the QuestionOptionRanked instance.

        :return: The ranked option text and number or a restriction message.
        :rtype: str
        """

        if self.question.type == 'R':
            return '{} ({})'.format(self.option, self.number)
        else:
            return 'You cannot create a ranked option for a non-ranked question'


class QuestionOptionYesNo(models.Model):
    """
    Represents a Yes/No option for a question in a voting system.

    Attributes:
        question (ForeignKey): The question to which this Yes/No option belongs.
        number (PositiveIntegerField): The number of the Yes/No option.
        option (TextField): The text of the Yes/No option.
    """

    question = models.ForeignKey(
        Question, related_name='yesno_options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self, *args, **kwargs):
        """
        Saves a QuestionOptionYesNo instance with automatic numbering for Yes/No questions.

        :param args: Variable length argument list.
        :param kwargs: Keyword arguments.
        :return: None
        """

        if not self.number:
            self.number = self.question.options.count() + 2
        if self.question.type == 'Y':
            return super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the QuestionOptionYesNo instance.

        :return: The Yes/No option text and number or a restriction message.
        :rtype: str
        """

        if self.question.type == 'Y':
            return '{} - {} ({}) '.format(self.question,
                                          self.option, self.number)
        else:
            return 'You cannot create a Yes/No option for a non-Yes/No question'


class Voting(models.Model):
    """
    Represents a voting in the system.

    Attributes:
        name (CharField): The name of the voting.
        desc (TextField): The description of the voting.
        question (ForeignKey): The question related to this voting.
        created_at (DateTimeField): The timestamp when the voting was created.
        start_date (DateTimeField): The start date and time of the voting.
        end_date (DateTimeField): The end date and time of the voting.
        future_stop (DateTimeField): The future stop date and time of the voting.
        pub_key (OneToOneField): The public key associated with the voting.
        auths (ManyToManyField): The authorizations related to this voting.
        tally (JSONField): The tally of votes.
        postproc (JSONField): The post-processing data of the voting.
    """

    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ForeignKey(
        Question, related_name='voting', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    future_stop = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(
        Key,
        related_name='voting',
        blank=True,
        null=True,
        on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

    def create_pubkey(self):
        """
        Creates a public key for the voting if it doesn't already have one and if it has authorizations.
        """
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {"voting": self.id, "auths": [
            {"name": a.name, "url": a.url} for a in self.auths.all()], }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        """
        Retrieves votes for the voting.

        :param token: Authorization token for retrieving votes.
        :type token: str
        :return: A list of formatted votes.
        :rtype: list
        """

        # gettings votes from store
        votes = mods.get(
            'store',
            params={
                'voting_id': self.id},
            HTTP_AUTHORIZATION='Token ' +
            token)
        # anon votes
        votes_format = []
        vote_list = []
        for vote in votes:
            for info in vote:
                if info == 'a':
                    votes_format.append(vote[info])
                if info == 'b':
                    votes_format.append(vote[info])
            vote_list.append(votes_format)
            votes_format = []
        return vote_list

    def tally_votes(self, token=''):
        """
        Tally votes for the voting.

        :param token: Authorization token for tallying votes.
        :type token: str
        """

        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        decrypt_aes_url = "/decrypt_aes/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = {"msgs": votes}
        response = mods.post(
            'mixnet',
            entry_point=shuffle_url,
            baseurl=auth.url,
            json=data,
            response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post(
            'mixnet',
            entry_point=decrypt_url,
            baseurl=auth.url,
            json=data,
            response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        def decimal_to_ascii(decimal_string):
            """
            Converts a decimal string to its ASCII character representation.

            This function takes a string of decimal numbers and converts each group of three digits to the corresponding ASCII character. It pads the string with zeros at the beginning if the length of the string is not a multiple of three.

            :param decimal_string: The decimal string to be converted.
            :type decimal_string: str
            :return: The ASCII character string or an error message if the input is not a valid decimal string.
            :rtype: str

            :raises ValueError: If the input contains characters that are not part of a valid decimal string.
            """

            decimal_string = str(decimal_string).replace(
                '[', '').replace(']', '')
            try:
                # Convert the decimal string to a list of ASCII characters with
                # length 4
                while len(decimal_string) % 3 != 0:
                    decimal_string = '0' + decimal_string
                ascii_string = ''
                for i in range(0, len(decimal_string), 3):
                    ascii_char = decimal_string[i:i + 3]
                    ascii_string += chr(int(ascii_char))
                return ascii_string
            except ValueError:
                # Handle the case where the input is not a valid decimal string
                return "Invalid decimal string"

        if self.question.type == 'R':
            data = {"msgs": response.json()}
            for key, values in data.items():
                data[key] = [decimal_to_ascii(value) for value in values]
            self.tally = data
            self.save()
        elif self.question.type == 'T':
            data = {"msgs": response.json()}
            for key, values in data.items():
                data[key] = [decimal_to_ascii(v) for v in values]
            self.tally = data
            self.save()
        else:
            self.tally = response.json()
            self.save()
        self.do_postproc()

    def do_postproc(self):
        """
        Performs post-processing on the tallied votes.
        """

        tally = self.tally
        options = self.question.options.all()

        opts = []
        for opt in options:
            if isinstance(tally, list):
                votes = tally.count(opt.number)
            else:
                votes = 0
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'votes': votes
            })

        # postproc for ranked questions
        if self.question.type == 'R':
            ranked_options = self.question.ranked_options.all()
            vote_counts = {opt.number: 0 for opt in ranked_options}
            for msg, votes_weights in tally.items():
                for vote_weight in votes_weights:
                    list_preferences = vote_weight.split('-')
                    for i, vote_weight in enumerate(list_preferences):
                        vote_counts[i + 1] += len(list_preferences) - \
                            int(vote_weight) + 1

            opts = []
            for opt in ranked_options:
                votes = len(tally['msgs'])
                votes_weights = vote_counts[opt.number]
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes,
                    'votes_wights': votes_weights

                })
            data = {'type': 'WEIGHT', 'options': opts}
        # yes/no postproc
        elif self.question.type == 'Y':
            yesno_options = self.question.yesno_options.all()
            for opt in yesno_options:
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                else:
                    votes = 0
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes
                })
            data = {'type': 'IDENTITY', 'options': opts}

        # postproc for text questions
        elif self.question.type == 'T':
            text_votes = []
            for msg, votes in tally.items():
                for vote in votes:
                    text_votes.append({'vote': vote})

            data = {'type': 'TEXT', 'text_votes': text_votes}
        else:
            data = {'type': 'IDENTITY', 'options': opts}

        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        """
        Returns a string representation of the Voting instance.

        :return: The name of the voting.
        :rtype: str
        """
        return self.name
