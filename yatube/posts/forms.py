from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Присваивает атрибуты форме поста."""
    # text = forms.CharField(widget=forms.Textarea(
        # attrs={'name': 'text', 'cols': '40', 'rows': '10'}),
        # label='Текст поста',
        # help_text='Текст поста не должен быть пустым'
    # )

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

    def clean_text(self):
        data = self.cleaned_data['text']
        if data.strip() == '' or data == '':
            raise forms.ValidationError(
                'Пост должен содержать хоть что-то')
        return data


class CommentForm(forms.ModelForm):
    """Создаёт форму по модели поста."""
    # text=forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comment
        fields = ('text',)

    def clean_text(self):
        data = self.cleaned_data['text']
        if data.strip() == '' or data == '':
            raise forms.ValidationError(
                'Комментарий должен содержать хоть что-то')
        return data
