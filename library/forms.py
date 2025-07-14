from django import forms
from .models import Ebook

class EbookUploadForm(forms.ModelForm):
    class Meta:
        model = Ebook
        fields = ['title', 'author', 'description', 'price', 'cover', 'file']  # adjust to your model
