from django.contrib import messages
from django.http import request
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import ListView, CreateView, UpdateView,DeleteView

from catalogo.forms.usuario import UsuarioForm, UsuarioUpdateForm
from catalogo.models import User


class UsuarioListView(ListView):
    model = User

    def get_queryset(self):
        users = User.objects.exclude(id=self.request.user.id)
        users = users.exclude(is_superuser=True)
        return users

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UsuarioListView, self).get_context_data(**kwargs)
        return context


class UsuarioCreateView(CreateView):
    model = User
    form_class = UsuarioForm
    template_name = '../templates/catalogo/user_form.html'

    def get_context_data(self, **kwargs):
        context = super(UsuarioCreateView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.instance.user_by = self.request.user.pk
        form.instance.activo = True
        usuario = form.save()
        usuario.set_password(usuario.password)
        usuario.save()

        messages.success(self.request, f'El usuario {usuario.username} ha sido creado con éxito.')
        return super(UsuarioCreateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super(UsuarioCreateView, self).form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('catalogo:usuarios-list')
    
    def get_form_kwargs(self):
        kwargs = super(UsuarioCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Pasa el usuario al formulario
        return kwargs


class UsuarioUpdateView(UpdateView):
    model = User
    form_class = UsuarioUpdateForm

    def get_context_data(self, **kwargs):
        context = super(UsuarioUpdateView, self).get_context_data(**kwargs)
        context['edit'] = True
        return context

    def form_valid(self, form):
        form.instance.user_by = self.request.user.pk
        form.instance.updated_at = now()
        form.save()
        messages.success(self.request, f'El usuario {form.instance.username} ha sido actualizado con éxito.')
        return super(UsuarioUpdateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, form.errors)
        return super(UsuarioUpdateView, self).form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('catalogo:usuarios-list')

class UsuarioDeleteView(DeleteView):
    model = User

    def get_success_url(self):
        messages.success(self.request, "El registro ha sido eliminado con éxito.")
        return reverse_lazy('catalogo:usuarios-list')
    
    def get_form_kwargs(self):
        kwargs = super(UsuarioUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Pasa el usuario al formulario
        return kwargs
