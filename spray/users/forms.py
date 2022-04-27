from django import forms

from spray.users.models import User, Client


class UserModelForm(forms.ModelForm):

    class Meta:
        model = User
        fields = '__all__'


class ClientModelForm(forms.ModelForm):

    class Meta:
        model = Client
        fields = '__all__'

    def save(self, commit=True):
        data = super().save(commit=False)
        data.set_password(data.password)
        if commit:
            data.save()
        return data


