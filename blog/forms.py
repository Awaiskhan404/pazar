from django import forms
from .models import Blog
from django.forms import ModelForm

class BlogForm(forms.ModelForm):
    
    class Meta:
        model = Blog
        fields = ('title', 'category', 'thumbnail', 'content', 'tags',)
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control', 'placeholder':'Write Blog Title'}),
            'thumbnail':forms.FileInput(attrs={'class':'form-control'}),
            'category':forms.Select(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)
        self.fields['tags'].widget.attrs['data-role'] = 'tagsinput'
    