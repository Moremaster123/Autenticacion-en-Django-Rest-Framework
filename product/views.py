from django.utils import timezone
from django.utils.formats import date_format
from django.views.generic import DetailView, ListView

from .models import Product


class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    extra_context = {'active_page': 'products'}

    def get_queryset(self):
        return Product.objects.filter(active=True).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today_text'] = date_format(timezone.localdate(), r'j \d\e F \d\e Y').lower()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    extra_context = {'active_page': 'products'}

    def get_queryset(self):
        return Product.objects.filter(active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = self.get_queryset().exclude(pk=self.object.pk)[:3]
        return context
