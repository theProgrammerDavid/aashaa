from django import forms
from django.contrib.auth.models import User
from .models import Kid, LostKid, VerifyRequest


class VerifyForm(forms.ModelForm):
    class Meta:
        model = VerifyRequest
        fields = ('photo', 'location')

    def __init__(self, *args, **kwargs):
        super(VerifyForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class LostKidRegistrationForm(forms.ModelForm):
    class Meta:
        model = LostKid
        fields = ('name', 'photo', 'date', 'state', 'description', 'email', 'phone_number')
        widgets = {
            'date': forms.DateInput(attrs={'class': 'datepicker'}),
        }

    def __init__(self, *args, **kwargs):
        super(LostKidRegistrationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}), )
    password2 = forms.CharField(label='Repeat Password',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(label='Phone Number')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class KidRegistrationForm(forms.ModelForm):
    class Meta:
        model = Kid
        fields = ('name', 'photo_id', 'state', 'description')

    def __init__(self, *args, **kwargs):
        super(KidRegistrationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
