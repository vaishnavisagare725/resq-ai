from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import RegisterSerializer, ResQTokenSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_scope = 'register'   # limited by DEFAULT_THROTTLE_RATES['register']


class LoginView(TokenObtainPairView):
    serializer_class = ResQTokenSerializer
    throttle_scope = 'login'      # limited by DEFAULT_THROTTLE_RATES['login']


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user