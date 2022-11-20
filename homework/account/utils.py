import hashlib
import random
import string
from datetime import datetime, timedelta
from oauth2_provider.models import Application, AccessToken, RefreshToken
from django.conf import settings

from account.models import Member


def generate_token(string_0, string_1):
    salt = random_salt_generator(4)
    token = f'{string_0}.{string_1}.{salt}'
    return hashlib.md5(token.encode('utf-8')).hexdigest()


def random_salt_generator(length):
    seq = string.ascii_lowercase + string.digits
    return ''.join(random.choices(seq, k=length))


def _fake_grant_token(user):
    """
    grant new tokens. We name this is 'fake' because we don't do this via oauth2_provider api.
    """
    application = Application.objects.get(name='homework')
    expires = datetime.now() + timedelta(days=365)
    access_token = AccessToken.objects.create(
        user=user,
        application=application,
        expires=expires,
        token=generate_token(user.username, user.date_joined.strftime('%Y-%m-%dT%H:%M:%S'))
    )
    refresh_token = RefreshToken.objects.create(
        access_token=access_token,
        user=user,
        application=application,
        token=generate_token(user.username, user.date_joined.strftime('%Y-%m-%dT%H:%M:%S'))
    )
    member = Member.objects.filter(id=user.id).first()
    return {
        'member_id': member.id,
        'member_name': member.name,
        'token_type': 'Bearer',
        'access_token': access_token.token,
        'refresh_token': refresh_token.token,
        'expires': 60*60*24*365,
        'expires_at': expires,
    }
