from rest_framework import serializers
from masterapp.models import Credential
from accountapp.models import User, UserGroup

class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    user_type_name = serializers.CharField(source='user_type.name', read_only=True)

    class Meta:
        model = User
        fields = ['id','username','first_name','last_name', 'user_type_name']


class GroupSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator', read_only=True)

    class Meta:
        model = UserGroup
        fields = ['id','name','creator_name']
        