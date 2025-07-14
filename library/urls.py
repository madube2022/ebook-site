from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.ebook_list, name='ebook_list'),
    path('ebook/<int:pk>/', views.ebook_detail, name='ebook_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='library/registration/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'), 
    path('ebook/<int:pk>/download-file/', views.download_ebook, name='download_ebook'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_ebook, name='upload_ebook'),

    # ✅ Add this for initiating payment
    path('ebook/<int:pk>/pay/', views.initiate_payment, name='initiate_payment'),

    # ✅ (Optional but recommended) Add this to verify payment callback
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('sales-report/', views.sales_report, name='sales_report'),

]
