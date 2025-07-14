from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Ebook(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField()
    cover = models.ImageField(upload_to='covers/')
    file = models.FileField(upload_to='ebooks/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)
    genre = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # ✅ Add this

    def __str__(self):
        return self.title




class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ebook = models.ForeignKey(Ebook, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    verified = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.ebook} - {self.verified}"
    

User.add_to_class('paid_ebooks', models.ManyToManyField(Ebook, blank=True, related_name='paid_users'))


class Download(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ebook = models.ForeignKey(Ebook, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
