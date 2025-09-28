from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup_view, name='signup'),
    path('verify-otp/<int:user_id>/', views.verify_otp_view, name='verify_otp'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
   
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create-plan/', views.create_plan_view, name='create_plan'),
    path('view-plan/<int:plan_id>/', views.view_plan_view, name='view_plan'),
    
    path("about/", views.about_view, name="about"),
    path("contact/", views.contact_view, name="contact"),
    
    path('delete-plan/<int:pk>/', views.delete_plan, name='delete_plan'),
 
]
