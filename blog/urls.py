from django.urls import path
from .import views

urlpatterns = [
    path('', views.bloghome, name="blog_home"),
    path('category/<slug:slug>', views.blogcategory, name="blog_category"),
    path('all-category', views.category, name="all_category"),
    path('article/<slug:slug>', views.blogPost, name="blog-post"),
    path('postComment', views.postComment, name="postComment"),
    path('tag/<slug:slug>/', views.tagged, name="tagged"),
    path('write-for-us', views.writeForUs, name="writeForUs"),
    path('search', views.search, name="search"),
    path('edit/<slug:slug>', views.BlogEditView.as_view(), name="edit-blog"),
    path('delete/<slug:slug>', views.BlogDeleteView.as_view(), name="delete-blog"),
]
