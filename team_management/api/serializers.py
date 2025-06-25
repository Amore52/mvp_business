from rest_framework import serializers
from tasks.models import Task, User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'assignee', 'deadline', 'team']
        read_only_fields = ['id', 'created_at', 'updated_at']