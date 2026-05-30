from django.shortcuts import render, get_object_or_404
from .models import BlogPost

def post_list(request):
    posts = BlogPost.objects.filter(is_published=True).select_related('author').prefetch_related('tags').order_by('-published_at')
    
    from django.core.paginator import Paginator
    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'blog/post_list.html', {'posts': page_obj})

def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, 'blog/post_detail.html', {'post': post})
