from django import forms

from .models.pages import Page


class PageForm(forms.ModelForm):

    # Customised ddl inferring additional context via text-indentation
    parent = forms.ChoiceField(
        choices=Page.list(),
        required=False,
        label="Path",
        help_text=Page._meta.get_field("parent").help_text,
    )

    class Meta:
        model = Page
        fields = ["title", "parent", "slug", "priority", "states", "groups"]

    def clean(self):
        """
        Django needs a little help to turn the custom `parent` field back into a model.
        """
        cleaned_data = super().clean()
        parent_id = cleaned_data["parent"]
        cleaned_data["parent"] = (
            Page.objects.get(pk=int(parent_id)) if parent_id else None
        )
        return cleaned_data
