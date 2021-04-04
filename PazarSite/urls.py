"""PazarSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls import handler400, handler403, handler404, handler500, url
from django.conf.urls.static import static
from accounts.views import AddPost, activation_sent_view, activate, ProfileEditView, ProfileView, post_comment_create_and_list_view, like, unlike, favourite, PostDetail, likePost, unlikePost, tags, PostDeleteView, PostEditView, showNotifications, DeleteNotification, follow, unfollow

admin.site.site_header = "Pazar Admin"
admin.site.site_title = "Pazar Admin Portal"
admin.site.index_title = "Welcome to Pazar Admin Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pazar.urls')),
    path('blog/', include('blog.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('account/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('sent/', activation_sent_view, name="activation_sent"),
    path('activate/<slug:uidb64>/<slug:token>/', activate, name='activate'),

    path('accounts/', include('allauth.urls')),
    path('change-password/',auth_views.PasswordChangeView.as_view(template_name='pazar/change-password.html',success_url='home'),name='change-password'),

    path('edit-profile/', ProfileEditView.as_view(), name="edit-profile"),
    path('profile/<int:id>/<slug:slug>', ProfileView.as_view(), name="profile"),

    path('password_change/', auth_views.PasswordChangeView.as_view(), name="password_change"),
    path('password_change/done', auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('posts/', post_comment_create_and_list_view, name="posts"),
    path('add-post/', AddPost, name='add-post'),
    path('post/like/<int:pk>', like, name="like-post"),
    path('post/unlike/<int:pk>', unlike, name="unlike-post"),
    path('like-post/<int:pk>', likePost, name='like'),
    path('unlike-post/<int:pk>', unlikePost, name='unlike'),
    path('post/favourite/<int:pk>', favourite, name='favourite'),
    path('post/<int:pk>', PostDetail, name='post-detail'),
    path('post/tags/<slug:slug>', tags, name="tag"),
    path('post/<int:pk>/edit', PostEditView.as_view(), name="post-edit"),
    path('post/<int:pk>/delete', PostDeleteView.as_view(), name='post-delete'),
    path('posts/notifications', showNotifications, name='show-notifications'),
    path('posts/notifications/<int:pk>/delete', DeleteNotification, name="delete-notification"),
    path('profile/follow/<int:pk>', follow, name='follow'),
    path('profile/unfollow/<int:pk>', unfollow, name="unfollow"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pazar.views.error_404_view'

handler400 = 'pazar.views.error_400_view'

handler500 = 'pazar.views.error_500_view'

handler403 = 'pazar.views.error_403_view'