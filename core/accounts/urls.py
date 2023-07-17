from django.urls import path, include
from django.urls.resolvers import URLPattern

app_name = 'accounts'
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('api/v1/', include('accounts.api.v1.urls'), name='accounts-api-v1'),
]