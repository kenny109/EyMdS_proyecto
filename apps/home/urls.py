from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from . import forms, views

app_name = "Home"

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_request, name="login"),
    # Desde Django 5.0 LogoutView solo acepta POST: el navbar envía un formulario (MR-111)
    path("logout/", LogoutView.as_view(template_name="home/logout.html"), name="logout"),
    path("about/", TemplateView.as_view(template_name="home/about.html"), name="about"),
    path("register/", views.register, name="register"),
    path("tiendas/", views.tiendas, name="tiendas"),
    # Recuperar contraseña por correo (MR-119). El enlace caduca (PASSWORD_RESET_TIMEOUT) y
    # la pantalla responde igual exista o no el correo, para no revelar qué cuentas existen.
    path("password/olvide/", auth_views.PasswordResetView.as_view(
        template_name="home/password/reset_form.html",
        email_template_name="home/password/reset_email.txt",
        subject_template_name="home/password/reset_subject.txt",
        form_class=forms.RecuperarPasswordForm,
        success_url=reverse_lazy("Home:password_reset_done"),
    ), name="password_reset"),
    path("password/olvide/enviado/", auth_views.PasswordResetDoneView.as_view(
        template_name="home/password/reset_done.html"), name="password_reset_done"),
    path("password/restablecer/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="home/password/reset_confirm.html",
        form_class=forms.NuevaPasswordForm,
        success_url=reverse_lazy("Home:password_reset_complete"),
    ), name="password_reset_confirm"),
    path("password/restablecer/listo/", auth_views.PasswordResetCompleteView.as_view(
        template_name="home/password/reset_complete.html"), name="password_reset_complete"),
    # Cambiar contraseña con la sesión iniciada (MR-119)
    path("password/cambiar/", auth_views.PasswordChangeView.as_view(
        template_name="home/password/change_form.html",
        form_class=forms.CambiarPasswordForm,
        success_url=reverse_lazy("Home:password_change_done"),
    ), name="password_change"),
    path("password/cambiar/listo/", auth_views.PasswordChangeDoneView.as_view(
        template_name="home/password/change_done.html"), name="password_change_done"),
]

urlpatterns += staticfiles_urlpatterns()
### Con esto, le agrego los statics files al URL PATTERNS
### Ahora puedo llamar o manipular los archivos staticos
### Desde el HTML, desde los Templates
