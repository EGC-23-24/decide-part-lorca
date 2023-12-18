'''
>>> B = 256
>>> k1 = MixCrypt(bits=B)
>>> k2 = MixCrypt(k=k1.k, bits=B)
>>> k3 = gen_multiple_key(k1, k2)
>>> N = 4
>>> clears = [random.StrongRandom().randint(1, B) for i in range(N)]
>>> cipher = [k3.encrypt(i) for i in clears]
>>> d = multiple_decrypt_shuffle(cipher, k1, k2)
>>> clears == d
False
>>> sorted(clears) == sorted(d)
True

>>> B = 256
>>> k1 = MixCrypt(bits=B)
>>> k1.setk(167,156,89,130) #doctest: +ELLIPSIS
<Crypto.PublicKey.ElGamal.ElGamalobj object at 0x...>
>>> k2 = MixCrypt(bits=B)
>>> k2.setk(167,156,53,161) #doctest: +ELLIPSIS
<Crypto.PublicKey.ElGamal.ElGamalobj object at 0x...>
>>> k3 = MixCrypt(bits=B)
>>> k3.k = ElGamal.construct((167, 156, 4717))
>>> k3.k.p, k3.k.g, k3.k.y
(167, 156, 4717)
>>> N = 4
>>> clears = [2,3,6,4]
>>> cipher = [(161, 109), (17, 101), (148, 163), (71, 37)]
>>> d = multiple_decrypt_shuffle(cipher, k2, k1)
>>> clears == d
False
>>> sorted(clears) == sorted(d)
True
'''


from pprint import pprint

from Crypto.PublicKey import ElGamal
from Crypto.Random import random
from Crypto import Random
from Crypto.Util.number import GCD
from Crypto.Cipher import AES


def rand(p):
    """
    Generates a random integer k where GCD(k, p-1) == 1.

    :param p: A prime number.
    :type p: int
    :return: A random integer k.
    :rtype: int
    """
    
    while True:
        k = random.StrongRandom().randint(1, int(p) - 1)
        if GCD(k, int(p) - 1) == 1: break
    return k


def gen_multiple_key(*crypts):
    """
    Generates a combined MixCrypt object from multiple MixCrypt objects.

    :param crypts: Variable number of MixCrypt objects.
    :type crypts: tuple
    :return: A new MixCrypt object with combined properties.
    :rtype: MixCrypt
    """
    
    k1 = crypts[0]
    k = MixCrypt(k=k1.k, bits=k1.bits)
    k.k.y = 1
    for kx in crypts:
        k.k.y *= kx.k.y
    k.k.y = k.k.y % k.k.p
    return k


def multiple_decrypt(c, *crypts):
    """
    Sequentially decrypts a cipher using multiple MixCrypt objects.

    :param c: The cipher to decrypt.
    :type c: tuple
    :param crypts: Variable number of MixCrypt objects for decryption.
    :type crypts: tuple
    :return: The decrypted message.
    :rtype: int
    """
    
    a, b = c
    for k in crypts:
        b = k.decrypt((a, b))
    return b


def multiple_decrypt_shuffle(ciphers, *crypts):
    """
    Sequentially decrypts and shuffles a list of ciphers using multiple MixCrypt objects.

    :param ciphers: The list of ciphers to decrypt and shuffle.
    :type ciphers: list
    :param crypts: Variable number of MixCrypt objects for decryption and shuffling.
    :type crypts: tuple
    :return: The list of decrypted and shuffled messages.
    :rtype: list
    """
    
    b = ciphers
    for i, k in enumerate(crypts):
        last = i == len(crypts) - 1
        b = k.shuffle_decrypt(b, last)
    return b

def multiple_decrypt_shuffle2(ciphers, *crypts, pubkey=None):
    """
    Decrypts and shuffles a list of ciphers using multiple MixCrypt objects.

    :param ciphers: The list of ciphers to decrypt and shuffle.
    :type ciphers: list
    :param crypts: Variable number of MixCrypt objects for decryption and shuffling.
    :type crypts: tuple
    :param pubkey: Optional public key used in the shuffling process.
    :type pubkey: tuple, optional
    :return: The list of decrypted and shuffled messages.
    :rtype: list
    """
    
    '''
    >>> B = 256
    >>> k1 = MixCrypt(bits=B)
    >>> k2 = MixCrypt(k=k1.k, bits=B)
    >>> k3 = gen_multiple_key(k1, k2)
    >>> pk = pubkey=(k3.k.p, k3.k.g, k3.k.y)
    >>> N = 8
    >>> clears = [random.StrongRandom().randint(1, B) for i in range(N)]
    >>> cipher = [k3.encrypt(i) for i in clears]
    >>> d = multiple_decrypt_shuffle2(cipher, k1, k2, pubkey=pk)
    >>> clears == d
    False
    >>> sorted(clears) == sorted(d)
    True
    '''

    b = ciphers.copy()

    # shuffle
    for k in crypts:
        b = k.shuffle(b, pubkey)

    # decrypt
    for i, k in enumerate(crypts):
        last = i == len(crypts) - 1
        b = k.multiple_decrypt(b, last=last)
    return b


class MixCrypt:
    """
    A class for cryptographic operations based on the ElGamal encryption scheme.

    :param k: Optional pre-existing key to initialize the MixCrypt.
    :type k: ElGamal key, optional
    :param bits: Bit size for the key generation.
    :type bits: int
    """
    
    def __init__(self, k=None, bits=256):
        self.bits = bits
        if k:
            self.k = self.getk(k.p, k.g)
        else:
            self.k = self.genk()

    def genk(self):
        """
        Generates a new ElGamal key.

        :return: The generated ElGamal key.
        :rtype: ElGamal key
        """
        
        self.k = ElGamal.generate(self.bits, Random.new().read)
        return self.k

    def getk(self, p, g):
        """
        Constructs an ElGamal key from given parameters.

        :param p: Prime number.
        :type p: int
        :param g: Generator number.
        :type g: int
        :return: The constructed ElGamal key.
        :rtype: ElGamal key
        """
        
        x = rand(p)
        y = pow(g, x, p)
        self.k = ElGamal.construct((p, g, y, x))
        return self.k

    def setk(self, p, g, y, x):
        """
        Sets the ElGamal key with specified parameters.

        :param p: Prime number.
        :type p: int
        :param g: Generator number.
        :type g: int
        :param y: Public key component.
        :type y: int
        :param x: Private key component.
        :type x: int
        :return: The set ElGamal key.
        :rtype: ElGamal key
        """
        
        self.k = ElGamal.construct((p, g, y, x))
        return self.k
    
    def encrypt(self, m, k=None):
        """
        Encrypts a message using ElGamal encryption.

        :param m: The message to encrypt.
        :type m: int
        :param k: Optional key to use for encryption. If not provided, use the instance's key.
        :type k: ElGamal key, optional
        :return: The encrypted message.
        :rtype: tuple
        """
        
        r = rand(self.k.p)
        if not k:
            k = self.k
        a, b = k._encrypt(m, r)
        return a, b

    def decrypt(self, c):
        """
        Decrypts an ElGamal encrypted message.

        :param c: The encrypted message tuple.
        :type c: tuple
        :return: The decrypted message.
        :rtype: int
        """
        
        m = self.k._decrypt(c)
        return m
    
    def multiple_decrypt(self, msgs, last=True):
        """
        Decrypts multiple messages, optionally leaving them in tuple form.

        :param msgs: List of encrypted message tuples.
        :type msgs: list
        :param last: If True, return the clear message; if False, return a tuple with the original 'a' value and the decrypted 'b'.
        :type last: bool
        :return: List of decrypted messages or message tuples.
        :rtype: list
        """
        
        msgs2 = []
        for a, b in msgs:
            clear = self.decrypt((a, b))
            if last:
                msg = clear
            else:
                msg = (a, clear)
            msgs2.append(msg)
        return msgs2

    def shuffle_decrypt(self, msgs, last=True):
        """
        Shuffles and decrypts a list of encrypted messages.

        :param msgs: The list of messages to shuffle and decrypt.
        :type msgs: list
        :param last: If True, only the decrypted message is returned; if False, a tuple is returned with the original 'a' value and the decrypted 'b'.
        :type last: bool
        :return: The shuffled and decrypted list of messages.
        :rtype: list
        """
        
        msgs2 = msgs.copy()
        msgs3 = []
        while msgs2:
            n = random.StrongRandom().randint(0, len(msgs2) - 1)
            a, b = msgs2.pop(n)
            clear = self.decrypt((a, b))
            if last:
                msg = clear
            else:
                msg = (a, clear)
            msgs3.append(msg)

        return msgs3
    
    def reencrypt(self, cipher, pubkey=None):
        """
        Re-encrypts an encrypted message, optionally with a new public key.

        :param cipher: The encrypted message to re-encrypt.
        :type cipher: tuple
        :param pubkey: Optional public key for re-encryption. If not provided, the instance's key is used.
        :type pubkey: tuple, optional
        :return: The re-encrypted message.
        :rtype: tuple
        """
        
        '''
        >>> B = 256
        >>> k = MixCrypt(bits=B)
        >>> clears = [random.StrongRandom().randint(1, B) for i in range(5)]
        >>> cipher = [k.encrypt(i) for i in clears]
        >>> cipher2 = [k.reencrypt(i) for i in cipher]
        >>> d = [k.decrypt(i) for i in cipher]
        >>> d2 = [k.decrypt(i) for i in cipher2]
        >>> clears == d == d2
        True
        >>> cipher != cipher2
        True
        '''

        if pubkey:
            p, g, y = pubkey
            k = ElGamal.construct((p, g, y))
        else:
            k = self.k

        a, b = map(int, cipher)
        a1, b1 = map(int, self.encrypt(1, k=k))
        p = int(k.p)

        return ((a * a1) % p, (b * b1) % p)

    def gen_perm(self, l):
        """
        Generates a permutation of indices for a given length.

        :param l: The length of the list to generate a permutation for.
        :type l: int
        :return: A list of permuted indices.
        :rtype: list
        """
        
        x = list(range(l))
        for i in range(l):
            d = random.StrongRandom().randint(0, i)
            if i != d:
                x[i] = x[d]
                x[d] = i
        return x

    def shuffle(self, msgs, pubkey=None):
        """
        Re-encrypts and shuffles a list of messages.

        :param msgs: The list of messages to re-encrypt and shuffle.
        :type msgs: list
        :param pubkey: Optional public key for re-encryption. If not provided, the instance's key is used.
        :type pubkey: tuple, optional
        :return: The shuffled and re-encrypted list of messages.
        :rtype: list
        """

        msgs2 = msgs.copy()
        perm = self.gen_perm(len(msgs))
        for i, p in enumerate(perm):
            m = msgs[p]
            nm = self.reencrypt(m, pubkey)
            msgs2[i] = nm

        return msgs2


if __name__ == "__main__":
    import doctest
    doctest.testmod()
