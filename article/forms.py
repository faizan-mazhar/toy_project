from django import forms
from article.models import Article


class UpdateArticleForm(forms.ModelForm):
    status = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Article
        fields = ["title", "content", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['readonly'] = True
        self.fields['status'].widget.attrs['required'] = False
        self.fields['status'].disabled = True


class CreateArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ["title", "content"]


class ArticleApprovalForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ["status"]
