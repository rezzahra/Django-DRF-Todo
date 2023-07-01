from django.urls import path, include

app_name = 'todo'
urlpatterns = [
    path('api/v1/', include('todo.api.v1.urls'), name='api-v1'),
]