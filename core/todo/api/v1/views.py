from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import permissions, status
from ...models import Task
from .serializers import TaskSerializer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class TasklModelViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = TaskSerializer(queryset,  context={'request': request},  many=True)
        return Response(serializer.data)

    # user=Task.objects.filter(user__in=User.objects.filter(username=self.request.user))
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])
        task.delete()
        return Response({'detail': 'task deleted successfully'})






#
#
# class TodoDetailApiView(viewsets.ModelViewSet):
#     serializer_class = TaskSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = "todo_id"
#
#     def get_object(self, queryset=None):
#         obj = Task.objects.get(pk=self.kwargs["todo_id"])
#         return obj
#
#     def delete(self, request, *args, **kwargs):
#         object = self.get_object()
#         object.delete()
#         return Response({"detail": "successfully removed"})
#
#     def perform_update(self, serializer):
#         serializer.save(user=self.request.user)
#
#     def post(self, request, *args, **kwargs):
#         object = self.get_object()
#         serializer = TaskSerializer(
#             data=request.data, instance=object, many=False
#         )
#         if serializer.is_valid():
#             serializer.save()
#         return Response(serializer.data)