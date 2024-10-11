from datetime import date


class ValidatableMixin:
    """
    Mixin that sets a validation property
    allow recursive validation
    """

    @property
    def is_valid(self):
        return self.validate()

    def validate(self):
        raise NotImplementedError("validate method must be implemented in subclass")
