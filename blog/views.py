from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag



# Create your views here.

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status = Post.Status.PUBLISHED)
    comment= None

    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)#create a comment instance without saving it to the database
        comment.post = post
        comment.save()
    
    return render(request, 'blog/post/comment.html', {
        'post': post,
        'form': form,
        'comment': comment
    })


def post_share(request, post_id):
    post = get_object_or_404(Post, id= post_id, status = Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        #fORM WAS SUBMITTED
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            #send email
            post_url = request.build_absolute_uri(post.get_absolute_url())

            subject = f"{cd['name']} recommends you read " \
                    f"{post.title}"
            
            message = f"Read {post.title} at {post_url}\n\n"\
            f"{cd['name']}\'s comments: {cd['comments']}"

            send_mail(subject, message, 'onuhudoudo@gmail.com', [cd['to']])
            sent =True
        
    else:
        form = EmailPostForm()
    
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        #__in is used to filter objects based on a list of values
        post_list = post_list.filter(tags__in=[tag])
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)#retrieving the http parameter "page"4
    try:
        posts = paginator.page(page_number)#paginator.page returns a page object 
    except EmptyPage:
         # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages) #paginator.num_pages returns the total number of pages available 
    except PageNotAnInteger:
        posts = paginator.page(1)
    return render(request, 'blog/post/list.html', {
        'posts': posts,
        'tag': tag})

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, slug= post, publish__year=year, publish__month=month, publish__day=day)

    #list of active comments for this post
    comments = post.comments.filter(active=True)

    #form for users to comment
    form = CommentForm()
    return render(request, 'blog/post/detail.html', {
        'post': post,
        'comments': comments,
        'form': form})
