from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:register')
    extra_context = {'active_page': 'register'}

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'El usuario {self.object.username} se registró correctamente.')
        return response
