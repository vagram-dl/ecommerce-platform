from django.urls import path
from .views import RegisterView, UserView, AuthorizeView, TokenView, UserInfoView
from .views import LoginView
from .views import LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(),name='login'),
    path('me/', UserView.as_view(), name='me'),
    path('logout/', LogoutView.as_view(),name='logout'),
    path('authorize/', AuthorizeView.as_view(), name='authorize'),
    path('token/',TokenView.as_view(),name='token'),
    path('userinfo/', UserInfoView.as_view(), name = 'userinfo'),
]