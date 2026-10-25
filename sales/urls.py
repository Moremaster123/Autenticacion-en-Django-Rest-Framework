from django.urls import path

from .views import SalesAjaxView, SalesView

app_name = 'sales'

urlpatterns = [
    path('', SalesView.as_view(), name='sales'),
    path('data/', SalesAjaxView.as_view(), name='sales-data'),
]
