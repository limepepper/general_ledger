from django.db import models


class ExchangeRate(models.Model):
    """
    Exchange rate model
    """

    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return f"{self.base_currency} to {self.target_currency} rate: {self.rate}"

    # def clean(self):
    #     if self.base_currency == self.target_currency:
    #         raise ValidationError("Base and target currency must be different")
    #
    # def save(self, *args, **kwargs):
    #     self.rate = Decimal(self.rate).quantize(Decimal("0.0000000001"), rounding=ROUND_HALF_UP)
    #     super().save(*args, **kwargs)
