from django import forms
from django.db import models
from django.db.models import fields
from .models import AdvertiseComment, Free_Listing, Advertise_with_Us, Subcategory, Comment, Customer, Skill, Product, Supplier, Stock, SaleBill, SaleItem, PurchaseBill, PurchaseItem, QuotationBill, QuotationItem, Sale, Employee, Attendance, AttendanceReport, Feedback
from django.forms import ModelForm, formset_factory, BaseFormSet, widgets
from multiselectfield import MultiSelectFormField

class DateInput(forms.DateInput):
    input_type = 'date'

class Free_ListingForm(forms.ModelForm):
    Business_Images = forms.FileField(required=True, widget=forms.FileInput(attrs={'class':'form-control','multiple':'true'}))

    class Meta:
        model = Free_Listing
        fields = ['Business_Name', 'Business_Category', 'Business_Subcategory', 'Business_Services', 'Business_Telephone', 'Business_WhatsApp', 'Business_Address', 'Business_Location', 'Business_Email', 'Business_Website', 'Business_Facebook', 'Business_Instagram', 'Business_Twitter', 'Business_Linkedin', 'Business_Pinterest', 'Business_Github', 'Business_Description','tags', 'Business_Logo', 'Business_Images', 'Business_Established_Date', 'Mode_Of_Payments',]
        widgets = {
            'Business_Name' : forms.TextInput(attrs={'placeholder':'Enter Your Business Name Here...'}),
            'Business_Location': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Enter Your Business Address Here...'}),
            'Business_Category' : forms.Select(attrs={'class':'chosen-select'}),
            'Business_Subcategory' : forms.SelectMultiple(attrs={'id':'my-select',}),
            'Business_Services' : forms.SelectMultiple(attrs={'id':'services-select'}),
            "Business_Description" : forms.Textarea(attrs={'placeholder':'Describe Your Business Here...'}),
            "Business_Established_Date" : DateInput(),
            'Business_Facebook' : forms.URLInput(attrs={'placeholder':'Enter Your Facebook Page Here...'}),
            'Business_Instagram' : forms.URLInput(attrs={'placeholder':'Enter Your Instagram Page Here...'}),
            'Business_Twitter' : forms.URLInput(attrs={'placeholder':'Enter Your Twitter Handle Here...'}),
            'Business_Linkedin' : forms.URLInput(attrs={'placeholder':'Enter Your Linkedin Page Here..'}),
            'Business_Pinterest' : forms.URLInput(attrs={'placeholder':'Enter Your Pinterest Board Here...'}),
            'Business_Github' : forms.URLInput(attrs={'placeholder':'Enter Your Github Profile Here...'}),
            'Business_Images' : forms.ClearableFileInput(attrs={'class':'form-control'}),
            'Business_Logo' : forms.FileInput(attrs={'class':'form-control'}),
            'Mode_Of_Payments' : forms.CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):
        super(Free_ListingForm, self).__init__(*args, **kwargs)
        self.fields['Business_Subcategory'].queryset = Subcategory.objects.none()
        if 'Business_Category' in self.data:
            try:
                Business_Category_id = int(self.data.get('Business_Category'))
                self.fields['Business_Subcategory'].queryset = Subcategory.objects.filter(category_id=Business_Category_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['Business_Subcategory'].queryset = self.instance.Business_Category.subcategory_set.order_by('name')
            
        self.fields['Business_Website'].widget.attrs['placeholder'] = 'Enter Your Business Website Here...'
        self.fields['Business_Email'].widget.attrs['placeholder'] = 'Enter Your Business Email Here...'
        self.fields['Business_Telephone'].widget.attrs['placeholder'] = 'Enter Your Phone Number Here...'
        self.fields['Business_WhatsApp'].widget.attrs['placeholder'] = 'Enter Your WhatsApp Number Here...'
        self.fields['Business_Address'].widget.attrs['placeholder'] = 'Enter Your Business Address Here...'
        self.fields['Business_Website'].required = False
        self.fields['Business_Facebook'].required = False
        self.fields['Business_Instagram'].required = False
        self.fields['Business_Twitter'].required = False
        self.fields['Business_Linkedin'].required = False
        self.fields['Business_Pinterest'].required = False
        self.fields['Business_Github'].required = False
        self.fields['Business_Email'].required = False
        self.fields['Business_Images'].widget.attrs['label'] = 'Business Images'
        self.fields['tags'].widget.attrs['data-role'] = 'tagsinput'
    def save(self, user=None):
        listing = super(Free_ListingForm, self).save(commit=False)
        if user:
            listing.Listed_by = user
        listing.save()
        return listing

class Advertise_With_UsForm(forms.ModelForm):
    Business_Images = forms.FileField(required=True, widget=forms.FileInput(attrs={'class':'form-control','multiple':'true'}))

    class Meta:
        model = Advertise_with_Us
        fields = ['Business_Name', 'Business_Category', 'Business_Subcategory', 'Business_Services', 'Business_Telephone', 'Business_WhatsApp', 'Business_Address', 'Business_Location', 'Business_Email', 'Business_Website', 'Business_Facebook', 'Business_Instagram', 'Business_Twitter', 'Business_Linkedin', 'Business_Pinterest', 'Business_Github', 'Business_Description', 'tags','Business_Logo', 'Business_Images', 'Business_Established_Date', 'Mode_Of_Payments',]
        widgets = {
            'Business_Name' : forms.TextInput(attrs={'placeholder':'Enter Your Business Name Here...'}),
            'Business_Location': forms.TextInput(attrs={'placeholder':'Enter Your Business Address Here...'}),
            'Business_Category' : forms.Select(attrs={'class':'chosen-select'}),
            'Business_Subcategory' : forms.SelectMultiple(attrs={'id': 'my-select',}),
            'Business_Services' : forms.SelectMultiple(attrs={'id':'service-select'}),
            'Business_Website' : forms.URLInput(attrs={'placeholder':'Enter Your Business Website Here...'}),
            'Business_Facebook' : forms.URLInput(attrs={'placeholder':'Enter Your Facebook Page Here...'}),
            'Business_Instagram' : forms.URLInput(attrs={'placeholder':'Enter Your Instagram Page Here...'}),
            'Business_Twitter' : forms.URLInput(attrs={'placeholder':'Enter Your Twitter Handle Here...'}),
            'Business_Linkedin' : forms.URLInput(attrs={'placeholder':'Enter Your Linkedin Page Here...'}),
            'Business_Pinterest' : forms.URLInput(attrs={'placeholder':'Enter Your Pinterest Board Here...'}),
            'Business_Github' : forms.URLInput(attrs={'placeholder':'Enter Your Github Profile Here...'}),
            'Business_Email' : forms.EmailInput(attrs={'placeholder':'Enter Your Business Email Here...'}),
            'Business_Description' : forms.Textarea(attrs={'placeholder':'Describe Your Business Here...'}),
            'Business_Images' : forms.ClearableFileInput(attrs={'class':'form-control'}),
            'Business_Logo' : forms.FileInput(attrs={'class':'form-control'}),
            'Business_Established_Date' : DateInput(attrs={'class':'form-control'}),
            'Mode_Of_Payments' : forms.CheckboxSelectMultiple
        }
    
    def __init__(self, *args, **kwargs):
        super(Advertise_With_UsForm, self).__init__(*args, **kwargs)
        self.fields['Business_Subcategory'].queryset = Subcategory.objects.none()
        if 'Business_Category' in self.data:
            try:
                Business_Category_id = int(self.data.get('Business_Category'))
                self.fields['Business_Subcategory'].queryset = Subcategory.objects.filter(category_id=Business_Category_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['Business_Subcategory'].queryset = self.instance.Business_Category.subcategory_set.order_by('name')

        self.fields['Business_Telephone'].widget.attrs['placeholder'] = 'Enter Your Phone Number Here...'
        self.fields['Business_WhatsApp'].widget.attrs['placeholder'] = 'Enter Your WhatsApp Number Here...'
        self.fields['Business_Address'].widget.attrs['placeholder'] = 'Enter Your Business Address Here...'
        self.fields['Business_Website'].required = False
        self.fields['Business_Facebook'].required = False
        self.fields['Business_Instagram'].required = False
        self.fields['Business_Twitter'].required = False
        self.fields['Business_Linkedin'].required = False
        self.fields['Business_Pinterest'].required = False
        self.fields['Business_Github'].required = False
        self.fields['Business_Email'].required = False
        self.fields['tags'].widget.attrs['data-role'] = 'tagsinput'

    def save(self, user=None):
        listing = super(Advertise_With_UsForm, self).save(commit=False)
        if user:
            listing.Added_by = user
        listing.save()
        return listing

class AdvertiseCommentForm(ModelForm):
    class Meta:
        model = AdvertiseComment
        fields = ['comment', 'rate']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment', 'rate']

class CustomerForm(forms.ModelForm):
    name = forms.TextInput(attrs={'class':'form-control'})
    shop = forms.Select(attrs={'class':'form-control'})
    phone = forms.TextInput(attrs={'class':'form-control'})
    address = forms.TextInput(attrs={'class':'form-control'})
    class Meta:
        model = Customer
        fields = ['name', 'shop', 'phone', 'address', 'email', 'gstin',]

    def __init__(self, user, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['shop'].queryset = Free_Listing.objects.filter(Listed_by=user)
        self.fields['gstin'].widget.attrs.update({'class':'textinput form-control', 'maxlength':'15', 'pattern':'[A-Z0-9]{15}', 'title':'GSTIN Format Required'})

class SkillForm(forms.ModelForm):
    images = forms.FileField(required=True, widget=forms.FileInput(attrs={'class':'form-control', 'multiple':'true'}))
    class Meta:
        model = Skill
        fields = ['name', 'excellence', 'images',]

    def __init__(self, *args, **kwargs):
        super(SkillForm, self).__init__(*args, **kwargs)
        self.fields['images'].label = 'Showcase your Skills'

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'shop', 'image', 'desc', 'price', 'offer_price', 'brand', 'warranty', 'exp_date',]
        widgets = {
            'exp_date' : DateInput(attrs={'class':'form-control'}),
        }

    def __init__(self, user, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['shop'].queryset = Free_Listing.objects.filter(Listed_by=user)

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['name', 'shop', 'supplier', 'quantity', 'image', 'hsn', 'price', 'offer_price', 'brand', 'warranty', 'exp_date',]
        widgets = {
            'exp_date': DateInput(attrs={'class':'form-control'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shop'].queryset = Free_Listing.objects.filter(Listed_by=user)
        self.fields['supplier'].queryset = Supplier.objects.filter(user=user)
        self.fields['name'].widget.attrs.update({'class':'form-control'})
        self.fields['quantity'].widget.attrs.update({'class':'form-control', 'min':'0'})
        self.fields['image'].required = False

class SelectSupplierForm(forms.ModelForm):
    class Meta:
        model = PurchaseBill
        fields = ['shop','supplier',]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(user=user)
        self.fields['shop'].queryset = Free_Listing.objects.filter(Listed_by=user)

class SelectCustomerForm(forms.ModelForm):
    class Meta:
        model = SaleBill
        fields = ['shop', 'customer',]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(user=user)
        self.fields['shop'].queryset = Free_Listing.objects.filter(Listed_by=user)
        self.fields['customer'].widget.attrs.update({'class':'form-control'})

class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseItem
        fields = ['stock', 'quantity', 'perPrice', 'gst', 'discount',]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Stock.objects.filter(user=user)
        self.fields['stock'].widget.attrs.update({'class':'text-input form-control setprice stock', 'required':'True'})
        self.fields['quantity'].widget.attrs.update({'class':'text-input form-control setprice quantity', 'min':'0','required':'True'})
        self.fields['perPrice'].widget.attrs.update({'class':'text-input form-control setprice price', 'min':'0', 'required':'True'})
        self.fields['gst'].widget.attrs.update({'class':'form-control'})
        self.fields['discount'].widget.attrs.update({'class':'form-control'})
PurchaseItemFormset = formset_factory(PurchaseItemForm, extra=1)

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'shop', 'phone', 'address', 'email', 'gstin']
        widgets = {
            'address':forms.Textarea(attrs={'class':'form-control', 'rows':'4'})
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shop'].queryset = Free_Listing.objects.filter(Listed_by=user)
        self.fields['name'].widget.attrs.update({'class':'textinput form-control'})
        self.fields['phone'].widget.attrs.update({'class':'textinput form-control'})
        self.fields['email'].widget.attrs.update({'class':'textinput form-control'})
        self.fields['gstin'].widget.attrs.update({'class':'textinput form-control', 'maxlength':'15', 'pattern':'[A-Z0-9]{15}', 'title':'GSTIN Format Required'})

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['stock', 'quantity', 'perPrice', 'gst', 'discount',]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stock'].queryset = Stock.objects.filter(user=user)
        self.fields['stock'].widget.attrs.update({'class':'textinput form-control setprice stock', 'required':'True'})
        self.fields['quantity'].widget.attrs.update({'class':'textinput form-control setprice quantity', 'min':'0', 'required':'True'})
        self.fields['perPrice'].widget.attrs.update({'class':'textinput form-control setprice price', 'min':'0', 'required':'True'})
        self.fields['gst'].widget.attrs.update({'class':'form-control'})
        self.fields['discount'].widget.attrs.update({'class':'form-control'})

SaleItemFormset = formset_factory(SaleItemForm, extra=1)

class SelectQuotationCustomerForm(forms.ModelForm):
    class Meta:
        model = QuotationBill
        fields = ['shop', 'customer']
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shop'].queryset = Free_Listing.objects.filter(Listed_by=user)
        self.fields['customer'].queryset = Customer.objects.filter(user=user)
        self.fields['shop'].widget.attrs.update({'class':'form-control'})
        self.fields['customer'].widget.attrs.update({'class':'form-control'})

class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ['product', 'quantity', 'perPrice', 'gst', 'discount',]

    def __init__(self,user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Stock.objects.filter(user=user)
        self.fields['product'].widget.attrs.update({'class':'textinput form-control setprice stock', 'required':'True'})
        self.fields['quantity'].widget.attrs.update({'class':'textinput form-control setprice quantity', 'min':'0', 'required':'True'})
        self.fields['perPrice'].widget.attrs.update({'class':'textinput form-control setprice price', 'min':'0', 'required':'True'})
        self.fields['gst'].widget.attrs.update({'class':'textinput form-control', 'min':'0', 'required':'False'})
        self.fields['discount'].widget.attrs.update({'class':'textinput form-control', 'min':'0', 'required':'False'})

QuotationItemFormset = formset_factory(QuotationItemForm, extra=1)

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['name', 'description', 'category', 'quantity', 'price', 'image',]
        widgets = {
            'image':forms.FileInput(attrs={'class':'form-control'})
        }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['shop', 'name', 'phone', 'email', 'address', 'gender', 'status', 'age', 'birthday', 'role', 'aadhaar', 'pan', 'bankName', 'bank', 'ifsc', 'upi', 'salary', 'description', 'photo',]
        widgets = {
            'birthday' : DateInput(attrs={'class':'form-control'}),
        }

    def __init__(self, user, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.fields['shop'].queryset = Free_Listing.objects.filter(Listed_by=user)
        self.fields['description'].widget.attrs['placeholder'] = 'Describe Employee Skills and Educations...'
        self.fields['bankName'].label = "Bank Name"
        self.fields['bank'].label = "Bank Account Number"

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['shop',]

    def __init__(self, user, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.fields['shop'].queryset = Free_Listing.objects.filter(Listed_by=user)

class AttendanceReportForm(forms.ModelForm):
    class Meta:
        model = AttendanceReport
        fields = ['employee', 'status', 'attendance_date',]
        widgets = {
            'status':forms.CheckboxInput(attrs={'class':'form-check'}),
            'attendance_date': DateInput(attrs={'class':'form-control'}),
            }

    def __init__(self,user,*args, **kwargs):
        super(AttendanceReportForm, self).__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(user=user)
        self.fields['employee'].widget.attrs.update({'class':'form-control'})
        self.fields['status'].widget.attrs.update({'class':'textinput form-check'})

EmployeeAttendanceFormset = formset_factory(AttendanceReportForm, extra=1)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'phone', 'email', 'message', 'rate',]

    def __init__(self,*args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class':'form-control'})
        self.fields['phone'].widget.attrs.update({'class':'form-control'})
        self.fields['email'].widget.attrs.update({'class':'form-control'})
        self.fields['message'].widget.attrs.update({'class':'form-control'})