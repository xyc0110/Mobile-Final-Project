from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # ✅ 加入 image 字段，才能在表单中上传图片
        fields = ('title', 'text', 'image',)
