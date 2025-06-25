from django import forms
from django.contrib.auth.models import User

# Form to handle sharing a document with multiple users
class ShareDocumentForm(forms.Form):
    # Field to select multiple users to share the document with
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # Default empty queryset, will be updated dynamically in the view
        widget=forms.CheckboxSelectMultiple,  # Displays the options as checkboxes for easy multi-selection
        required=False,  # Sharing is optional; no users need to be selected
        label='Select Users to Share With'  # Label displayed for the field in the form
    )
