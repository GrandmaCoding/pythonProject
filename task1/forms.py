from django import forms


class InputForm(forms.Form):
    enter_data = forms.CharField(max_length=200, help_text='Enter text here')
