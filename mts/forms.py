from django import forms


class TarifsFilterForm(forms.Form):
    min_price = forms.IntegerField(label="от", required=False)
    max_price = forms.IntegerField(label="до", required=False)
    ordering = forms.ChoiceField(
        label="сортировка",
        required=False,
        choices=[
            ["title", "по алфавиту"],
            ["price", "цена по возрастанию"],
            ["-price", "цена по убыванию"],
        ],
    )
