from django.urls import path
from django.http import HttpResponse
from .import views
from .views import ShopOwnerSignUpView, UserSignUpView, LoginView, ConsumerInterestsView

urlpatterns = [
    path('signup/', views.SignUpView, name='signup'),
    path('signup/business_owner/', views.ShopOwnerSignUpView, name='business_owner_signup'),
    path('signup/user/', views.UserSignUpView, name='user_signup'),
    path('login', LoginView.as_view(), name="login"),
    path('interests/', ConsumerInterestsView.as_view(), name='Consumer_interests'),
    path('profile/<int:pk>/<slug:slug>', views.ProfileDetailView.as_view(), name="profile-detail"),
]
