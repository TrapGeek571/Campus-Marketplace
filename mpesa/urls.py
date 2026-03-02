from django.urls import path
from . import views

app_name = 'mpesa'

urlpatterns = [
    path('pay/<int:product_id>/', views.initiate_payment, name='initiate_payment'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('status/<int:transaction_id>/', views.payment_status, name='payment_status'),
]