from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, UserRating, ForumPost, ForumReply

# Registration form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'Email address'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'

# Login form, extends AuthenticationForm with custom styles
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Username or email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Password'
        })

# Rating form
class RatingForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1, max_value=5,
        widget=forms.HiddenInput() # Hidden input, value set by JS star widget
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 3,
            'placeholder': 'Share your thoughts (optional)'
        })
    )

    class Meta:
        model = UserRating
        fields = ('rating', 'comment')

# Forum post form
class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ('title', 'content')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Share your dining experience...'}),
        }

# Forum reply form
class ForumReplyForm(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write a reply...'}),
        }

# Profile edit form, allows updating name, email and avatar
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
