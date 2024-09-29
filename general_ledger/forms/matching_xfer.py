from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class TransferForm(forms.Form):

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop("instance")
        prefix = kwargs.pop("prefix")
        active_book_id = kwargs.pop("active_book_id")
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = f"{instance.id}-exampleForm"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "submit_survey"

        self.helper.add_input(Submit("submit", "Submit"))

    like_website = forms.TypedChoiceField(
        label="Do you like this website?",
        choices=((1, "Yes"), (0, "No")),
        coerce=lambda x: bool(int(x)),
        widget=forms.RadioSelect,
        initial="1",
        required=True,
    )
    favorite_number = forms.IntegerField(
        label="Favorite number",
        required=False,
    )

    notes = forms.CharField(
        label="Additional notes or feedback",
        required=False,
    )
