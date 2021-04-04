from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from .decorators import shop_owner_required, user_required
from .forms import ShopOwnerSignUpForm, UserSignUpForm, LoginForm, ConsumerInterestsForm, PostForm
from .models import CustomUser, Consumer, ShopOwner, Notification
from django.contrib.auth import views as auth_views
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth import update_session_auth_hash, login, authenticate
from social_django.models import UserSocialAuth
from .models import Profile, FollowUser, Post, PostComment, PostLike, PostFileContent
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView, DetailView
from pazar.models import Category, Product, Skill, Free_Listing, Customer
from .forms import UserForm, ProfileForm, CommentForm
from django.http.response import HttpResponseRedirect, HttpResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.template import loader
from taggit.models import Tag
# Create your views here.
def SignUpView(request):
    return render(request, 'accounts/signup.html')

def activation_sent_view(request):
    return render(request, 'activation_sent.html')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true 
        user.is_active = True
        # set signup_confirmation true
        user.signup_confirmation = True
        user.save()
        login(request, user)
        if request.user.is_shop_owner:
            return redirect('Dashboard')
        else:
            return redirect('home')
        messages.success(request, 'Congratulations! Logged in successfully.')
        return redirect('home')
    else:
        return render(request, 'activation_invalid.html')

def ShopOwnerSignUpView(request):
    user_type = 'Business Owner'
    form = ShopOwnerSignUpForm()
    if request.method == "POST":
        form = ShopOwnerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.username = form.cleaned_data.get('username')
            # shop_owner = ShopOwner.objects.create(user=user)
            # shop_owner.save()
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            # load a template like get_template() 
            # and calls its render() method immediately.
            message = render_to_string('activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return render(request,'activation_sent.html')
    else:
        form = ShopOwnerSignUpForm()
    return render(request, 'accounts/business_owner_signup_form.html', {'form':form, 'user_type':user_type})
    
# class ShopOwnerSignUpView(CreateView):
#     model = CustomUser
#     form_class = ShopOwnerSignUpForm
#     template_name = 'accounts/signup_form.html'

#     def get_context_data(self, **kwargs):
#         kwargs['user_type'] = 'Business Owner'
#         return super().get_context_data(**kwargs)

#     def form_valid(self,form):
#         user = form.save()
#         login(self.request, user)
#         return redirect('/')

def UserSignUpView(request):
    user_type = 'User'
    form = UserSignUpForm()
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.username = form.cleaned_data.get('username')
            # shop_owner = ShopOwner.objects.create(user=user)
            # shop_owner.save()
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            # load a template like get_template() 
            # and calls its render() method immediately.
            message = render_to_string('activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return render(request,'activation_sent.html')
    else:
        form = UserSignUpForm()
    return render(request, 'accounts/user_signup_form.html', {'form':form, 'user_type':user_type})

# class UserSignUpView(CreateView):
#     model = CustomUser
#     form_class = UserSignUpForm
#     template_name = 'accounts/signup_form.html'

#     def get_context_data(self, **kwargs):
#         kwargs['user_type'] = 'User'
#         return super().get_context_data(**kwargs)

#     def form_valid(self,form):
#         user = form.save()
#         login(self.request, user)
#         return redirect('/')

class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('home')

    # def get_context_data(self, *args, **kwargs):
    #     context = super(LoginView, self).get_context_data(*args, **kwargs)
    #     context["next"] = self.request.GET.get('next') 
    #     return context

    def form_valid(self, form):
        messages.success(self.request, 'Congratulations! Logged in successfully!')
        return super().form_valid(form)

    # def get_success_url(self, *args, **kwargs):
    #     return reverse('home')

    def get_success_url(self, *args, **kwargs):
        success_url = reverse_lazy('home')
        next_url = self.request.POST.get('next')
        if next_url:
            return next_url
        else:
            return success_url
    

    # def get_success_url(self, *args, **kwargs):
    #     next_url = self.request.POST.get('next')
    #     success_url = reverse('home')
    #     if next_url:
    #         success_url += '?next={}'.format(next_url)
    #     return success_url

# class ProfileEditView(UpdateView):
#     model = Profile
#     fields = ['name', 'age', 'birthday', 'gender', 'bio', 'description', 'address', 'phone_no', 'website', 'facebook', 'instagram', 'twitter', 'github', 'linkedin', 'youtube', 'pinterest', 'pic']
#     template_name = 'registration/edit-profile.html'

#     def get_success_url(self):
#         return reverse('index')

#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         return super().form_valid(form)

#     def get_object(self):
#         return self.request.user.profile

class ProfileEditView(LoginRequiredMixin, TemplateView):
    user_form = UserForm
    profile_form = ProfileForm
    template_name = 'registration/edit-profile.html'

    def post(self, request):
        post_data = request.POST or None
        file_data = request.FILES or None
        user_form = UserForm(post_data, instance=request.user)
        profile_form = ProfileForm(post_data, file_data, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your Profile is updated successfully!')
            return HttpResponseRedirect(reverse_lazy('home'))

        context = self.get_context_data(user_form=user_form, profile_form=profile_form)

        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'pazar/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slug'] = Profile.slug
        context['pk'] = Profile.pk
        context['skills'] = Skill.objects.filter(user=self.request.user)
        context['shop'] = Free_Listing.objects.filter(Listed_by=self.request.user)
        context['customer'] = Customer.objects.filter(user=self.request.user)
        context['product'] = Product.objects.filter(user=self.request.user)
        return context

    def get_object(self):
        return self.request.user.profile

@method_decorator([login_required, user_required], name='dispatch')
class ConsumerInterestsView(UpdateView):
    model = Consumer
    form_class = ConsumerInterestsForm
    template_name = 'accounts/interests_form.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user.consumer

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consumer = self.request.user.consumer
        consumer_interests = consumer.interests.values_list('pk', flat=True)
        interests = Category.objects.filter(id__in=consumer_interests)
        context['interests'] = interests
        return context

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile detail.html'
    login_url = '/account/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs['pk']
        user = CustomUser.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        profiles = CustomUser.objects.filter(id=id)
        for p1 in profiles:
            p1.followed = False
            ob = FollowUser.objects.filter(follower=p1, following=self.request.user)
            if ob:
                p1.followed = True
        context["profile"] = profile
        context["profiles"] = profiles
        return context

def follow(request, pk):
    user = CustomUser.objects.get(pk=pk)
    FollowUser.objects.create(follower=user, following=request.user)
    return HttpResponseRedirect(redirect_to=reverse_lazy('profile-detail', args=[user.pk, user.profile.slug]))

def unfollow(request, pk):
    user = CustomUser.objects.get(pk=pk)
    FollowUser.objects.filter(follower=user, following=request.user).delete()
    return HttpResponseRedirect(redirect_to=reverse_lazy('profile-detail', args=[user.pk, user.profile.slug]))

def like(request, pk):
    post = Post.objects.get(pk=pk)
    PostLike.objects.create(post=post, liked_by=request.user)
    return HttpResponseRedirect(redirect_to=reverse_lazy('posts'))

def likePost(request, pk):
    post = Post.objects.get(pk=pk)
    PostLike.objects.create(post=post, liked_by=request.user)
    return HttpResponseRedirect(redirect_to=reverse_lazy('post-detail', args=[pk]))

def unlike(request, pk):
    post = Post.objects.get(pk=pk)
    PostLike.objects.filter(post=post, liked_by=request.user).delete()
    return HttpResponseRedirect(redirect_to=reverse_lazy('posts'))

def unlikePost(request, pk):
    post = Post.objects.get(pk=pk)
    PostLike.objects.filter(post=post, liked_by=request.user).delete()
    return HttpResponseRedirect(redirect_to=reverse_lazy('post-detail', args=[pk]))

class PostCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('')
    success_message = 'Posted successfully!'
    template_name = 'accounts/add post.html'

    def form_valid(self,form):
        post = form.save(self.request.user)
        form.instance.uploaded_by = self.request.user
        images = self.request.FILES.getlist('pic')
        for i in images:
            PostFileContent.objects.create(post=post, file=i)
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    login_url = '/account/login'
    template_name = 'accounts/post list.html'

class PostEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('posts')
    success_message = 'Post has been updated successfully!'
    template_name = 'accounts/edit post.html'

    # def form_valid(self, form):
    #     form.instance.uploaded_by = self.request.user
    #     user = self.request.user
    #     if form.instance.uploaded_by == user:
    #         return super().form_valid(form)
    #     else:
    #         form.add_error(None, "You need to be the author of the post in order to edit it.")
    #         return super().form_invalid(form)

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs

class PostDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Post
    template_name = 'accounts/delete post.html'
    fields = '__all__'
    success_message = 'Your post has been deleted successfully!'
    success_url = reverse_lazy('posts')

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        obj = Post.objects.get(pk=pk)
        if not obj.uploaded_by == self.request.user:
            messages.warning(self.request, 'You need to be the author of the post in order to delete it.')
        return obj

@login_required
def favourite(request, pk):
    user = request.user
    post = Post.objects.get(id=pk)
    profile = Profile.objects.get(user=user)
    if profile.favourites.filter(id=pk).exists():
        profile.favourites.remove(post)
    else:
        profile.favourites.add(post)
    return HttpResponseRedirect(reverse("post-detail", args=[pk]))

def CountNotifications(request):
    count_notifications = 0
    if request.user.is_authenticated:
        count_notifications = Notification.objects.filter(user=request.user, is_seen=False).count()
    return {'count_notifications':count_notifications}

@login_required(login_url='/account/login')
def post_comment_create_and_list_view(request):
    qs = Post.objects.all().order_by('-cr_date')
    for p1 in qs:
        p1.liked = False
        ob = PostLike.objects.filter(post=p1, liked_by=request.user)
        if ob:
            p1.liked = True
        oblist = PostLike.objects.filter(post=p1)
        p1.likedNo = oblist.count()
    followedList = FollowUser.objects.filter(following=request.user)
    followedList2 = []
    for e in followedList:
        followedList2.append(e.follower)
    post_list = Post.objects.filter(uploaded_by__in = followedList2).order_by('-cr_date')
    for post1 in post_list:
        post1.liked1 = False
        object = PostLike.objects.filter(post=post1, liked_by=request.user)
        if object:
            post1.liked1 = True
        objectlist = PostLike.objects.filter(post=post1)
        post1.likedno = objectlist.count()
    myPosts = Post.objects.filter(uploaded_by=request.user)
    for myPost in myPosts:
        myPost.likes = False
        myPostList = PostLike.objects.filter(post=myPost, liked_by=request.user)
        if myPostList:
            myPost.likes = True
        myPost_list = PostLike.objects.filter(post=myPost)
        myPost.likesNo = myPost_list.count()
    comment_form = CommentForm()
    profile = Profile.objects.get(user=request.user)
    # if 'submit_p_form' in request.POST:
    #     post_form = PostForm(request.POST, request.FILES)
    #     if post_form.is_valid():
    #         post = post_form.save(commit=False)
    #         post_form.uploaded_by = request.user
    #         post.save()
    #         messages.success(request, 'Posted Successfully!')
    # post_form = PostForm()
    # if request.method == 'POST':
    #     post_form = PostForm(request.POST, request.FILES)
    #     if post_form.is_valid():
    #         post_form = post_form.save(commit=False)
    #         post_form.uploaded_by = request.user
    #         post_form.save()
    #         messages.success(request, 'Posted Successfully')
    
    if 'submit_c_form' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            instance = comment_form.save(commit=False)
            instance.commented_by = request.user
            instance.post = Post.objects.get(id=request.POST.get('pk'))
            instance.save()
            messages.success(request, 'Commented Successfully!')
            comment_form = CommentForm()

    count_notifications = 0
    if request.user.is_authenticated:
        count_notifications = Notification.objects.filter(user=request.user, is_seen=False).count()
    
    context = {
        'qs':qs,
        'profile':profile,
        'c_form':comment_form,
        'post_list':post_list,
        'myPosts':myPosts,
        'count_notifications':count_notifications,
    }
    return render(request, 'accounts/post list.html', context)

@login_required(login_url='/account/login')
def PostDetail(request, pk):
    post = get_object_or_404(Post, id=pk)
    user =request.user
    profile = Profile.objects.get(user=user)
    favourited = False
    comments = PostComment.objects.filter(post=post).order_by('-cr_date')
    post.liked = False
    ob = PostLike.objects.filter(post=post, liked_by=request.user)
    if ob:
        post.liked = True
        obList = PostLike.objects.filter(post=post)
        post.likedNo = obList.count()

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=user)
        if profile.favourites.filter(id=pk).exists():
            favourited = True

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.commented_by = user
            comment.save()
            messages.success(request, 'Commented Successfully!')
            return HttpResponseRedirect(reverse('post-detail', args=[pk]))
    else:
        form = CommentForm()
    
    template = loader.get_template('accounts/post detail.html')

    context = {
        'post': post,
        'favourited':favourited,
        'profile':profile,
        'form':form,
        'comments':comments
    }
    return HttpResponse(template.render(context, request))

def tags(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    common_tags = Post.tags.most_common()[:10]
    posts = Post.objects.filter(tags=tag)
    context = {
        'tag':tag,
        'common_tags':common_tags,
        'posts':posts,
    }
    return render(request, 'accounts/post tag.html', context)

@login_required(login_url='/account/login')
def showNotifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')
    Notification.objects.filter(user=user, is_seen=False).update(is_seen=True)
    template = loader.get_template('accounts/notifications.html')
    context = {
        'notifications':notifications,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='/account/login')
def DeleteNotification(request, pk):
    user = request.user
    Notification.objects.filter(id=pk, user=user).delete()
    return redirect('show-notifications')

def AddPost(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.uploaded_by = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Posted Successfully')
            return redirect('post-detail', post.id)
    else:
        form = PostForm()
    return render(request, 'accounts/add post.html', {'form':form})