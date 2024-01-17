from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('classes', views.classes, name='classes'),
    path('trainers', views.trainers, name='trainers'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('register', views.user_register, name='register'),
    path('profile', views.profile, name='profile'),
    path('change_password', views.change_password, name='change_password'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('update_classes/', views.update_classes, name='update_classes'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)