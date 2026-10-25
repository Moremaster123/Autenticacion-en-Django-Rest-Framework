from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import LoginView, LogoutView, ProductViewSet, ProfileView, UserViewSet

app_name = 'api'

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
] + router.urls
