from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from .forms import LoginForm, SignUpForm, PasswordResetForm, SetPasswordForm
from .mixins import RedirectAuthenticatedMixin

class SignUp(RedirectAuthenticatedMixin, CreateView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        self.object = form.save()
        auth_login(self.request, self.object) # Login the user
        return redirect(self.get_success_url())

class Login(RedirectAuthenticatedMixin, LoginView):
    form_class = LoginForm
    template_name = 'login.html'
    success_url = reverse_lazy('core:home') 

class ForgotPassword(RedirectAuthenticatedMixin, PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'forgot-password.html'
    email_template_name = 'password-reset-email.html'
    success_url = reverse_lazy('accounts:login')

class ResetPassword(RedirectAuthenticatedMixin, PasswordResetConfirmView):
    form_class = SetPasswordForm
    template_name = 'reset-password.html'
    success_url = reverse_lazy('accounts:login')


# class ProfileView(LoginRequiredMixin, TemplateView):
#     template_name = 'profile.html'