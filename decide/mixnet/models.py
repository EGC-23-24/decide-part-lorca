from django.db import models

from .mixcrypt import MixCrypt

from base import mods
from base.models import Auth, Key
from base.serializers import AuthSerializer
from django.conf import settings

# number of bits for the key, all auths should use the same number of bits
B = settings.KEYBITS


class Mixnet(models.Model):
    """
    Django Model representing a Mixnet entity in the context of electronic voting.

    Attributes:
        voting_id (PositiveIntegerField): Identifier for the voting instance.
        auth_position (PositiveIntegerField): Position of the authorization in the mixnet.
        auths (ManyToManyField): Relation to multiple Auth instances.
        key (ForeignKey): Foreign key to a Key instance, nullable.
        pubkey (ForeignKey): Foreign key to a Key instance for public key, nullable.
    """
    
    voting_id = models.PositiveIntegerField()
    auth_position = models.PositiveIntegerField(default=0)
    auths = models.ManyToManyField(Auth, related_name="mixnets")
    key = models.ForeignKey(Key, blank=True, null=True,
                            related_name="mixnets",
                            on_delete=models.SET_NULL)
    pubkey = models.ForeignKey(Key, blank=True, null=True,
                               related_name="mixnets_pub",
                               on_delete=models.SET_NULL)
    
    def __str__(self):
        """
        Returns a string representation of the Mixnet instance.

        :return: A formatted string representing the Mixnet instance.
        :rtype: str
        """
        
        auths = ", ".join(a.name for a in self.auths.all())
        return "Voting: {}, Auths: {}\nPubKey: {}".format(self.voting_id,
                                                          auths, self.pubkey)

    def shuffle(self, msgs, pk):
        """
        Shuffles the provided messages using the mixnet's cryptographic settings.

        :param msgs: The messages to shuffle.
        :type msgs: list
        :param pk: Public key used in the shuffling process.
        :type pk: Key
        :return: Shuffled messages.
        :rtype: list
        """
        
        crypt = MixCrypt(bits=B)
        k = crypt.setk(self.key.p, self.key.g, self.key.y, self.key.x)

        return crypt.shuffle(msgs, pk)

    def decrypt(self, msgs, pk, last=False):
        """
        Decrypts the provided messages using the mixnet's cryptographic settings.

        :param msgs: The messages to decrypt.
        :type msgs: list
        :param pk: Public key used in the decryption process.
        :type pk: Key
        :param last: Indicates if this is the last decryption step.
        :type last: bool
        :return: Decrypted messages.
        :rtype: list
        """
        
        crypt = MixCrypt(bits=B)
        k = crypt.setk(self.key.p, self.key.g, self.key.y, self.key.x)
        return crypt.shuffle_decrypt(msgs, last)
    
    def gen_key(self, p=0, g=0):
        """
        Generates a cryptographic key for the mixnet.

        :param p: Prime number, part of the cryptographic key.
        :type p: int, optional
        :param g: Generator number, part of the cryptographic key.
        :type g: int, optional
        """
        
        crypt = MixCrypt(bits=B)
        if self.key:
            k = crypt.setk(self.key.p, self.key.g, self.key.y, self.key.x)
        elif (not g or not p):
            k = crypt.genk()
            key = Key(p=int(k.p), g=int(k.g), y=int(k.y), x=int(k.x))
            key.save()

            self.key = key
            self.save()
        else:
            k = crypt.getk(p, g)
            key = Key(p=int(k.p), g=int(k.g), y=int(k.y), x=int(k.x))
            key.save()

            self.key = key
            self.save()

    def chain_call(self, path, data):
        """
        Makes a chained API call to the next authorization in the mixnet.

        :param path: The API path for the call.
        :type path: str
        :param data: Data to be sent in the API call.
        :type data: dict
        :return: The response from the API call or None.
        :rtype: Response or None
        """
        
        next_auths=self.next_auths()

        data.update({
            "auths": AuthSerializer(next_auths, many=True).data,
            "voting": self.voting_id,
            "position": self.auth_position + 1,
        })

        if next_auths:
            auth = next_auths.first().url
            r = mods.post('mixnet', entry_point=path,
                           baseurl=auth, json=data)
            return r

        return None

    def next_auths(self):
        """
        Retrieves the next set of authorizations in the mixnet.

        :return: The next set of Auth instances.
        :rtype: QuerySet
        """
        next_auths = self.auths.filter(me=False)

        if self.auths.count() == next_auths.count():
            next_auths = next_auths[1:]

        return next_auths
