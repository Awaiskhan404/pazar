from django.contrib import admin
from .models import CustomUser, ShopOwner, Consumer, Profile
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.options import ModelAdmin

# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('username','email','first_name','last_name','is_shop_owner','is_user','is_staff')
    list_filter = ('is_staff','is_shop_owner', 'is_user','is_superuser')
    fieldsets = (
        (None, {'fields':('email','password')}),
        ('Personal Info', {'fields':('username','first_name','last_name')}),
        ('Permissions', {'fields':('is_superuser','is_staff','is_active','signup_confirmation','is_shop_owner','is_user')})
    )
    add_fieldsets = (
        (None, {
            'classes':('wide',),
            'fields':('email','username','password1','password2','is_staff')
        }),
    )
    search_fields = ('email','username',)
    ordering = ('email',)

class ProfileAdmin(ModelAdmin):
    list_display = ['name', 'phone_no', 'gender', 'admin_photo', 'updated_at']
    search_fields = ['name', 'phone_no']
    list_filter = ['gender', 'age']
    fieldsets = (
        (None, {'fields':('user','slug',)}),
        ('Personal Info', {'fields':('name', 'gender', 'age', 'birthday', 'bio', 'description', 'address', 'phone_no', 'pic', 'favourites',)}),
        ('Social Media', {'fields':('website', 'facebook', 'instagram', 'twitter', 'github', 'linkedin', 'youtube', 'pinterest',)})
    )

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(ShopOwner)
admin.site.register(Consumer)
admin.site.register(Profile, ProfileAdmin)

from .models import FollowUser
class FollowUserAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'cr_date',]
admin.site.register(FollowUser, FollowUserAdmin)

from .models import Post
class PostAdmin(ModelAdmin):
    list_display = ['msg', 'admin_photo', 'uploaded_by', 'cr_date']
    search_fields = ['msg', 'uploaded_by',]
    list_filter = ['uploaded_by',]
admin.site.register(Post, PostAdmin)

from .models import PostComment
class PostCommentAdmin(ModelAdmin):
    list_display = ['post', 'msg', 'commented_by', 'cr_date',]
    search_fields = ['msg', 'post', 'commented_by',]
    list_filter = ['post', 'commented_by',]
admin.site.register(PostComment, PostCommentAdmin)

from .models import PostLike
class PostLikeAdmin(ModelAdmin):
    list_display = ['post', 'liked_by', 'cr_date',]
    search_fields = ['post', 'liked_by',]
    list_filter = ['post', 'liked_by']
admin.site.register(PostLike, PostLikeAdmin)

from .models import Notification
admin.site.register(Notification)

from .models import PostFileContent
admin.site.register(PostFileContent)