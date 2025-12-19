from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate

from .models import Post
from .forms import PostForm



def post_list(request):
    """
    首页：显示所有作者博客
    置顶优先，其次按发布时间倒序
    """
    posts = Post.objects.filter(
        published_date__lte=timezone.now()
    ).order_by('-is_pinned', '-published_date')

    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})




def situp_stats(request):
    """
    모든 사용자
    날짜별 총 윗몸일으키기 개수 (text 내 situp count 합산)
    """
    posts = Post.objects.filter(
        published_date__isnull=False
    )

    daily_sum = {}

    for post in posts:
        if post.text:
            import re
            match = re.search(r'situp\s*count\s*=\s*(\d+)', post.text, re.IGNORECASE)
            if match:
                count = int(match.group(1))
                day = post.published_date.strftime('%Y-%m-%d')

                if day not in daily_sum:
                    daily_sum[day] = 0
                daily_sum[day] += count

    dates = sorted(daily_sum.keys())
    counts = [daily_sum[d] for d in dates]

    return render(request, 'blog/stats.html', {
        'dates': dates,
        'counts': counts
    })





from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import PostSerializer


class BlogImages(viewsets.ModelViewSet):
    """
    REST API (Upload / Manage)
    GET  /api_root/posts/
    POST /api_root/posts/
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Post.objects.filter(
            published_date__lte=timezone.now()
        ).order_by('-published_date')

    def create(self, request, *args, **kwargs):
        """
        multipart/form-data 업로드 대응
        title / text 없을 경우 자동 생성
        """
        data = request.data.copy()

        if 'title' not in data:
            data['title'] = 'Android Upload'
        if 'text' not in data:
            data['text'] = 'Image uploaded from Android client'

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        serializer.save(
            author=request.user if request.user.is_authenticated else None,
            published_date=timezone.now()
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ImageListView(viewsets.ReadOnlyModelViewSet):
    """
    Image List & Retrieve API (Read Only)
    GET /api_root/images/
    GET /api_root/images/{id}/
    """
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Post.objects.filter(
            published_date__lte=timezone.now()
        ).order_by('-is_pinned', '-published_date')
