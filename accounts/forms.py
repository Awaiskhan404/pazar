from django import forms
from django.contrib.auth .forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, ShopOwner, Consumer, Profile, Post, PostComment
from pazar.models import Category

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email',)
        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email',)

class ShopOwnerSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name','email','password1','password2')

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            match = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_shop_owner = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.save()
        shop_owner = ShopOwner.objects.create(user=user)
        shop_owner.save()
        return user

class UserSignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    interests = forms.ModelMultipleChoiceField(queryset=Category.objects.all(),widget=forms.CheckboxSelectMultiple,required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'first_name', 'last_name','email','password1','password2', 'interests')

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            match = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_user = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.save()
        consumer = Consumer.objects.create(user=user)
        consumer.interests.add(*self.cleaned_data.get('interests'))
        consumer.save()
        return user

class UserInterestsForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = ('interests',)
        widgets = {'interests': forms.CheckboxSelectMultiple}

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='E-mail or Username')

class DateInput(forms.DateInput):
    input_type = 'date'

class ConsumerInterestsForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = ('interests', )
        widgets = {
            'interests': forms.CheckboxSelectMultiple
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
        ]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'age','birthday','gender','bio','description','address','phone_no', 'whatsapp', 'website','facebook','instagram',
            'twitter','github','linkedin','youtube','pinterest','pic',
        ]
        widgets = {
            'birthday': DateInput(),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['pic', 'msg', 'tags']
        widgets = {
            'pic' : forms.FileInput(attrs={'class':'form-control'}),
            'msg' : forms.TextInput(attrs={'class':'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['tags'].widget.attrs['data-role'] = 'tagsinput'
        self.fields['pic'].label = "Post Thumbnail"
        self.fields['msg'].label = "Caption"
        self.fields['msg'].widget.attrs['placeholder'] = "Write Caption..."

class CommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ('msg',)
        widgets = {
            'msg' : forms.TextInput(attrs={'class':'form-control', 'placeholder':'Write your comment...'})
        }

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['msg'].label = ""