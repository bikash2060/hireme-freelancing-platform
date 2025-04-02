from django.db import models
from django.utils.translation import gettext_lazy as _

class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "skill"


