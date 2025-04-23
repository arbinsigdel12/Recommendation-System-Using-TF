from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new users
            self.is_admin = self.is_staff
        super().save(*args, **kwargs)

class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('view', 'Viewed'),
        ('cart', 'Added to Cart'),
        ('buy', 'Purchased'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-timestamp']