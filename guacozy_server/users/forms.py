from django.contrib.auth.forms import AuthenticationForm


class CustomAuthenticationForm(AuthenticationForm):
    def clean(self):
        cleaned_data = super().clean()
        self.request.session['username'] = cleaned_data['username']
        self.request.session['password'] = cleaned_data['password']
        return cleaned_data
