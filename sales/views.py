from datetime import timedelta

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView, View

from orders.models import STATUS_CHOICES, Order


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class SalesView(StaffRequiredMixin, TemplateView):
    template_name = 'sales/sales.html'
    extra_context = {'active_page': 'sales'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.order_by('-updated_at')
        valid_orders = orders.exclude(status='refunded')
        context['orders'] = orders
        context['recent_orders'] = orders.filter(status='created')[:5]
        context['shipped_orders'] = orders.filter(status='shipped')[:5]
        context['paid_orders'] = orders.filter(status='paid')[:5]
        context['total_sales'] = valid_orders.aggregate(total=Sum('total'))['total'] or 0
        context['products_sold'] = valid_orders.aggregate(total=Count('cart__products'))['total']
        return context


class SalesAjaxView(StaffRequiredMixin, View):
    days = 7

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') != 'XMLHttpRequest':
            return JsonResponse({'error': 'Solo se permiten solicitudes Ajax.'}, status=400)

        today = timezone.localdate()
        start = today - timedelta(days=self.days - 1)

        per_day = (
            Order.objects.exclude(status='refunded')
            .filter(created_at__date__gte=start)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(total=Sum('total'))
        )
        totals = {row['day']: float(row['total']) for row in per_day}
        dates = [start + timedelta(days=i) for i in range(self.days)]

        per_status = dict(Order.objects.values_list('status').annotate(count=Count('id')))

        data = {
            'labels': [date.strftime('%d/%m') for date in dates],
            'totals': [totals.get(date, 0) for date in dates],
            'status_labels': [label for value, label in STATUS_CHOICES],
            'status_counts': [per_status.get(value, 0) for value, label in STATUS_CHOICES],
        }
        return JsonResponse(data)
