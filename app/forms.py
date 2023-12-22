from django import forms
from .models import CustomUser, Content, Comment


class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'description', 'file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['file'].widget.attrs['class'] = 'form-control-file'


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class ProfileEditForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ['name', 'username', 'avatar', 'email', 'bio', 'password']
