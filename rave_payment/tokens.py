from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
import requests
from requests.auth import AuthBase

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.userprofile.email_confirmed)
        )

account_activation_token = AccountActivationTokenGenerator()


class TokenAuth(AuthBase):
    """Implements a custom authentication scheme."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        """Attach an API token to a custom auth header."""
        r.headers['Authorization'] = 'Bearer ' + self.token  # Python 3.6+
        print('Bearer ' + self.token)
        return r