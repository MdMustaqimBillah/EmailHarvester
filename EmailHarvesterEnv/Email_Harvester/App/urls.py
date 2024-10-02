from rest_framework.authtoken import views as auth_views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'history', views.ScrapingHistoryViewSet, basename='history')

app_name='App'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/', include(router.urls)),
    path('api/scrape/', views.scrape_url, name='scrape'),
    path('api-token-auth/', auth_views.obtain_auth_token, name='api_token_auth'),
]