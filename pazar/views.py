from accounts.views import tags
import re
from django.db.models.expressions import F
# from django.db.models.fields import json
from django.http.response import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, request
from django.contrib import messages
from datetime import datetime
from .models import Advertise_with_Us, Attendance, AttendanceReport, Contact, Comment, Feedback, Product_Category, SkillImages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, TemplateView, DetailView, UpdateView, DeleteView, CreateView, ListView, View
from .forms import Free_ListingForm, CommentForm, PurchaseItemForm, SelectQuotationCustomerForm, QuotationItemForm, QuotationItemFormset, EmployeeAttendanceFormset, AttendanceForm, FeedbackForm, AdvertiseCommentForm
from .models import Free_Listing, Subcategory, FreeListingImage, AdvertiseWithUsImage, Category,Subcategory, Comment, Customer, Skill, Product, Stock, Supplier, SaleItem, SaleBill, PurchaseItem, PurchaseBill, QuotationItem, QuotationBill, Sale, Employee, FAQ, Testimonial, SkillImages, AdvertiseComment
from django.urls import reverse, reverse_lazy
from .forms import Advertise_With_UsForm, CustomerForm, SkillForm, ProductForm, SelectSupplierForm, PurchaseItemFormset, SupplierForm,SaleItemFormset, StockForm, SelectCustomerForm, SaleForm, EmployeeForm
from accounts.decorators import user_required, shop_owner_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from blog.models import Blog
from accounts.models import CustomUser, Profile
from django_filters.views import FilterView
from .filters import StockFilter
from django.forms import formset_factory, formsets, modelformset_factory
from num2words import num2words
from math import ceil
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from taggit.models import Tag
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# Create your views here.
def index(request):
    faqs = FAQ.objects.all()[:7]
    blogs = Blog.objects.order_by('-timestamp')[:4]
    listing = Free_Listing.objects.all().count()
    profile = Profile.objects.all().count()
    customers = Customer.objects.all().count()
    saleBill = SaleBill.objects.all().count()
    purchaseBill = PurchaseBill.objects.all().count()
    invoices = str(int(saleBill) + int(purchaseBill))
    return render(request, 'pazar/index.html', {'listing':listing, 'profile':profile, 'customers':customers, 'invoices':invoices, 'faqs':faqs, 'blogs':blogs})

@login_required
def home(request):
    listing = Free_Listing.objects.all().order_by('-Listed_at')[0:6]
    advertisement = Advertise_with_Us.objects.all().order_by('-Added_at')[0:6]
    categories = Category.objects.order_by('?')[0:9]
    products = Product.objects.all().order_by('-date')[0:8]
    blogs = Blog.objects.all().order_by('-timestamp')[0:3]
    if request.user.is_shop_owner:
        listing = Free_Listing.objects.all().order_by('-Listed_at')[0:6]
        advertisement = Advertise_with_Us.objects.all().order_by('-Added_at')[0:6]
        categories = Category.objects.order_by('?')[0:9]
        products = Product.objects.all().order_by('-date')[0:8]
        blogs = Blog.objects.all().order_by('-timestamp')[0:3]
        return render(request, 'pazar/home.html', {'blogs':blogs, 'listing':listing, 'categories':categories, 'products':products,'advertisement':advertisement,})
    if request.user.is_user:
        consumer = request.user.consumer
        consumer_interests = consumer.interests.values_list("pk", flat=True)
        interests = Category.objects.filter(id__in=consumer_interests).order_by('name')[0:9]
        queryset = Free_Listing.objects.filter(Business_Category__in=consumer_interests).order_by('-Listed_at')[0:6]
        advertise = Advertise_with_Us.objects.filter(Business_Category__in=consumer_interests).order_by('-Added_at')[0:6]
        return render(request, 'pazar/home.html', {'interests':interests, 'listings':queryset, 'advertise':advertise})
    return render(request, 'pazar/home.html', {'blogs':blogs, 'listing':listing, 'categories':categories, 'products':products,'advertisement':advertisement,})

@method_decorator([login_required, user_required], name="dispatch")
class InterestedCategoryView(ListView):
    model = Category
    ordering = ('name')
    context_object_name = 'categories'
    template_name = 'pazar/interested category.html'
    login_url = '/account/login'

    def get_queryset(self):
        consumer = self.request.user.consumer
        consumer_interests = consumer.interests.values_list("pk", flat=True)
        queryset = Category.objects.filter(id__in=consumer_interests)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.order_by('name')
        return context

@method_decorator([login_required, user_required], name="dispatch")
class CategoryListingView(ListView):
    model = Free_Listing
    ordering = ('-Listed_at')
    context_object_name = 'listings'
    template_name = 'pazar/category listing.html'
    login_url = '/account/login'

    def get_queryset(self):
        consumer = self.request.user.consumer
        consumer_interests = consumer.interests.values_list("pk", flat=True)
        queryset = Free_Listing.objects.filter(Business_Category__in=consumer_interests)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consumer = self.request.user.consumer
        consumer_interests = consumer.interests.values_list("pk", flat=True)
        advertise = Advertise_with_Us.objects.filter(Business_Category__in=consumer_interests)
        context['category'] = Category.objects.order_by('name')
        context['advertise'] = advertise
        return context

@method_decorator([login_required, user_required], name="dispatch")
class InterestedProductView(ListView):
    model = Product
    ordering = ('-date')
    context_object_name = 'products'
    template_name = 'pazar/interested product.html'
    login_url = '/account/login'

    def get_queryset(self):
        consumer = self.request.user.consumer
        consumer_interests = consumer.interests.values_list("pk", flat=True)
        shops = Free_Listing.objects.filter(Business_Category__in=consumer_interests)
        products = Product.objects.filter(shop__in=shops)
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Product_Category.objects.order_by('name')
        return context

def listingList(request):
    listings = Free_Listing.objects.all().order_by('-Listed_at')
    advertise = Advertise_with_Us.objects.all().order_by('-Added_at')
    category = Category.objects.order_by('name')
    return render(request, 'pazar/listing list.html', {'listings':listings, 'category':category, 'advertise':advertise})

def productList(request):
    products = Product.objects.all().order_by('-date')
    cats = Product_Category.objects.all().order_by('name')
    return render(request, 'pazar/products.html', {'products':products, 'cats':cats})

def productCategoryDetail(request, pk, slug):
    cats = Product_Category.objects.order_by('name')
    cat = Product_Category.objects.get(id=pk, slug=slug)
    products = Product.objects.filter(category=cat).order_by('-date')
    return render(request, 'pazar/product category detail.html', {'products':products, 'cat':cat, 'cats':cats})

def contact(request):
    if request.method =="POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        msg = request.POST. get('msg')

        if len(name)<2 or len(email)<3 or len(phone)<10 or len(msg)<5:
            messages.warning(request, "Please fill the form correctly")
        else:
            contact = Contact(name=name, email=email, phone=phone, msg=msg, date=datetime.today())
            contact.save()
            messages.success(request, 'Your Queries has been Successfully Sent!')
    return render(request, 'pazar/contact.html')

def about(request):
    return render(request, 'pazar/about.html')

def services(request):
    return render(request,'pazar/services.html')

def categories(request):
    category = Category.objects.order_by('name')
    return render(request, 'pazar/categories.html', {'category':category})

def Search(request):
    query=request.GET['query']
    if len(query)>78 or len(query)<1:
        cats = Category.objects.none()
        subcats = Subcategory.objects.none()
        listings = Free_Listing.objects.none()
        sale = Sale.objects.none()
        profiles = Profile.objects.none()
        products = Product.objects.none()
    else:
        cats = Category.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)).distinct()
        subcats = Subcategory.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)).distinct()
        listings = Free_Listing.objects.filter(Q(Business_Name__icontains=query) | Q(Business_Email__icontains=query) | Q(Business_Address__icontains=query) | Q(Business_Telephone__icontains=query) | Q(Business_WhatsApp__icontains=query) | Q(Business_Description__icontains=query)).distinct()
        sale = Sale.objects.filter(Q(name__icontains=query) | Q(description__icontains=query)).distinct()
        profiles = Profile.objects.filter(Q(name__icontains=query) | Q(bio__icontains=query) | Q(description__icontains=query) | Q(address__icontains=query) | Q(phone_no__icontains=query))
        products = Product.objects.filter(Q(name__icontains=query) | Q(desc__icontains=query) | Q(price__icontains=query) | Q(offer_price__icontains=query)).distinct()
    if cats.count() == 0 and subcats.count() == 0 and listings.count() == 0 and sale.count() == 0 and profiles.count() == 0 and products.count() == 0:
        messages.warning(request, "No search results found. Please refine your query.")
    params = {
        'cats': cats,
        'subcats': subcats,
        'query': query,
        'listings':listings,
        'sale': sale,
        'profiles':profiles,
        'products':products,
    }
    return render(request, 'pazar/Search.html', params)

def logoutpage(request):
    logout(request)
    return redirect('logout')

@method_decorator([login_required, shop_owner_required], name='dispatch')
class Free_ListingView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = "pazar/Free Listing.html"
    form_class = Free_ListingForm
    success_message = "Your Business %(Business_Name)s has been listed successfully!"

    def form_valid(self, form):
        listing = form.save(self.request.user)
        form.save_m2m()
        images = self.request.FILES.getlist('Business_Images')
        for i in images:
            FreeListingImage.objects.create(listing=listing,image=i)
        return super(Free_ListingView, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("Free Listing")

@method_decorator([login_required, shop_owner_required], name='dispatch')
class Advertise_With_UsView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = "pazar/Advertise With Us.html"
    form_class = Advertise_With_UsForm
    success_message = "Your Business %(Business_Name)s has been added successfully!"

    def form_valid(self, form):
        advertise = form.save(self.request.user)
        form.save_m2m()
        images = self.request.FILES.getlist('Business_Images')
        for i in images:
            AdvertiseWithUsImage.objects.create(advertise=advertise,image=i)
        return super(Advertise_With_UsView, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("Advertise With Us")

@method_decorator([login_required, shop_owner_required], name='dispatch')
class DashboardView(LoginRequiredMixin, View):
    login_url = '/account/login'
    template_name = 'pazar/dashboard.html'

    def get(self, request):
        labels = []
        data = []
        stockqueryset = Stock.objects.filter(user=request.user)
        for item in stockqueryset:
            labels.append(item.name)
            data.append(item.quantity)
        sales = SaleBill.objects.filter(user=request.user).order_by('-time')[:3]
        purchases = PurchaseBill.objects.filter(user=request.user).order_by('-time')[:3]
        context = {
            'labels':labels,
            'data':data,
            'sales':sales,
            'purchases':purchases
        }
        return render(request, self.template_name, context)

def load_subcategory(request):
    category_id = request.GET.get('Business_Category')
    subcategory = Subcategory.objects.filter(category_id=category_id).order_by('name')
    return render(request, 'pazar/subcategory_dropdown_list_options.html', {'subcategory':subcategory})

def category_base(request):
    category = Category.objects.order_by('name')
    return render(request, 'category base.html', {'category':category})

class CategoryDetailView(TemplateView):
    template_name = 'pazar/subcategory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs['id']
        slug = self.kwargs['slug']
        name = Category.name
        categories = Category.objects.get(slug=slug, id=id)
        subcategory =  Subcategory.objects.filter(category__name=name).order_by('name')
        category = Category.objects.order_by("name")
        context['categories'] = categories
        context['subcategory'] = subcategory
        context['category'] = category
        return context

class SubcategoryDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'pazar/listing.html'
    login_url = '/account/login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = CustomUser.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        id = self.kwargs['id']
        slug = self.kwargs['slug']
        subcategories = Subcategory.objects.get(slug=slug, id=id)
        context['id'] = Subcategory.pk
        context['slug'] = Subcategory.slug
        context['subcategories'] = subcategories
        context['listing'] = Free_Listing.objects.filter(Business_Subcategory=subcategories).order_by('-Listed_at')
        context['advertise'] = Advertise_with_Us.objects.filter(Business_Subcategory=subcategories).order_by('-Added_at')
        context['category'] = Category.objects.order_by("name")
        context["profile"] = profile
        return context
    
class ListingDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'pazar/business_list.html'
    login_url = '/account/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs['id']
        slug = self.kwargs['slug']
        comments = Comment.objects.filter(listing_id=id)
        products = Product.objects.filter(shop_id=id)
        paginator = Paginator(comments, 3)
        page = self.request.GET.get('page')
        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)
        listing = Free_Listing.objects.get(pk=id,slug=slug)
        listing.view += 1
        listing.save()
        context['id'] = Free_Listing.pk
        context['slug'] = Free_Listing.slug
        context['listing'] = listing
        context['comments'] = comments
        context['products'] = products
        return context

class AdvertiseDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'pazar/advertise detail.html'
    login_url = '/account/login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs['id']
        slug = self.kwargs['slug']
        comments = AdvertiseComment.objects.filter(advertise_id=id)
        products = Product.objects.filter(shop_id=id)
        paginator = Paginator(comments, 3)
        page = self.request.GET.get('page')
        try:
            comments = paginator.page(page)
        except PageNotAnInteger:
            comments = paginator.page(1)
        except EmptyPage:
            comments = paginator.page(paginator.num_pages)
        advertise = Advertise_with_Us.objects.get(pk=id,slug=slug)
        advertise.view += 1
        advertise.save()
        context['id'] = Advertise_with_Us.pk
        context['slug'] = Advertise_with_Us.slug
        context['advertise'] = advertise
        context['comments'] = comments
        context['products'] = products
        return context

@login_required(login_url='/account/login')
def addcomment(request, id, slug):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            data = Comment()
            data.comment = form.cleaned_data['comment']
            data.rate = form.cleaned_data['rate']
            data.listing_id = id
            current_user = request.user
            data.commented_by_id = current_user.id
            data.save()
            messages.success(request, 'Your review has been sent. Thank you for your interest.')
            return HttpResponseRedirect(url)
    return HttpResponseRedirect(url)

@login_required(login_url='/account/login')
def addadvertisecomment(request, id, slug):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        form = AdvertiseCommentForm(request.POST)
        if form.is_valid():
            data = AdvertiseComment()
            data.comment = form.cleaned_data['comment']
            data.rate = form.cleaned_data['rate']
            data.advertise_id = id
            current_user = request.user
            data.commented_by_id = current_user.id
            data.save()
            messages.success(request, 'Your review has been sent. Thank you for your interest.')
            return HttpResponseRedirect(url)
    return HttpResponseRedirect(url)

@login_required(login_url='/account/login')
def shopList(request):
    listing = Free_Listing.objects.filter(Listed_by=request.user).order_by('-Listed_at')
    advertise = Advertise_with_Us.objects.filter(Added_by=request.user).order_by('-Added_at')
    return render(request, 'pazar/shop list.html', {'listing':listing, 'advertise':advertise})

@login_required(login_url='/account/login')
def shopDetail(request, id, slug):
    listing = get_object_or_404(Free_Listing, id=id, slug=slug)
    customer = Customer.objects.filter(shop=listing, user=request.user)
    return render(request, 'pazar/shop detail.html', {'listing':listing, 'customer':customer})

@login_required(login_url='/account/login')
def advertiseShopDetail(request, id, slug):
    advertise = get_object_or_404(Advertise_with_Us, id=id, slug=slug)
    return render(request, 'pazar/advertise shop detail.html', {'advertise':advertise})

class shopEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Free_Listing
    form_class = Free_ListingForm
    template_name = 'pazar/shop edit.html'
    login_url = '/account/login'
    success_url = reverse_lazy('shop-list')
    success_message = 'Your shop details has been updated!'

class advertiseEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Advertise_with_Us
    form_class = Advertise_With_UsForm
    template_name = 'pazar/advertise edit.html'
    login_url = '/account/login'
    success_url = reverse_lazy('shop-list')
    success_message = 'Your shop details has been updated!'

class shopDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Free_Listing
    template_name = 'pazar/shop delete.html'
    login_url = '/account/login'
    fields = '__all__'
    success_url = reverse_lazy('shop-list')
    success_message = 'Your shop has been deleted successfully!'

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.Listed_by == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's business listings.")

class advertiseDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Advertise_with_Us
    template_name = 'pazar/advertise delete.html'
    login_url = '/account/login'
    fields = '__all__'
    success_url = reverse_lazy('shop-list')
    success_message = 'Your shop has been deleted successfully!'

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.Added_by == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's business listings.")

@login_required(login_url='/account/login')
def customerList(request):
    listing = Free_Listing.objects.filter(Listed_by=request.user).order_by('-Listed_at')
    customer = Customer.objects.filter(user=request.user).order_by('-datetime')
    return render(request, 'pazar/customer list.html', {'customer':customer, 'listing':listing})

@login_required(login_url='/account/login')
def addCustomer(request):
    if request.method == "POST":
        form = CustomerForm(request.user, request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('customer-list')
    else:
        form = CustomerForm(request.user)
    return render(request, 'pazar/add customer.html', {'form':form})

class customerEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'pazar/customer edit.html'
    login_url = '/account/login'
    success_message = 'Your customer details has been updated!'
    success_url = reverse_lazy('customer-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
class customerDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Customer
    template_name = 'pazar/customer delete.html'
    login_url = '/account/login'
    fields = '__all__'
    success_message = 'Your customer has been deleted successfully!'
    success_url = reverse_lazy('customer-list')

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.user == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's customers.")

@login_required(login_url='/account/login')
def skillList(request):
    skills = Skill.objects.filter(user=request.user).order_by('-date')
    return render(request, 'pazar/skill list.html', {'skills':skills})

@login_required(login_url='/account/login')
def addSkill(request):
    form = SkillForm()
    if request.method == "POST":
        form = SkillForm(request.POST, request.FILES)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            images = request.FILES.getlist('images')
            for i in images:
                SkillImages.objects.create(skill=skill, images=i)
            messages.success(request, 'Skill added successfully!')
            if request.user.is_shop_owner:
                return redirect('skill-list')
            else:
                return redirect('add-skill')
    else:
        form = SkillForm()
    context = {
        'form':form,
        'skills':Skill.objects.all()
    }
    return render(request, 'pazar/add skill.html', context)

class skillEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = 'pazar/skill edit.html'
    login_url = '/account/login'
    success_message = 'Your skill has been updated!'
    success_url = reverse_lazy('skill-list')

class EditSkillView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Skill
    form_class = SkillForm
    template_name = 'pazar/skill edit.html'
    login_url = '/account/login'
    success_message = 'Your skill has been updated!'
    success_url = reverse_lazy('add-skill')

class skillDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Skill
    template_name = 'pazar/skill delete.html'
    login_url = '/account/login'
    fields = '__all__'
    success_message = 'Your skill has been deleted successfully!'
    success_url = reverse_lazy('skill-list')

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.user == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's skills.")

class DeleteSkillView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Skill
    template_name = 'pazar/skill delete.html'
    login_url = '/account/login'
    fields = '__all__'
    success_message = 'Your skill has been deleted successfully!'
    success_url = reverse_lazy('add-skill')

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.user == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's skills.")
    
@login_required(login_url='/account/login')
def blogList(request):
    blog = Blog.objects.filter(author=request.user).order_by('-timestamp')
    return render(request, 'pazar/blog list.html', {'blog':blog})

@login_required(login_url='/account/login')
def ProductList(request):
    listing = Free_Listing.objects.filter(Listed_by=request.user).order_by('-Listed_at')
    product = Product.objects.filter(user=request.user).order_by('-date')
    return render(request, 'pazar/product list.html', {'product':product, 'listing':listing})

@login_required(login_url='/account/login')
def AddProduct(request):
    if request.method == "POST":
        form = ProductForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product-list')
    else:
        form = ProductForm(request.user)
    return render(request, 'pazar/add product.html', {'form':form})

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'pazar/product detail.html'

class ProductEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'pazar/product edit.html'
    login_url = '/account/login'
    success_message = 'Your product has been updated!'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class ProductDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Product
    template_name = 'pazar/product delete.html'
    login_url = '/account/login'
    fields = '__all__'
    success_message = 'Your product has been deleted successfully!'
    success_url = reverse_lazy('product-list')

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.user == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's products.")

class StockListView(LoginRequiredMixin, FilterView):
    filterset_class = StockFilter
    template_name = 'pazar/inventory.html'
    ordering = ['-date']
    login_url = '/account/login'
    paginate_by = 10

    def get_queryset(self):
        return Stock.objects.filter(user=self.request.user)

class StockCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Stock
    form_class = StockForm
    template_name = 'pazar/add stock.html'
    login_url = '/account/login'
    success_url = reverse_lazy('inventory')
    success_message = 'Stock has been created successfully!'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class StockUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Stock
    form_class = StockForm
    template_name = 'pazar/edit stock.html'
    login_url = '/account/login'
    success_url = reverse_lazy('inventory')
    success_message = 'Stock has been updated successfully!'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class StockDeleteView(LoginRequiredMixin, View):
    template_name = 'pazar/delete stock.html'
    login_url = '/account/login'
    success_message = 'Stock has been deleted successfully!'

    def get(self,request,pk):
        stock = get_object_or_404(Stock, pk=pk)
        return render(request, self.template_name, {'object':stock})

    def post(self, request, pk):
        stock = get_object_or_404(Stock, pk=pk)
        stock.delete()
        messages.success(request, self.success_message)
        return redirect('inventory')

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'pazar/supplier list.html'
    ordering = ['-date']
    login_url = '/account/login'
    paginate_by = 10

    def get_queryset(self):
        return Supplier.objects.filter(user=self.request.user)

class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    success_url = reverse_lazy('supplier-list')
    success_message = 'Supplier has been created successfully!'
    template_name = 'pazar/add supplier.html'
    login_url = '/account/login'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class SupplierEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    success_url = reverse_lazy('supplier-list')
    success_message = 'Supplier details has been updated successfully!'
    template_name = 'pazar/edit supplier.html'
    login_url = '/account/login'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class SupplierDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Supplier
    template_name = 'pazar/delete supplier.html'
    login_url = '/account/login'
    fields = '__all__'
    success_message = 'Your supplier has been deleted successfully!'
    success_url = reverse_lazy('supplier-list')

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.user == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's suppliers.")

class SupplierView(LoginRequiredMixin, View):
    login_url = '/account/login'

    def get(self, request, name):
        supplierobj = get_object_or_404(Supplier, name=name)
        bill_list = PurchaseBill.objects.filter(supplier=supplierobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'supplier':supplierobj,
            'bills': bills
        }
        return render(request, 'pazar/supplier.html', context)

class PurchaseView(LoginRequiredMixin, ListView):
    model = PurchaseBill
    template_name = 'pazar/purchases list.html'
    login_url = '/account/login'
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

    def get_queryset(self):
        return PurchaseBill.objects.filter(user=self.request.user)

@login_required(login_url='/account/login')
def SelectSupplierView(request):
    form = SelectSupplierForm(request.user)
    if request.method == 'get':
        form = SelectSupplierForm(request.user, request.GET or None)
        return render(request, 'pazar/select supplier.html', {'form':form})
    if request.method == "POST":
        form = SelectSupplierForm(request.user, request.POST or None)
        if form.is_valid():
            supplierid = request.POST.get('supplier')
            supplier = get_object_or_404(Supplier, id=supplierid)
            shopid = request.POST.get('shop')
            shop = get_object_or_404(Free_Listing, id=shopid)
            return redirect('add-purchase', supplier.pk)
        return render(request, 'pazar/select supplier.html', {'form':form})
    return render(request, 'pazar/select supplier.html', {'form':form})

class PurchaseCreateView(LoginRequiredMixin, View):
    template_name = 'pazar/new purchase.html'
    login_url = '/account/login'

    def get(self, request, pk):
        formset = PurchaseItemFormset(request.GET or None ,form_kwargs = {'user':request.user})
        supplierobj = get_object_or_404(Supplier, pk=pk)
        context = {
            'formset':formset,
            'supplier':supplierobj
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = PurchaseItemFormset(request.POST or None, form_kwargs={'user':request.user})
        supplierobj = get_object_or_404(Supplier, pk=pk)
        shopobj = get_object_or_404(Free_Listing, pk=pk)
        if formset.is_valid():
            billobj = PurchaseBill(supplier=supplierobj, shop=shopobj)
            billobj.user = request.user
            billobj.save()
            for form in formset:
                billitem = form.save(commit=False)
                billitem.user = request.user
                billitem.billNo = billobj
                stock = get_object_or_404(Stock, name = billitem.stock.name)
                billitem.subTotalPrice = billitem.perPrice * billitem.quantity
                billitem.gstAmount = billitem.subTotalPrice * float(billitem.gst/100)
                billitem.discountAmount = billitem.subTotalPrice * float(billitem.discount)/100
                billitem.totalPrice = (billitem.subTotalPrice + billitem.gstAmount) - billitem.discountAmount
                stock.quantity +=billitem.quantity
                stock.user = request.user
                stock.save()
                billitem.save()
            messages.success(request, 'Purchased items have been registered successfully!')
            return redirect('purchase-bill', billNo=billobj.pk)
        formset = PurchaseItemFormset(request.GET or None, form_kwargs={'user':request.user})
        context = {
            'formset' :formset,
            'supplier':supplierobj
        }
        return render(request, self.template_name, context)

class PurchaseDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = PurchaseBill
    template_name = 'pazar/delete purchase.html'
    login_url = '/account/login'
    success_url = reverse_lazy('purchase-list')

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = PurchaseItem.objects.filter(billNo=self.object.pk)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.delete():
                stock.quantity -= item.quantity
                stock.save()
        messages.success(self.request, 'Purchase Bill has been deleted successfully!')
        return super(PurchaseDeleteView, self).delete(*args, **kwargs)

class CustomerView(LoginRequiredMixin, View):
    login_url = '/account/login'

    def get(self, request, name):
        customerobj = get_object_or_404(Customer, name=name)
        bill_list = SaleBill.objects.filter(customer=customerobj)
        page = request.GET.get('page', 1)
        paginator = Paginator(bill_list, 10)
        try:
            bills = paginator.page(page)
        except PageNotAnInteger:
            bills = paginator.page(1)
        except EmptyPage:
            bills = paginator.page(paginator.num_pages)
        context = {
            'customer':customerobj,
            'bills':bills,
        }
        return render(request, 'pazar/customer.html', context)

class SaleView(LoginRequiredMixin, ListView):
    model = SaleBill
    template_name = 'pazar/sale list.html'
    login_url = '/account/login'
    context_object_name = 'bills'
    ordering = ['-time']
    paginate_by = 10

    def get_queryset(self):
        return SaleBill.objects.filter(user=self.request.user)

@login_required(login_url='/account/login')
def SelectCustomerView(request):
    form = SelectCustomerForm(request.user)
    if request.method == 'get':
        form = SelectCustomerForm(request.user, request.GET or None)
        return render(request, 'pazar/select customer.html', {'form':form})
    if request.method == "POST":
        form = SelectCustomerForm(request.user, request.POST or None)
        if form.is_valid():
            customerid = request.POST.get('customer')
            customer = get_object_or_404(Customer, id=customerid)
            shopid = request.POST.get('shop')
            shop = get_object_or_404(Free_Listing, id=shopid)
            return redirect('add-sale', customer.pk)
        return render(request, 'pazar/select customer.html', {'form':form})
    return render(request, 'pazar/select customer.html', {'form':form})

class SaleCreateView(LoginRequiredMixin, View):
    template_name = 'pazar/new sale.html'
    login_url = '/account/login'

    def get(self, request, pk):
        formset = SaleItemFormset(request.GET or None, form_kwargs={'user':request.user})
        customerobj = get_object_or_404(Customer, pk=pk)
        context = {
            'formset':formset,
            'customer':customerobj,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = SaleItemFormset(request.POST or None, form_kwargs={'user':request.user})
        customerobj = get_object_or_404(Customer, pk=pk)
        shopobj = get_object_or_404(Free_Listing, pk=pk)
        if formset.is_valid():
            billobj = SaleBill(customer=customerobj, shop=shopobj)
            billobj.user = request.user
            billobj.save()
            for form in formset:
                billitem = form.save(commit=False)
                billitem.user = request.user
                billitem.billNo = billobj
                stock = get_object_or_404(Stock, name=billitem.stock.name)
                billitem.subTotalPrice = billitem.perPrice * billitem.quantity
                billitem.gstAmount = billitem.subTotalPrice * float(billitem.gst/100)
                billitem.discountAmount = billitem.subTotalPrice * float(billitem.discount/100)
                billitem.totalPrice = (billitem.subTotalPrice + billitem.gstAmount) - billitem.discountAmount
                stock.quantity -= billitem.quantity
                stock.user = request.user
                stock.save()
                billitem.save()
            messages.success(request, 'Sold items have been registered successfully!')
            return redirect('sale-bill', billNo=billobj.pk)
        formset = SaleItemFormset(request.GET or None, form_kwargs={'user':request.user})
        context = {
            'formset':formset,
            'customer':customerobj
        }
        return render(request, self.template_name, context)

class SaleDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = SaleBill
    template_name = 'pazar/delete sale.html'
    login_url = '/account/login'
    success_url = reverse_lazy('sale-list')

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        items = SaleItem.objects.filter(billNo=self.object.pk)
        for item in items:
            stock = get_object_or_404(Stock, name=item.stock.name)
            if stock.delete():
                stock.quantity += item.quantity
                stock.save()
        messages.success(self.request, 'Sale bill has been deleted successfully!')
        return super(SaleDeleteView, self).delete(*args, **kwargs)

class PurchaseBillView(LoginRequiredMixin, View):
    model = PurchaseBill
    template_name = 'pazar/purchase bill.html'
    login_url = '/account/login'

    def get(self, request, billNo):
        context = {
            'bill':PurchaseBill.objects.get(pk=billNo),
            'items':PurchaseItem.objects.filter(billNo=billNo),
        }
        return render(request, self.template_name, context)

    def post(self, request, billNo):
        context = {
            'bill':PurchaseBill.objects.get(pk=billNo),
            'items':PurchaseItem.objects.filter(billNo=billNo),
        }
        return render(request, self.template_name, context)

class SaleBillView(LoginRequiredMixin, View):
    model = SaleBill
    template_name = 'pazar/sale bill.html'
    login_url = '/account/login'

    def get(self, request, billNo):
        context = {
            'bill':SaleBill.objects.get(pk=billNo),
            'items':SaleItem.objects.filter(billNo=billNo),
        }
        return render(request, self.template_name, context)

    def post(self, request, billNo):
        context = {
            'bill':SaleBill.objects.get(pk=billNo),
            'items':SaleItem.objects.filter(billNo=billNo),
        }
        return render(request, self.template_name, context)

class QuotationListView(LoginRequiredMixin, ListView):
    model = QuotationBill
    template_name = 'pazar/quotation list.html'
    login_url = '/account/login'
    context_object_name = 'quotations'
    ordering = ['-date']
    paginate_by = 10

    def get_queryset(self):
        return QuotationBill.objects.filter(user=self.request.user)

@login_required(login_url='/account/login')
def SelectQuotationCustomerView(request):
    form = SelectQuotationCustomerForm(request.user)
    if request.method == 'get':
        form = SelectQuotationCustomerForm(request.user, request.GET or None)
        return render(request, 'pazar/select quotation customer.html', {'form':form})
    if request.method == "POST":
        form = SelectQuotationCustomerForm(request.user, request.POST or None)
        if form.is_valid():
            customerid = request.POST.get('customer')
            customer = get_object_or_404(Customer, id=customerid)
            shopid = request.POST.get('shop')
            shop = get_object_or_404(Free_Listing, id=shopid)
            return redirect('add-quotation', customer.pk)
        return render(request, 'pazar/select quotation customer.html', {'form':form})
    return render(request, 'pazar/select quotation customer.html', {'form':form})

class QuotationCreateView(LoginRequiredMixin, View):
    template_name = 'pazar/new quotation.html'
    login_url = '/account/login'

    def get(self, request, pk):
        formset = QuotationItemFormset(request.GET or None, form_kwargs={'user':request.user})
        customerobj = get_object_or_404(Customer, pk=pk)
        context = {
            'formset':formset,
            'customer':customerobj
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = QuotationItemFormset(request.POST or None, form_kwargs={'user':request.user})
        customerobj = get_object_or_404(Customer, pk=pk)
        shopobj = get_object_or_404(Free_Listing, pk=pk)
        if formset.is_valid():
            billobj = QuotationBill(customer=customerobj, shop=shopobj)
            billobj.user = request.user
            billobj.save()
            for form in formset:
                billitem = form.save(commit=False)
                billitem.user = request.user
                billitem.quoteNo = billobj
                billitem.subTotalPrice = billitem.perPrice * billitem.quantity
                billitem.gstAmount = billitem.subTotalPrice * float(billitem.gst/100)
                billitem.discountAmount = billitem.subTotalPrice * float(billitem.discount/100)
                billitem.totalPrice = (billitem.subTotalPrice + billitem.gstAmount) - billitem.discountAmount
                billitem.save()
            messages.success(request, 'Quotation has been created successfully!')
            return redirect('quotation-bill', quoteNo=billobj.pk)
        formset = QuotationItemFormset(request.GET or None, form_kwargs={'user':request.user})
        context ={
            'formset':formset,
            'customer':customerobj
        }
        return render(request, self.template_name, context)

class QuotationDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = QuotationBill
    template_name = 'pazar/delete quotation.html'
    login_url = '/account/login'
    fields = '__all__'
    success_message = 'Your Quotation has been deleted successfully!'
    success_url = reverse_lazy('quotation-list')

class QuotationView(LoginRequiredMixin, View):
    model = QuotationBill
    template_name = 'pazar/quotation.html'
    login_url = '/account/login'

    def get(self, request, quoteNo):
        context = {
            'quotes':QuotationBill.objects.get(pk=quoteNo),
            'items':QuotationItem.objects.filter(quoteNo=quoteNo)
        }
        return render(request, self.template_name, context)

    def post(self, request, quoteNo):
        context = {
            'quotes':QuotationBill.objects.get(pk=quoteNo),
            'items':QuotationItem.objects.filter(quoteNo=quoteNo)
        }
        return render(request, self.template_name, context)

@login_required(login_url='/account/login')
def OlxList(request):
    categories = Category.objects.order_by('name')[0:20]
    userItems = Sale.objects.filter(user=request.user).order_by('-date')
    items = Sale.objects.all().order_by('-date')
    olx = Sale.objects.all().order_by('-date')[0:16]
    n = len(olx)
    nSlides = n//4 + ceil((n/4)-(n//4))
    return render(request, 'pazar/olx list.html', {'olx':olx, 'items':items, 'userItems':userItems, 'categories':categories, 'nSlides':nSlides, 'range':range(1, nSlides)})

@login_required(login_url='/account/login')
def CategoryItem(request, slug):
    category = Category.objects.get(slug=slug)
    items = Sale.objects.filter(category=category).order_by('-date')
    return render(request, 'pazar/category list.html', {'items':items, 'category':category})

@login_required(login_url='/account/login')
def CategoryWiseItem(request):
    category = Category.objects.order_by('name')
    items = Sale.objects.all().order_by('-date')
    return render(request, 'pazar/all category item.html', {'categories':category, 'items':items})

@login_required(login_url='/account/login')
def ItemDetailView(request, pk, slug):
    item = get_object_or_404(Sale, id=pk, slug=slug)
    return render(request, 'pazar/item detail.html', {'item':item})

@login_required(login_url='/account/login')
def addOlxItem(request):
    form = SaleForm()
    if request.method == 'POST':
        form = SaleForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, 'Item to sell added successfully!')
            return redirect('items')
    else:
        form = SaleForm()
    return render(request, 'pazar/add item.html', {'form':form})

class EditItemView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = 'pazar/edit item.html'
    login_url = '/account/login'
    success_message = 'Your item has been edited successfully!'
    success_url = reverse_lazy('items')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class DeleteItemView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Sale
    template_name = 'pazar/delete item.html'
    login_url = '/account/login'
    fields = '__all__'
    success_message = 'Your item has been deleted successfully!'
    success_url = reverse_lazy('items')

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.user == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's items.")

@login_required(login_url='/account/login')
def employeeList(request):
    employee = Employee.objects.filter(user=request.user).order_by('-date')
    return render(request, 'pazar/employee list.html', {'employee':employee})

@login_required(login_url='/account/login')
def EmployeeProfile(request, pk):
    employee = Employee.objects.get(id=pk)
    return render(request, 'pazar/employee detail.html', {'employee':employee})

@login_required(login_url='/account/login')
def addEmployee(request):
    form = EmployeeForm(request.user)
    if request.method == 'POST':
        form = EmployeeForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            emp = form.save(commit=False)
            emp.user = request.user
            emp.save()
            messages.success(request, 'Employee added successfully!')
            return redirect('employee')
    else:
        form = EmployeeForm(request.user)
    return render(request, 'pazar/add employee.html', {'form':form})

class editEmployee(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'pazar/edit employee.html'
    login_url = '/account/login'
    success_message = 'Employee edited successfully!'
    success_url = reverse_lazy('employee')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class DeleteEmployeeView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Employee
    template_name = 'pazar/delete employee.html'
    login_url = '/account/login'
    fields = '__all__'
    success_message = 'Your employee has been deleted successfully!'
    success_url = reverse_lazy('employee')

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.user == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's employee.")

@login_required(login_url='/account/login')
def AttendanceList(request):
    attendance = Attendance.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'pazar/attendance list.html', {'attendance':attendance})

@login_required(login_url='/account/login')
def SelectAttendanceView(request):
    form = AttendanceForm(request.user)
    if request.method == 'get':
        form = AttendanceForm(request.user, request.GET or None)
        return render(request, 'pazar/employee take attendance.html', {'form':form})
    if request.method == 'POST':
        form = AttendanceForm(request.user, request.POST or None)
        if form.is_valid():
            shopId = request.POST.get('shop')
            date = request.POST.get('attendance_date')
            shop = get_object_or_404(Free_Listing, id=shopId)
            return redirect('create-attendance', shop.pk)
        return render(request, 'pazar/employee take attendance.html', {'form':form})
    return render(request, 'pazar/employee take attendance.html', {'form':form})

class AttendanceCreateView(LoginRequiredMixin, View):
    template_name = 'pazar/new attendance.html'
    login_url = '/account/login'
    
    def get(self, request, pk):
        formset = EmployeeAttendanceFormset(request.GET or None, form_kwargs={'user':request.user})
        shopObj = get_object_or_404(Free_Listing, pk=pk)
        employee = Employee.objects.filter(shop=shopObj)
        context = {
            'formset':formset,
            'employee': shopObj
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        formset = EmployeeAttendanceFormset(request.POST or None, form_kwargs={'user':request.user})
        shopObj = get_object_or_404(Free_Listing, pk=pk)
        if formset.is_valid():
            attendanceObj = Attendance(shop=shopObj)
            attendanceObj.user = request.user
            attendanceObj.save()
            for form in formset:
                employee = form.save(commit=False)
                employee.user = request.user
                employee.attendance = attendanceObj
                employee.save()
            messages.success(request, 'Attendance added successfully!')
            return redirect('attendance-list')
        formset = EmployeeAttendanceFormset(request.GET or None, form_kwargs={'user':request.user})
        context = {
            'formset':formset,
            'shop':shopObj
        }
        return render(request, self.template_name, context)

class AttendanceDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Attendance
    template_name = 'pazar/delete attendance.html'
    login_url = '/account/login'
    fields = '__all__'
    success_message = 'Your Attendance has been deleted successfully!'
    success_url = reverse_lazy('attendance-list')

    # override the delete function to check for a user match
    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.user == request.user:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Cannot delete other's attendance.")

def faq(request):
    faq = FAQ.objects.all()
    return render(request, 'pazar/faq.html', {'faq':faq})

def testimonials(request):
    testimonial = Testimonial.objects.all().order_by('-rate')[0:3]
    testimonials = Testimonial.objects.all().order_by('-date')
    return render(request, 'pazar/testimonials.html', {'testimonials':testimonials, 'testimonial':testimonial})

def plansPricing(request):
    return render(request, 'pazar/plans pricing.html')

def disclaimer(request):
    return render(request, 'pazar/disclaimer.html')

def complaints(request):
    return render(request, 'pazar/complaints.html')

def privacyPolicy(request):
    return render(request, 'pazar/privacy policy.html')

def refundPolicy(request):
    return render(request, 'pazar/refund policy.html')

def termsConditions(request):
    return render(request, 'pazar/terms conditions.html')

def help(request):
    return render(request, 'pazar/help.html')

def careers(request):
    return render(request, 'pazar/careers.html')

def feedback(request):
    feedbacks = Feedback.objects.all().order_by('-date')
    form = FeedbackForm()
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feedback sent successfully!')
    return render(request, 'pazar/feedback.html', {'form':form, 'feedbacks':feedbacks})

def customerCare(request):
    return render(request, 'pazar/customer care.html')

def dashboardSearch(request):
    query = request.GET['query']
    if len(query)>78 or len(query)<1:
        shops = Free_Listing.objects.none()
        customers = Customer.objects.none()
        products = Product.objects.none()
        employee = Employee.objects.none()
    else:
        shops = Free_Listing.objects.filter(Q(Business_Name__icontains=query) | Q(Business_Email__icontains=query) | Q(Business_Address__icontains=query) | Q(Business_Telephone__icontains=query) | Q(Business_WhatsApp__icontains=query) | Q(Business_Description__icontains=query)).distinct()
        customers = Customer.objects.filter(Q(name__icontains=query) | Q(phone__icontains=query) | Q(address__icontains=query) | Q(email__icontains=query) | Q(gstin__icontains=query)).distinct()
        products = Product.objects.filter(Q(name__icontains=query) | Q(desc__icontains=query) | Q(price__icontains=query) | Q(offer_price__icontains=query)).distinct()
        employee = Employee.objects.filter(Q(name__icontains=query) | Q(phone__icontains=query) | Q(email__icontains=query) | Q(address__icontains=query) | Q(role__icontains=query) | Q(aadhaar__icontains=query) | Q(pan__icontains=query) | Q(bank__icontains=query) | Q(ifsc__icontains=query) | Q(salary__icontains=query) | Q(description__icontains=query)).distinct()
    if shops.count() == 0 and customers.count() == 0 and products.count() == 0 and employee.count() == 0:
        messages.warning(request, 'No search results found. Please refine your query.')
    params = {
        'shops': shops,
        'customers': customers,
        'products': products,
        'employee': employee,
        'query': query,
    }
    return render(request, 'pazar/search results.html', params)

def listingTag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    common_tags = Free_Listing.tags.most_common()[:10]
    listings = Free_Listing.objects.filter(tags=tag).order_by('-Listed_at')
    context = {
        'tag':tag,
        'common_tags':common_tags,
        'listings':listings,
    }
    return render(request, 'pazar/listing tag.html', context)

def advertiseTag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    common_tags = Advertise_with_Us.tags.most_common()[:10]
    listings = Advertise_with_Us.objects.filter(tags=tag).order_by('-Added_at')
    context = {
        'tag':tag,
        'common_tags':common_tags,
        'listings':listings,
    }
    return render(request, 'pazar/advertise tag.html', context)

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

class GeneratePDF(View):
    def get(self, request, billNo, *args, **kwargs):
        template = get_template('pazar/sale invoice.html')
        context = {
            'bill':SaleBill.objects.get(pk=billNo),
            'items':SaleItem.objects.filter(billNo=billNo),
        }
        html = template.render(context)
        pdf = render_to_pdf('pazar/sale invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = 'Pazar Sale Invoice_%s.pdf' %(billNo)
            content = "inline; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

class PurchaseGeneratePDF(View):
    def get(self, request, billNo, *args, **kwargs):
        template = get_template('pazar/purchase invoice.html')
        context = {
            'bill':PurchaseBill.objects.get(pk=billNo),
            'items':PurchaseItem.objects.filter(billNo=billNo),
        }
        html = template.render(context)
        pdf = render_to_pdf('pazar/purchase invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = 'Pazar Purchase Invoice_%s.pdf' %(billNo)
            content = "inline; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

class QuoteGeneratePDF(View):
    def get(self, request, quoteNo, *args, **kwargs):
        template = get_template('pazar/quotation invoice.html')
        context = {
            'quotes':QuotationBill.objects.get(pk=quoteNo),
            'items':QuotationItem.objects.filter(quoteNo=quoteNo)
        }
        html = template.render(context)
        pdf = render_to_pdf('pazar/quotation invoice.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = 'Pazar Quotation_%s.pdf' %(quoteNo)
            content = "inline; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

def arun(request):
    return render(request, 'pazar/arun.html')

def mohak(request):
    return render(request, 'pazar/mohak.html')

def error_404_view(request, exception):
    return render(request, '404.html')

def error_500_view(request, exception=None):
    return render(request, '500.html')

def error_403_view(request, exception=None):
    return render(request, '403.html')

def error_400_view(request, exception=None):
    return render(request, '400.html')