from django import forms

class ProblemForm(forms.Form):
    Title = forms.CharField(label="Title", required=True,max_length=50,)
    Text = forms.CharField(label="Text", required=True, max_length=300, widget=forms.Textarea)
    Image = forms.ImageField(required=False)