from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from six import text_type
from .models import CustomUser, Profile

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, customuser, timestamp):
        return (
            six.text_type(customuser.pk) + six.text_type(timestamp) +
            six.text_type(CustomUser.signup_confirmation)
        )

account_activation_token = AccountActivationTokenGenerator()