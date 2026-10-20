from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Who am I? Read-only."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'department']
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'password']

    def validate_password(self, value):
        validate_password(value)          # Django's password rules
        return value

    def create(self, validated_data):
        # role is never taken from the client: new accounts are always citizens
        return User.objects.create_user(**validated_data, role=User.Role.CITIZEN)


class ResQTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role            # convenience for React only; the backend never trusts it
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data