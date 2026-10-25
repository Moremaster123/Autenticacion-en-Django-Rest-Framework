from django.db import models


class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = 'addresses'

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"
