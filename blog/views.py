from math import ceil
from django.http.response import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Category, Blog, BlogComment
from django.contrib import messages
from blog.templatetags import extras
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from taggit.models import Tag
from .forms import BlogForm
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

# Create your views here.
def bloghome(request):
    category = Category.objects.order_by('name')[:12]
    blog = Blog.objects.order_by('?')[:3]
    posts = Blog.objects.all().order_by('-timestamp')[0:16]
    n = len(posts)
    nSlides = n//4 + ceil((n/4)-(n//4))
    return render(request, 'blog/blog home.html', {'category':category, 'blog':blog, 'posts':posts, 'nSlides':nSlides, 'range':range(1, nSlides),})

def blogcategory(request, slug):
    category = Category.objects.get(slug=slug)
    blogpost = Blog.objects.filter(category=category)
    return render(request, 'blog/blog category.html', {'blogpost':blogpost, 'category':category})

def category(request):
    category = Category.objects.order_by('name')
    blog = Blog.objects.order_by('-timestamp')
    page = request.GET.get('page', 1)

    paginator = Paginator(blog, 20)
    try:
        blog = paginator.page(page)
    except PageNotAnInteger:
        blog = paginator.page(1)
    except EmptyPage:
        blog = paginator.page(paginator.num_pages)
    return render(request, 'blog/all category.html', {'category':category, 'blog':blog})

def blogPost(request, slug): 
    post=Blog.objects.get(slug=slug)
    post.views= post.views +1
    post.save()
    comments= BlogComment.objects.filter(post=post, parent=None)
    replies= BlogComment.objects.filter(post=post).exclude(parent=None)
    replyDict = {}
    for reply in replies:
        if reply.parent.id not in replyDict.keys():
            replyDict[reply.parent.id]=[reply]
        else:
            replyDict[reply.parent.id].append(reply)
    context={'post':post, 'comments': comments, 'user': request.user, 'replyDict':replyDict}
    return render(request, "blog/blogPost.html", context)

def postComment(request):
    if request.method == "POST":
        comment=request.POST.get('comment')
        user=request.user
        postSno =request.POST.get('postSno')
        post= Blog.objects.get(id=postSno)
        parentSno= request.POST.get('parentSno')
        if parentSno == "":
            comment=BlogComment(comment= comment, user=user, post=post)
            comment.save()
            messages.success(request, "Your comment has been posted successfully!")
        else:
            parent= BlogComment.objects.get(id=parentSno)
            comment=BlogComment(comment= comment, user=user, post=post , parent=parent)
            comment.save()
            messages.success(request, "Your reply has been posted successfully!")
    return redirect(f"/blog/article/{post.slug}")

def tagged(request, slug):
    category = Category.objects.order_by('name')
    tag = get_object_or_404(Tag, slug=slug)
    common_tags = Blog.tags.most_common()[:5]
    posts = Blog.objects.filter(tags=tag)
    context = {
        'tag':tag,
        'common_tags':common_tags,
        'blog':posts,
        'category':category,
    }
    return render(request, 'blog/all category.html', context)

@login_required(login_url='/account/login')
def writeForUs(request):
    form = BlogForm()
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            newpost = form.save(commit=False)
            newpost.author = request.user
            newpost.save()
            form.save_m2m()
            messages.success(request, "Your blog has been published successfully!")
    else:
        form = BlogForm()
    context = {
        'form':form
    }
    return render(request, 'blog/write for us.html', context)

def search(request):
    query=request.GET['query']
    if len(query)>78 or len(query)<1:
        allPosts=Blog.objects.none()
    else:
        allPostsTitle= Blog.objects.filter(title__icontains=query)
        allPostsContent =Blog.objects.filter(content__icontains=query)
        allPosts=  allPostsTitle.union(allPostsContent)
    if allPosts.count()==0:
        messages.warning(request, "No search results found. Please refine your query.")
    params={'allPosts': allPosts, 'query': query}
    return render(request, 'blog/search.html', params)

class BlogEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Blog
    form_class = BlogForm
    template_name = 'blog/blog edit.html'
    success_message = 'Your blog has been updated!'
    success_url = reverse_lazy('blog-list')

class BlogDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Blog
    template_name = 'blog/blog delete.html'
    fields = '__all__'
    success_message = 'Your blog has been deleted successfully!'
    success_url = reverse_lazy('blog-list')

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.author == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's articles.")