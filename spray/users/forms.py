from django import forms

from spray.users.models import User, Valet, Client


class UserModelForm(forms.ModelForm):

    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        data = super().save(commit=False)
        data.set_password(data.password)
        if commit:
            data.save()
        return data


class ClientModelForm(UserModelForm):

    class Meta:
        model = Client
        fields = '__all__'


class ValetModelForm(UserModelForm):
    class Meta:
        model = Valet
        fields = '__all__'


class ResetPasswordForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don`t match!')
        return cd['password2']