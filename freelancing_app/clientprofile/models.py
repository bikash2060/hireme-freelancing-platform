from django.db import models
from accounts.models import User

class Client(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='client_profile'
    )

    def __str__(self):
        return f"Client: {self.user.username}"

    class Meta:
        db_table = "client"
