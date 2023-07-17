from rest_framework import serializers
from ...models import Task
from accounts.models import User


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    relative_url = serializers.URLField(source="get_absolute_api_url", read_only=True)
    absolute_url = serializers.SerializerMethodField(method_name='get_absolute_url')

    class Meta:
        model = Task
        fields = ('title', 'completed', 'user', 'relative_url', 'absolute_url')

    def get_absolute_url(self, object):
        request = self.context.get("request")
        return request.build_absolute_uri(object.pk)

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("snippet", None)
            rep.pop("absolute_url", None)
        return rep

    def create(self, validated_data):
        validated_data["user"] = User.objects.get(
            id=self.context.get("request").user.id
        )
        return super().create(validated_data)

    def put(self, validated_data):
        validated_data["user"] = User.objects.get(
            id=self.context.get("request").user.id
        )
        return super().update(validated_data)


