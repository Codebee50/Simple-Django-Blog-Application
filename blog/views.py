from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
def post_list(request):

    post_list = Post.published.all()

    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)#retrieving the http parameter "page"4
    try:
        posts = paginator.page(page_number)#paginator.page returns a page object 
    except EmptyPage:
         # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages) #paginator.num_pages returns the total number of pages available 
    except PageNotAnInteger:
        posts = paginator.page(1)

    
    return render(request, 'post/list.html', {'posts': posts})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug= post, publish__year=year, publish__month=month, publish__day=day)

    return render(request, 'post/detail.html', {'post': post})