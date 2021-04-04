from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator, MinValueValidator, FileExtensionValidator
from pazar.models import Category
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings
import os
from taggit.managers import TaggableManager
from django.db.models.signals import post_save, post_delete

USERNAME_REGEX = '^[a-zA-Z0-9.+-]*$'

def user_profile_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    profile_pic_name = 'user_{0}/profile.jpg'.format(instance.user.id)
    full_path = os.path.join(settings.MEDIA_ROOT, profile_pic_name)

    if os.path.exists(full_path):
    	os.remove(full_path)

    return profile_pic_name

def post_image_directory_path(instance, filename):
    return 'user_{0}/post/{1}/{2}'.format(instance.uploaded_by.id, instance.msg, filename)

def post_images_directory_path(instance, filename):
    return 'user_{0}/post/{1}/{2}'.format(instance.post.uploaded_by.id, instance.post.msg, filename)

def post_multiple_images_directory_path(instance, filename):
    return 'user_{0}/post/{1}multiple_images/{2}'.format(instance.user.id, instance.post.msg, filename)

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError(_('The email must be set.'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email,password,**extra_fields)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, validators=[RegexValidator(regex=USERNAME_REGEX)], unique=True, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    email = models.EmailField(_('E-Mail'), unique=True)
    is_shop_owner = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    signup_confirmation = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.username

    def get_short_name(self):
        return self.username

class ShopOwner(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Consumer(models.Model):
    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE)
    interests = models.ManyToManyField(Category, related_name='Interested_Category')

    def __str__(self):
        return self.user.username
    
class Profile(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, null=True, blank=True)
    age = models.IntegerField(default=18, validators=[MinValueValidator(18)])
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20, default="Male", choices=(("Male", "Male"), ("Female", "Female"))
    )
    bio = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    address = models.CharField(max_length=250,null=True, blank=True)
    phone_no = models.CharField(
        validators=[RegexValidator("0?[5-9]{1}\d{9}$")],
        max_length=15,
        null=True,
        blank=True,
    )
    whatsapp = models.CharField(
        validators=[RegexValidator("0?[5-9]{1}\d{9}$")],
        max_length=15,
        null=True,
        blank=True,
    )
    website = models.URLField(null=True, blank=True, default="")
    facebook = models.URLField(null=True, blank=True, default="")
    instagram = models.URLField(null=True, blank=True, default="")
    twitter = models.URLField(null=True, blank=True, default="")
    github = models.URLField(null=True, blank=True, default="")
    linkedin = models.URLField(null=True, blank=True, default="")
    youtube = models.URLField(null=True, blank=True, default="")
    pinterest = models.URLField(null=True, blank=True, default="")
    pic = models.ImageField(
        upload_to=user_profile_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])], default="Default User.png", null=True, blank=True
    )
    favourites = models.ManyToManyField('accounts.Post', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.pic.url))
    admin_photo.short_description = "Profile Pic"
    admin_photo.allow_tags = True
    
    class Meta:
        ordering = ['-pk']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Profile, self).save(*args,**kwargs)

    def get_absolute_url(self):
        return reverse("profile-detail", kwargs={"pk":self.id, "slug": self.slug})

    def followerCount(self):
        return FollowUser.objects.filter(follower=self.user).count()

    def followingCount(self):
        return FollowUser.objects.filter(following=self.user).count()

class Notification(models.Model):
	NOTIFICATION_TYPES = ((1,'Like'),(2,'Comment'), (3,'Follow'))
    
	post = models.ForeignKey('accounts.Post', on_delete=models.CASCADE, related_name="noti_post", blank=True, null=True)
	sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="noti_from_user")
	user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="noti_to_user")
	notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
	text_preview = models.CharField(max_length=90, blank=True)
	date = models.DateTimeField(auto_now_add=True)
	is_seen = models.BooleanField(default=False)

class Post(models.Model):
    uploaded_by = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    msg = models.TextField()
    pic = models.ImageField(upload_to=post_image_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])
    tags = TaggableManager(verbose_name='Hashtags', help_text='Tag your post here')
    cr_date = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse("", args=[str(self.id)])
    
    def __str__(self):
        return self.msg[0:20]

    def admin_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.pic.url))
    admin_photo.short_description = "Post Picture"
    admin_photo.allow_tags = True

class PostFileContent(models.Model):
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post_owner')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_image')
    file = models.FileField(upload_to=post_images_directory_path, validators=[FileExtensionValidator(['png', 'jpg', 'jpeg'])])

    def __str__(self):
        return self.post.msg[0:20]
    
class PostComment(models.Model):
    commented_by = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    msg = models.CharField(max_length=500)
    updated_at = models.DateTimeField(auto_now=True)
    cr_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.msg[0:20]

    def user_comment_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        text_preview = comment.msg[:90]
        sender = comment.commented_by
        notify = Notification(post=post, sender=sender, user=post.uploaded_by, text_preview=text_preview, notification_type=2)
        notify.save()

    def user_del_comment_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.commented_by
        notify = Notification.objects.filter(post=post, sender=sender, notification_type=2)
        notify.delete()

class PostLike(models.Model):
    liked_by = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    cr_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s liked by %s" %(self.post, self.liked_by)

    def user_liked_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.liked_by
        notify = Notification(post=post, sender=sender, user=post.uploaded_by, notification_type=1)
        notify.save()

    def user_unlike_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.liked_by
        notify = Notification.objects.filter(post=post, sender=sender, notification_type=1)
        notify.delete()
    

class FollowUser(models.Model):
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='following')
    cr_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s is followed by %s" %(self.following, self.follower)

    def user_follow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        notify = Notification(sender=sender, user=following, notification_type=3)
        notify.save()
    
    def user_unfollow(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        following = follow.following
        notify = Notification.objects.filter(sender=sender, user=following, notification_type=3)
        notify.delete()

post_save.connect(PostLike.user_liked_post, sender=PostLike)
post_delete.connect(PostLike.user_unlike_post, sender=PostLike)

post_save.connect(FollowUser.user_follow, sender=FollowUser)
post_delete.connect(FollowUser.user_unfollow, sender=FollowUser)

post_save.connect(PostComment.user_comment_post, sender=PostComment)
post_delete.connect(PostComment.user_del_comment_post, sender=PostComment) 