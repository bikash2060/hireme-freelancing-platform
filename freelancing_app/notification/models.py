# models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    redirect_url = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'notifications'

    def __str__(self):
        return f"{self.user.username} - {self.message[:50]}"