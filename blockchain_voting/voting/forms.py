from django import forms

class VoteForm(forms.Form):
    candidate_id = forms.IntegerField()
