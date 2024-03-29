from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


app_name = 'api-v1'
urlpatterns = [

    path('registration/', views.RegistrationApiView.as_view(), name='registration'),
    path('activation/confirm/<str:token>', views.ActivationApiView.as_view(), name='registration-confirm'),
    path("activation/resend/",views.ActivationResendApiView.as_view(),name="activation-resend",),

    # change pass
    path("change-password/", views.ChangePasswordApiView.as_view(), name="change-password",),

    # rest pass
    path("reset-password/emai/",views.RestPasswordEmailApiView.as_view(),name="reset-password-email",),
    path("reset-password/<str:token>",views.ResetPasswordApiView.as_view(),name="reset-password",),

    # login token
    path("token/login/", views.CustomAuthToken.as_view(), name="token-login"),
    path("token/logout/", views.CustomDiscardAuthToken.as_view(), name="token-logout"),
    # Jwt
    path("jwt/create/", views.CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-create"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),

]
