from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# this gets passed a UUID not a contact
def validate_is_customer(contact):
    if not contact.is_customer:
        raise ValidationError(
            _("%(contact)s is not a customer"),
            params={"contact": contact},
        )
