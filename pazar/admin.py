from django.contrib import admin
from django.contrib.admin.sites import site
from .models import Category, Subcategory, Contact, Free_Listing, SaleItem, SaleBill ,PurchaseBill, PurchaseItem
from django.contrib.admin.options import ModelAdmin
from mapbox_location_field.admin import MapAdmin

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'admin_photo', 'admin_image',]
    search_fields = ['name',]
admin.site.register(Category, CategoryAdmin)

class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'admin_photo',]
    search_fields = ['name',]
    list_filter = ['category',]
admin.site.register(Subcategory, SubcategoryAdmin)

class ContactAdmin(ModelAdmin):
    list_display = ['name', 'email', 'phone', 'msg', 'date']
    search_fields = ['name', 'email', 'phone']
admin.site.register(Contact, ContactAdmin)

from .models import FreeListingImage
class FreeListingImageAdmin(admin.StackedInline):
    model = FreeListingImage

class FreeListingImageAdmin(admin.ModelAdmin):
    list_display = ('listing', 'admin_photo')
admin.site.register(FreeListingImage, FreeListingImageAdmin)

class Free_ListingAdmin(admin.ModelAdmin):
    list_display = ['id', 'Business_Name', 'admin_photo', "Business_Category", "Business_Telephone", 'Business_Location', "Listed_at"]
    search_fields = ['Business_Name', 'Business_Category', 'Business_Subcategory']
    list_filter = ['Business_Name', 'Business_Category','Business_Subcategory']
    tag_fields = ["Business_Subcategory"]
    inlines = [FreeListingImageAdmin]

admin.site.register(Free_Listing, MapAdmin)

from .models import AdvertiseWithUsImage
class AdvertiseWithUsImageAdmin(admin.StackedInline):
    model = AdvertiseWithUsImage

class AdvertiseWithUsImageAdmin(admin.ModelAdmin):
    list_display = ('advertise', 'admin_photo')
admin.site.register(AdvertiseWithUsImage, AdvertiseWithUsImageAdmin)

from .models import Advertise_with_Us
class Advertise_with_UsAdmin(admin.ModelAdmin):
    list_display = ['id', 'Business_Name', "Business_Category", "Business_Telephone", "Added_at"]
    search_fields = ['Business_Name', 'Business_Category', 'Business_Subcategory']
    list_filter = ['Business_Name', 'Business_Category','Business_Subcategory']
    tag_fields = ["Business_Subcategory"]
    inlines = [AdvertiseWithUsImageAdmin]

admin.site.register(Advertise_with_Us, MapAdmin)

from .models import SkillImages
class SkillImagesAdmin(admin.StackedInline):
    model = SkillImages
admin.site.register(SkillImages)

from .models import Skill
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'excellence', 'user', 'admin_photo',]
    search_fields = ['name', 'excellence', 'user',]
    list_filter = ['user',]
    inlines = [SkillImagesAdmin]
admin.site.register(Skill, SkillAdmin)

from .models import Comment
class CommentAdmin(admin.ModelAdmin):
    list_display = ['comment', 'rate',]
    list_filter = ['rate',]
admin.site.register(Comment, CommentAdmin)

from .models import AdvertiseComment
class AdvertiseCommentAdmin(admin.ModelAdmin):
    list_display = ['comment', 'rate',]
    list_filter = ['rate',]
admin.site.register(AdvertiseComment, AdvertiseCommentAdmin)

from .models import Customer
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop', 'phone', 'address',]
    search_fields = ['name', 'shop', 'phone', 'address',]
    list_filter = ['shop',]
admin.site.register(Customer, CustomerAdmin)

from .models import Product_Category
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin_photo',)
    search_fields = ('name',)
admin.site.register(Product_Category, ProductCategoryAdmin)

from .models import Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'shop', 'admin_photo', 'price', 'offer_price',]
    search_fields = ['name', 'shop', 'price',]
    list_filter = ['shop', 'user']
admin.site.register(Product, ProductAdmin)

from .models import Stock
class StockAdmin(admin.ModelAdmin):
    list_display = ['name', 'admin_photo', 'shop', 'user', 'date',]
    search_fields = ['name', 'user', 'shop', ]
    list_filter = ['shop', 'user',]
admin.site.register(Stock, StockAdmin)

from .models import Supplier
admin.site.register(Supplier)

from .models import PurchaseBill
admin.site.register(PurchaseBill)

from .models import PurchaseItem
admin.site.register(PurchaseItem)

from .models import SaleBill
admin.site.register(SaleBill)

from .models import SaleItem
admin.site.register(SaleItem)

from .models import QuotationBill
admin.site.register(QuotationBill)

from .models import QuotationItem
admin.site.register(QuotationItem)

from .models import Sale
class SaleAdmin(ModelAdmin):
    list_display = ['name', 'admin_photo', 'category', 'user', 'date',]
    search_fields = ['name', 'user', 'category', 'description',]
    list_filter = ['category', 'user',]
admin.site.register(Sale, SaleAdmin)

from .models import Employee
class EmployeeAdmin(ModelAdmin):
    list_display = ['name', 'admin_photo', 'shop', 'role', 'salary', 'date',]
    search_fields = ['user', 'shop', 'name', 'phone', 'address', 'aadhaar', 'pan',]
    list_filter = ['user', 'shop',]
admin.site.register(Employee, EmployeeAdmin)

from .models import Attendance
admin.site.register(Attendance)

from.models import AttendanceReport
admin.site.register(AttendanceReport)

from .models import FAQ
admin.site.register(FAQ)

from .models import Feedback
admin.site.register(Feedback)

from .models import Testimonial
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'rate', 'admin_photo', 'date')
    search_fields = ('name', 'role', 'rate',)
    list_filter = ('rate',)
admin.site.register(Testimonial, TestimonialAdmin)

from .models import Services
admin.site.register(Services)