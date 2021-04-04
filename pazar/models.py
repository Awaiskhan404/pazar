from re import T
from django.core import validators
from django.db import models
from django.utils.html import escape, mark_safe
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.urls import reverse
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from taggit.managers import TaggableManager
from django.utils.text import slugify
from mapbox_location_field.models import LocationField, AddressAutoHiddenField
from django.utils.safestring import mark_safe
from django.db.models import Avg, Count
from PazarSite.utils import unique_slug_generator
from multiselectfield import MultiSelectField

def listing_logo_directory_path(instance, filename):
    return 'user_{0}/listing/{1}/logo/{2}'.format(instance.Listed_by.id, instance.Business_Name, filename)

def listing_images_directory_path(instance, filename):
    return 'user_{0}/listing/{1}/images/{2}'.format(instance.Listed_by.id, instance.Business_Name, filename)

def listing_multiple_images_directory_path(instance, filename):
    return 'user_{0}/listing/{1}/multiple_images/{2}'.format(instance.listing.Listed_by.id, instance.listing.Business_Name, filename)

def advertise_logo_directory_path(instance, filename):
    return 'user_{0}/advertise/{1}/logo/{2}'.format(instance.Added_by.id, instance.Business_Name, filename)

def advertise_images_directory_path(instance, filename):
    return 'user_{0}/advertise/{1}/images/{2}'.format(instance.Added_by.id, instance.Business_Name, filename)

def advertise_multiple_images_directory_path(instance, filename):
    return 'user_{0}/advertise/{1}/multiple_images/{2}'.format(instance.advertise.Added_by.id, instance.advertise.Business_Name, filename)

def product_images_directory_path(instance, filename):
    return 'user_{0}/product/{1}/{2}'.format(instance.user.id, instance.name, filename)

def stock_images_directory_path(instance, filename):
    return 'user_{0}/stock/{1}/{2}'.format(instance.user.id, instance.name, filename)

def sale_images_directory_path(instance, filename):
    return 'user_{0}/sale/{1}/{2}'.format(instance.user.id, instance.name, filename)

def employee_images_directory_path(instance, filename):
    return 'user_{0}/employee/{1}/{2}'.format(instance.user.id, instance.shop.Business_Name, filename)

def skill_image_directory_path(instance, filename):
    return 'user_{0}/skills/{1}/{2}'.format(instance.user.id, instance.name, filename)

def skill_images_directory_path(instance, filename):
    return 'user_{0}/skills/{1}/{2}'.format(instance.skill.user.id, instance.skill.name, filename)

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True)
    color = models.CharField(max_length=7, default='#007bff')
    icon = models.ImageField(upload_to='categories/icons', validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], null=True, blank=True)
    image = models.ImageField(upload_to='categories/images', validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])],null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover = models.ImageField(upload_to='categories/cover', null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    SEO_Description = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True, help_text='Comma separated keywords here')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('id',)

    def __str__(self):
        return self.name

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.icon.url))
    admin_photo.short_description = "Icon"
    admin_photo.allow_tags = True

    def admin_image(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    admin_image.short_description = "Image"
    admin_image.allow_tags = True
    
    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' %(color, name)
        return mark_safe(html)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args,**kwargs)

class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='subcategories/images', validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover = models.ImageField(upload_to='subcategories/cover', null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    SEO_Description = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True, help_text='Comma separated keywords here')

    class Meta:
        verbose_name_plural = "Subcategories"
        ordering = ('id',)

    def __str__(self):
        return self.name

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    admin_photo.short_description = "Image"
    admin_photo.allow_tags = True

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Subcategory, self).save(*args,**kwargs)

class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    phone = models.CharField(
        validators=[RegexValidator("0?[5-9]{1}\d{9}$")],
        max_length=15,
        null=True,
        blank=True,
    )
    msg = models.TextField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Services(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Services'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Services, self).save(*args,**kwargs)

class Free_Listing(models.Model):
    Payments_Choices = (
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Credit Card / Debit Card', 'Credit Card / Debit Card'),
        ('NEFT/RTGS', 'NEFT/RTGS'),
        ('UPI', 'UPI'),
    )
    Listed_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    Business_Name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    Business_Category = models.ForeignKey(Category, on_delete=models.CASCADE)
    Business_Subcategory = models.ManyToManyField(Subcategory)
    Business_Services = models.ManyToManyField(Services)
    Business_Website = models.URLField(null=True, blank=True)
    Business_Facebook = models.URLField(null=True, blank=True)
    Business_Instagram = models.URLField(null=True, blank=True)
    Business_Twitter = models.URLField(null=True, blank=True)
    Business_Linkedin = models.URLField(null=True, blank=True)
    Business_Pinterest = models.URLField(null=True, blank=True)
    Business_Github = models.URLField(null=True, blank=True)
    Business_Email = models.EmailField(null=True, blank=True)
    # Business_Location = models.CharField(max_length=300)
    Business_Location = LocationField(null=True, blank=True)
    Address = AddressAutoHiddenField(null=True, blank=True)
    Business_Address = models.CharField(max_length=300)
    Business_Telephone = models.CharField(
        validators=[RegexValidator("0?[5-9]{1}\d{9}$")],
        max_length=15,
    )
    Business_WhatsApp = models.CharField(null=True, blank=True, max_length=15, validators=[RegexValidator("0?[5-9]{1}\d{9}$")])
    Business_Description = models.TextField()
    Business_Logo = models.ImageField(upload_to=listing_logo_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    Business_Images = models.ImageField(upload_to=listing_images_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], verbose_name='Business Images')
    Business_Established_Date = models.DateField()
    Listed_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(verbose_name='Business Keywords', help_text='Tag your business here')
    view = models.PositiveIntegerField(default=0)
    Mode_Of_Payments = MultiSelectField(choices=Payments_Choices)
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True, help_text='Comma separated keywords here')

    def __str__(self):
        return self.Business_Name

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.Business_Logo.url))
    admin_photo.short_description = "Logo"
    admin_photo.allow_tags = True

    def get_absolute_url(self):
        return reverse("Free Listing")

    class Meta:
        verbose_name = "Free Listing"
        verbose_name_plural = "Free Listings"
        ordering = ('-id',)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.Business_Name)
        super(Free_Listing, self).save(*args,**kwargs)

    def averagereview(self):
        reviews = Comment.objects.filter(listing=self).aggregate(average=Avg('rate'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews["average"])
        return avg

    def countreview(self):
        reviews = Comment.objects.filter(listing=self).aggregate(count=Count('id'))
        cnt = 0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt

class FreeListingImage(models.Model):
    listing = models.ForeignKey(Free_Listing, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=listing_multiple_images_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])

    def __str__(self):
        return self.listing.Business_Name

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    admin_photo.short_description = "Image"
    admin_photo.allow_tags = True

class Advertise_with_Us(models.Model):
    Payments_Choices = (
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Credit Card / Debit Card', 'Credit Card / Debit Card'),
        ('NEFT/RTGS', 'NEFT/RTGS'),
        ('UPI', 'UPI'),
    )
    Added_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    Business_Name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    Business_Category = models.ForeignKey(Category, on_delete=models.CASCADE)
    Business_Subcategory = models.ManyToManyField(Subcategory)
    Business_Services = models.ManyToManyField(Services)
    Business_Website = models.URLField(null=True, blank=True)
    Business_Facebook = models.URLField(null=True, blank=True)
    Business_Instagram = models.URLField(null=True, blank=True)
    Business_Twitter = models.URLField(null=True, blank=True)
    Business_Linkedin = models.URLField(null=True, blank=True)
    Business_Pinterest = models.URLField(null=True, blank=True)
    Business_Github = models.URLField(null=True, blank=True)
    Business_Email = models.EmailField(null=True, blank=True)
    # Business_Location = models.CharField(max_length=300)
    Business_Location = LocationField(null=True, blank=True)
    Address = AddressAutoHiddenField(null=True, blank=True)
    Business_Address = models.CharField(max_length=300)
    Business_Telephone = models.CharField(
        validators=[RegexValidator("0?[5-9]{1}\d{9}$")],
        max_length=15,
    )
    Business_WhatsApp = models.CharField(null=True, blank=True, max_length=15, validators=[RegexValidator("0?[5-9]{1}\d{9}$")])
    Business_Description = models.TextField()
    Business_Logo = models.ImageField(upload_to=advertise_logo_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    Business_Images = models.ImageField(upload_to=advertise_images_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], verbose_name='Business Images',null=True, blank=True)
    Business_Established_Date = models.DateField()
    Added_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(verbose_name='Business Keywords', help_text='Tag your business here')
    view = models.PositiveIntegerField(default=0)
    Mode_Of_Payments = MultiSelectField(choices=Payments_Choices)
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True, help_text='Comma separated keywords here')
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.Business_Name

    def get_absolute_url(self):
        return reverse("Advertise With Us")

    class Meta:
        verbose_name = "Advertise With Us"
        verbose_name_plural = "Advertise With Us"
        ordering = ('-id',)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.Business_Name)
        super(Advertise_with_Us, self).save(*args,**kwargs)

    def averagereview(self):
        reviews = AdvertiseComment.objects.filter(advertise=self).aggregate(average=Avg('rate'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews["average"])
        return avg

    def countreview(self):
        reviews = AdvertiseComment.objects.filter(advertise=self).aggregate(count=Count('id'))
        cnt = 0
        if reviews["count"] is not None:
            cnt = int(reviews["count"])
        return cnt

class AdvertiseWithUsImage(models.Model):
    advertise = models.ForeignKey(Advertise_with_Us, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=advertise_multiple_images_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])

    def __str__(self):
        return self.advertise.Business_Name
    
    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    admin_photo.short_description = "Image"
    admin_photo.allow_tags = True

import random
color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
class Skill(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name="Skill")
    excellence = models.IntegerField(('Excellence ( in %)'), validators=[MinValueValidator(0), MaxValueValidator(100)], default=0, help_text='Value between 0 & 100')
    images = models.ImageField(upload_to=skill_image_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], verbose_name='Showcase your Skills', null=True, blank=True)
    color = models.CharField(max_length=7, default=color)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_random_color(self):
        color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        return color

    def save(self, *args, **kwargs):
        self.color = color
        super(Skill, self).save(*args,**kwargs)

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.images.url))
    admin_photo.short_description = "Image"
    admin_photo.allow_tags = True

class SkillImages(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    images = models.ImageField(upload_to=skill_images_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])

    class Meta:
        verbose_name = 'Skill Image'
        verbose_name_plural = 'Skills Images'

    def __str__(self):
        return self.skill.name

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.images.url))
    admin_photo.short_description = "Image"
    admin_photo.allow_tags = True

class AdvertiseComment(models.Model):
    commented_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    advertise = models.ForeignKey(Advertise_with_Us, on_delete=models.CASCADE)
    comment = models.CharField(max_length=250, blank=True)
    rate = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    commented_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment

class Comment(models.Model):
    commented_by = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    listing = models.ForeignKey(Free_Listing, on_delete=models.CASCADE)
    comment = models.CharField(max_length=250, blank=True)
    rate = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    commented_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment

class Customer(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    shop = models.ForeignKey(Free_Listing, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    slug = models.SlugField(null=True, blank=True)
    phone = models.CharField(
        validators=[RegexValidator("0?[5-9]{1}\d{9}$")],
        max_length=15,
        null=True,
        blank=True
    )
    address = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    gstin = models.CharField(max_length=15, unique=True, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + ' of ' + self.shop.Business_Name

    # def save(self, *args, **kwargs):
    #     self.slug = slugify(self.name)
    #     super(Customer, self).save(*args,**kwargs)

def slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(slug_generator, sender=Customer)

class Product_Category(models.Model):
    name = models.CharField(max_length=50)
    icon = models.ImageField(upload_to='product categories/icons', validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=7, default='#007bff')
    slug = models.SlugField(unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product_Category, self).save(*args, **kwargs)

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' %(color, name)
        return mark_safe(html)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.icon.url))
    admin_photo.short_description = "Icon"
    admin_photo.allow_tags = True

class Product(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    shop = models.ForeignKey(Free_Listing, on_delete=models.CASCADE)
    category = models.ForeignKey(Product_Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to=product_images_directory_path, validators=[FileExtensionValidator(['png','jpg','jpeg'])])
    desc = models.TextField()
    price = models.FloatField()
    offer_price = models.FloatField(null=True, blank=True)
    brand = models.CharField(max_length=100)
    warranty = models.CharField(max_length=20)
    exp_date = models.DateField(null=True, blank=True)
    title = models.CharField(max_length=160, null=True, blank=True)
    description = models.TextField(null=True, blank=True,)
    keywords = models.TextField(null=True, blank=True, help_text='Comma separated keywords here')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name + ' of shop ' + self.shop.Business_Name

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    admin_photo.short_description = "Image"
    admin_photo.allow_tags = True

class Stock(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    shop = models.ForeignKey(Free_Listing, on_delete=models.CASCADE)
    supplier = models.ForeignKey('pazar.Supplier', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to=stock_images_directory_path, null=True, blank=True, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    hsn = models.CharField(max_length=200, verbose_name='HSN Number')
    price = models.FloatField()
    offer_price = models.FloatField(null=True, blank=True)
    brand = models.CharField(max_length=100)
    warranty = models.CharField(max_length=20, null=True, blank=True)
    exp_date = models.DateField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name + "(" + str(self.quantity) + " unit)" + " of shop " + self.shop.Business_Name
    
    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    admin_photo.short_description = "Stock Image"
    admin_photo.allow_tags = True

class Supplier(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    shop = models.ForeignKey(Free_Listing, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    phone = models.CharField(
        validators=[RegexValidator("0?[5-9]{1}\d{9}$")],
        max_length=15,
    )
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    gstin = models.CharField(max_length=15, unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class PurchaseBill(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    shop = models.ForeignKey(Free_Listing, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Bill No.- "  + str(self.pk)

    def get_items_list(self):
        return PurchaseItem.objects.filter(billNo=self)

    def gst(self):
        purchaseItems = PurchaseItem.objects.filter(billNo=self)
        gst = 0
        for item in purchaseItems:
            gst += item.gst
        return gst

    def gst_amount(self):
        purchaseItems = PurchaseItem.objects.filter(billNo=self)
        total = 0
        for item in purchaseItems:
            total += item.subTotalPrice*item.gst/100
        return total

    def discount(self):
        purchaseItems = PurchaseItem.objects.filter(billNo=self)
        discount = 0
        for item in purchaseItems:
            discount += item.discount
        return discount

    def discount_amount(self):
        purchaseItems = PurchaseItem.objects.filter(billNo=self)
        total = 0
        for item in purchaseItems:
            total += item.subTotalPrice*item.discount/100
        return total

    def get_subtotal_price(self):
        purchaseItems = PurchaseItem.objects.filter(billNo=self)
        total = 0
        for item in purchaseItems:
            total += item.subTotalPrice
        return total

    def get_total_price(self):
        purchaseItems = PurchaseItem.objects.filter(billNo=self)
        total = 0
        for item in purchaseItems:
            total += item.totalPrice
        return total
    
class PurchaseItem(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    billNo = models.ForeignKey(PurchaseBill, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    gst = models.FloatField(('GST (in %)'), default=0)
    gstAmount = models.FloatField(default=0)
    discount = models.FloatField(('Discount (in %)'), default=0)
    discountAmount = models.FloatField(default=0)
    quantity = models.FloatField(default=1)
    perPrice = models.FloatField(default=0)
    subTotalPrice = models.FloatField(default=0)
    totalPrice = models.FloatField(default=0)

    def __str__(self):
        return "Bill No.- " + str(self.billNo.pk) + ", Item = " + self.stock.name

class SaleBill(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    shop = models.ForeignKey(Free_Listing, on_delete=models.CASCADE, default="")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Bill No.- " + str(self.pk)

    def get_items_list(self):
        return SaleItem.objects.filter(billNo=self)

    def gst(self):
        saleItems = SaleItem.objects.filter(billNo=self)
        gst = 0
        for item in saleItems:
            gst += item.gst
        return gst

    def gst_amount(self):
        saleItems = SaleItem.objects.filter(billNo=self)
        total = 0
        for item in saleItems:
            total += item.subTotalPrice*item.gst/100
        return total

    def discount(self):
        saleItems = SaleItem.objects.filter(billNo=self)
        discount = 0
        for item in saleItems:
            discount += item.discount
        return discount

    def discount_amount(self):
        saleItems = SaleItem.objects.filter(billNo=self)
        total = 0
        for item in saleItems:
            total += item.subTotalPrice*item.discount/100
        return total

    def get_subtotal_price(self):
        saleItems = SaleItem.objects.filter(billNo=self)
        total = 0
        for item in saleItems:
            total += item.subTotalPrice
        return total

    def get_total_price(self):
        saleItems = SaleItem.objects.filter(billNo=self)
        total = 0
        for item in saleItems:
            total += item.totalPrice
        return total

class SaleItem(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    billNo = models.ForeignKey(SaleBill, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    gst = models.FloatField(('GST (in %)'), default=0)
    gstAmount = models.FloatField(default=0)
    discount = models.FloatField(('Discount (in %)'), default=0)
    discountAmount = models.FloatField(default=0)
    quantity = models.FloatField(default=1)
    perPrice = models.FloatField(default=0)
    subTotalPrice = models.FloatField(default=0)
    totalPrice = models.FloatField(default=0)

    def __str__(self):
        return "Bill No.- " + str(self.billNo.pk) + ", Item = " + self.stock.name

class QuotationBill(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    shop = models.ForeignKey(Free_Listing, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return 'Quotation for shop ' + self.shop.Business_Name + ' made by ' + self.user.username + ' for customer ' + self.customer.name

    def get_items_list(self):
        return QuotationItem.objects.filter(quoteNo=self)

    def gst(self):
        quoteItems = QuotationItem.objects.filter(quoteNo=self)
        gst = 0
        for item in quoteItems:
            gst += item.gst
        return gst

    def gst_amount(self):
        quoteItems = QuotationItem.objects.filter(quoteNo=self)
        total = 0
        for item in quoteItems:
            total += item.subTotalPrice*item.gst/100
        return total

    def discount(self):
        quoteItems = QuotationItem.objects.filter(quoteNo=self)
        discount = 0
        for item in quoteItems:
            discount += item.discount
        return discount

    def discount_amount(self):
        quoteItems = QuotationItem.objects.filter(quoteNo=self)
        total = 0
        for item in quoteItems:
            total += item.subTotalPrice*item.discount/100
        return total 

    def get_subtotal_price(self):
        quoteItems = QuotationItem.objects.filter(quoteNo=self)
        total = 0
        for item in quoteItems:
            total += item.subTotalPrice
        return total

    def get_total_price(self):
        quoteItems = QuotationItem.objects.filter(quoteNo=self)
        total = 0
        for item in quoteItems:
            total += (item.subTotalPrice+item.subTotalPrice*item.gst/100)-item.subTotalPrice*item.discount/100
        return total
    
class QuotationItem(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    quoteNo = models.ForeignKey(QuotationBill, on_delete=models.CASCADE)
    product = models.ForeignKey(Stock, on_delete=models.CASCADE)
    gst = models.FloatField(('GST (in %)'), default=0)
    gstAmount = models.FloatField(default=0)
    discount = models.FloatField(('Discount (in %)'), default=0)
    discountAmount = models.FloatField(default=0)
    quantity = models.FloatField(default=1)
    perPrice = models.FloatField(default=0)
    subTotalPrice = models.FloatField(default=0)
    totalPrice = models.FloatField(default=0)

    def __str__(self):
        return 'Quotation No.- ' + str(self.quoteNo.pk) +' for item ' + self.product.name

class Sale(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Product_Category, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=sale_images_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    SEO_Description = models.TextField(null=True, blank=True)
    keywords = models.TextField(null=True, blank=True, help_text='Comma separated keywords here')

    def __str__(self):
        return self.name

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    admin_photo.short_description = "Item Image"
    admin_photo.allow_tags = True

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Sale, self).save(*args,**kwargs)

alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')
numeric = RegexValidator(r'^[0-9+]', 'Only digit characters.')

class Employee(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    shop = models.ForeignKey(Free_Listing, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    phone = models.CharField(
        validators=[RegexValidator("0?[5-9]{1}\d{9}$")],
        max_length=15,
    )
    email = models.EmailField(max_length=254)
    address = models.CharField(max_length=300)
    gender = models.CharField(max_length=6, choices=(("Male", "Male"), ("Female", "Female")), default='Male')
    status = models.CharField(max_length=9, choices=(("Married", "Married"), ("Unmarried", "Unmarried")), default='Unmarried')
    age = models.IntegerField(default=18, validators=[MinValueValidator(18)])
    birthday = models.DateField()
    role = models.CharField(max_length=50)
    aadhaar = models.CharField(max_length=12, validators=[numeric])
    pan = models.CharField(max_length=10,validators=[alphanumeric], null=True, blank=True)
    bankName = models.CharField(max_length=200, null=True, blank=True)
    bank = models.CharField(max_length=20,validators=[alphanumeric], null=True, blank=True)
    ifsc = models.CharField(max_length=11,validators=[alphanumeric], null=True, blank=True)
    upi = models.CharField(max_length=20, null=True, blank=True)
    salary = models.IntegerField()
    description = models.TextField()
    photo = models.ImageField(upload_to=employee_images_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Employee " + self.name + " of shop " + self.shop.Business_Name

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.photo.url))
    admin_photo.short_description = "Employee Image"
    admin_photo.allow_tags = True

class Attendance(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    shop = models.ForeignKey(Free_Listing, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return self.shop.Business_Name + " Employee Attendance taken at " + self.created_at.strftime('%d-%m-%Y, %H:%M')

    def get_employee_list(self):
        return AttendanceReport.objects.filter(attendance=self)

class AttendanceReport(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    attendance_date = models.DateField()
    status = models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return self.employee.name

class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()

    def __str__(self):
        return self.question[0:50]

class Feedback(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(
        validators=[RegexValidator("0?[5-9]{1}\d{9}$")],
        max_length=15,
        null=True,
        blank=True,
    )
    email = models.EmailField(max_length=254, null=True, blank=True,)
    message = models.TextField()
    rate = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Testimonial(models.Model):
    name = models.CharField(max_length=50)
    role = models.CharField(max_length=100)
    desc = models.TextField()
    image = models.ImageField(upload_to='testimonial')
    rate = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    admin_photo.short_description = "Image"
    admin_photo.allow_tags = True