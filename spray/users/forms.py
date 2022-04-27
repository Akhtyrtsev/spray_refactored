from django import forms

from spray.users.models import User, Client, Valet


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


class ValetModelForm(forms.ModelForm):
    class Meta:
        model = Valet
        fields = '__all__'

    def save(self, commit=True):
        data = super().save(commit=False)
        data.set_password(data.password)
        if commit:
            data.save()
        return data

