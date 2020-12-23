from django.db import models

class Plan(models.Model):
    """
    Stores the plan details
    """
    name = models.CharField(max_length=127, primary_key=True)
    duration = models.PositiveIntegerField(default=30)
    price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    long_name = models.CharField(max_length=127)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.long_name}'