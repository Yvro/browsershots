from shotserver04.xmlrpc import register
from shotserver04.common import ErrorMessage, get_or_error
from shotserver04.nonces import crypto
from shotserver04.nonces.models import Nonce
from shotserver04.factories.models import Factory
from datetime import datetime, timedelta


@register(str, str)
def challenge(request, factory_name):
    """
    Generate a nonce for authentication.

    Arguments
    ~~~~~~~~~
    * factory_name string (lowercase, normally from hostname)

    Return value
    ~~~~~~~~~~~~
    * challenge string (algorithm$salt$nonce)

    The return value is a string that contains the password encryption
    algorithm (sha1 or md5), the salt, and the nonce, separated by '$'
    signs, for example::

        sha1$0c0ac$eb403b48ec9bf887ba645408acad17a5

    See nonces.verify for how to encrypt your password with the nonce.
    """
    factory = get_or_error(Factory, name=factory_name)
    hashkey = crypto.random_md5()
    ip = request.META['REMOTE_ADDR']
    Nonce.objects.create(factory=factory, hashkey=hashkey, ip=ip)
    password = factory.admin.password
    if password.count('$'):
        algo, salt, encrypted = password.split('$')
    else:
        algo, salt, encrypted = 'md5', '', password
    return '$'.join((algo, salt, hashkey))


@register(str, str, str)
def verify(request, factory_name, encrypted_password):
    """
    Test authentication with an encrypted password.

    Arguments
    ~~~~~~~~~
    * factory_name string (lowercase, normally from hostname)
    * encrypted_password string (lowercase hexadecimal, length 32)

    Return value
    ~~~~~~~~~~~~
    * status string ('OK' or short error message)

    Password encryption
    ~~~~~~~~~~~~~~~~~~~
    To encrypt the password, you must first generate a nonce and get
    the encryption algorithm and salt (see nonces.challenge). Then you
    can compute the encrypted password like this::

        encrypted_password = md5(sha1(salt + password) + nonce)

    If requested by the challenge, you must use md5 rather than sha1
    for the inner hash. The result of each hash function call must be
    formatted as lowercase hexadecimal. The calls to nonces.challenge
    and nonces.verify must be made from the same IP address.
    """
    # Shortcut for use with other XML-RPC methods
    if isinstance(factory_name, Factory):
        factory = factory_name
    else:
        factory = get_or_error(Factory, name=factory_name)
    ip = request.META['REMOTE_ADDR']
    # Get password hash from database
    password = factory.admin.password
    if password.count('$'):
        algo, salt, hashed = password.split('$')
    else:
        algo, salt, hashed = 'md5', '', password
    # Get matching nonces
    nonces = Nonce.objects.filter(factory=factory, ip=ip).extra(
        where=["MD5(%s || hashkey) = %s"],
        params=[hashed, encrypted_password])
    if len(nonces) == 0:
        raise ErrorMessage('Password mismatch.')
    if len(nonces) > 1:
        raise ErrorMessage('Hash collision.')
    # Check nonce freshness
    nonce = nonces[0]
    if datetime.now() - nonce.created > timedelta(0, 600, 0):
        nonce.delete()
        raise ErrorMessage('Nonce expired.')
    # Success!
    nonce.delete()
    return 'OK'
