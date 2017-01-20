from django import forms
from grumblr.models import *

class RegistrationForm(forms.Form):
    user_name = forms.CharField(max_length=20, label="User Name")
    email = forms.EmailField(max_length = 50, label="Email Address", widget=forms.EmailInput())
    first_name = forms.CharField(max_length = 20, label="First Name")
    last_name = forms.CharField(max_length = 20, label="Last Name")
    password = forms.CharField(max_length=200,
                               label='Password',
                               widget=forms.PasswordInput())
    confirm_pass = forms.CharField(max_length = 200,
                                label='Confirm password',
                                widget = forms.PasswordInput())
    age = forms.IntegerField(min_value=0, max_value=200, label='Age',required = False)
    bio = forms.CharField(max_length=420, label='About me',required = False)

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_pass = cleaned_data.get('confirm_pass')
        if password and confirm_pass and password != confirm_pass:
            raise forms.ValidationError("Passwords did not match.")
        return cleaned_data

    def clean_username(self):
        user_name = self.cleaned_data.get('user_name')
        if Users.objects.filter(user_name=user_name):
            return forms.ValidationError("User name already taken.")

        return user_name

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Users
        exclude = ('username','password', 'email', 'following', 'confirm', )
        widgets = {
            'bio': forms.Textarea(attrs={'cols': 20, 'rows': 10}),
            'selfi': forms.FileInput(),
        }
        fields = ('first_name', 'last_name', 'age', 'bio', 'selfi')

# <input type="text" class="form-control" name="firstName" value={{field}}>

class PasswordEditForm(forms.Form):
    old = forms.CharField(max_length=200,
                               label='Old Password',
                               widget=forms.PasswordInput())
    password = forms.CharField(max_length=200,
                               label='Password',
                               widget=forms.PasswordInput())
    confirm_pass = forms.CharField(max_length=200,
                                   label='Confirm password',
                                   widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(PasswordEditForm, self).clean()
        password = cleaned_data.get('password')
        confirm_pass = cleaned_data.get('confirm_pass')
        if password and confirm_pass and password != confirm_pass:
            raise forms.ValidationError("Passwords did not match!")
        return cleaned_data

class StatusModelForm(forms.ModelForm):
    class Meta:
        model = Status
        exclude=('user_name', 'last_name', 'first_name','created_date')
        widgets = {
            'text' : forms.Textarea(attrs={'cols': 20, 'rows': 10})
        }
        fields = ('text', )


class PasswordEditForm_forget(forms.Form):

    password = forms.CharField(max_length=200,
                               label='Password',
                               widget=forms.PasswordInput())
    confirm_pass = forms.CharField(max_length=200,
                                   label='Confirm password',
                                   widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super(PasswordEditForm_forget, self).clean()
        password = cleaned_data.get('password')
        confirm_pass = cleaned_data.get('confirm_pass')
        if password and confirm_pass and password != confirm_pass:
            raise forms.ValidationError("Passwords did not match!")
        return cleaned_data

class AddCommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        exclude=("created_date", "owner", "status", )
        widgets = {
            "text" :  forms.TextInput
        }
        fields = ("text", )

    def clean(self):
        cleaned_data = super(AddCommentForm, self).clean()
        return cleaned_data