from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class MinimumLengthAndNumberValidator:
    """
    Validate that the password:
    - Contains at least 8 characters
    - Contains at least one number
    """
    
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("This password must contain at least %(min_length)d characters."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )
        
        if not re.search(r'\d', password):
            raise ValidationError(
                _("This password must contain at least one number."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(min_length)d characters and at least one number."
            % {'min_length': self.min_length}
        )