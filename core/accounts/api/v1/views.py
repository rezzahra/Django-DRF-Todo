from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializers, CustomAuthTokenSerializer, CustomTokenObtainPairSerializer,\
    ChangePasswordSerializer,ActivationResendSerializer, RestPasswordEmailSerializer, ResetPasswordSerializer


# custom token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

# logout token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# jwt
from rest_framework_simplejwt.views import TokenObtainPairView

# change pass
from django.contrib.auth import get_user_model
User = get_user_model()

# email
from ..utils import EmailThread
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from mail_templated import EmailMessage

# # activation email
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from django.conf import settings


class RegistrationApiView(generics.GenericAPIView):
    serializer_class = RegistrationSerializers

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializers(data = request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data['email']
            data = {
                'email' : email
            }
            user_obj = get_object_or_404(User, email=email)
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage(
                "email/activation_email.tpl",
                {"token": token},
                "admin@gmail.com",
                to=[email],
            )
            EmailThread(email_obj).start()
            return Response(data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordApiView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"detail": "password changed successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#
# class Test(generics.GenericAPIView):
#     def get(self, request, *args, **kwargs):
#         email_obj = EmailMessage('email/hello.tpl', {'name': 'zahra'}, 'info@gmail.com',to=['user@gmail.com'])
#         EmailThread(email_obj).start()
#         return Response('send email')
#

class ActivationApiView(generics.GenericAPIView):
    def get(self, request, token, *args, **kwargs):
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = token.get("user_id")
        except ExpiredSignatureError:
            return Response(
                {"detail": "token has been expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except InvalidSignatureError:
            return Response(
                {"detail": "token is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )

        user_obj = User.objects.get(pk=user_id)
        if user_obj.is_verified:
            return Response({"detail": "your account has already been verified"})
        user_obj.is_verified = True
        user_obj.save()
        return Response(
            {"detail": "your account have been verified and activated successfully"}
        )


class ActivationResendApiView(generics.GenericAPIView):
    serializer_class = ActivationResendSerializer

    def post(self, request, *args, **kwargs):
        serializer = ActivationResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user"]
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage(
            "email/activation_email.tpl",
            {"token": token},
            "admin@gmail.com",
            to=[user_obj.email],
        )
        EmailThread(email_obj).start()
        return Response(
            {"detail": "user activation resend successfully"}, status=status.HTTP_200_OK
        )

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class RestPasswordEmailApiView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = RestPasswordEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user"]
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage(
            "email/reset_email.tpl",
            {"token": token},
            "admin@gmail.com",
            to=[user_obj.email],
        )
        EmailThread(email_obj).start()
        return Response({"detail": "send email"}, status=status.HTTP_200_OK)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)



class ResetPasswordApiView(generics.GenericAPIView):
    Model = User
    serializer_class = ResetPasswordSerializer

    def get(self, request, token, *args, **kwargs):
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except DecodeError:
            return Response(
                {"detail": "token is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        except ExpiredSignatureError:
            return Response(
                {"detail": "token has been expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response({"detail": "token is valid and not expire"})

    def post(self, request, token, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = token.get("user_id")
        except DecodeError:
            return Response(
                {"detail": "token is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        except ExpiredSignatureError:
            return Response(
                {"detail": "token has been expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            user_obj = User.objects.get(pk=user_id)
            user_obj.set_password(serializer.data.get("password"))
            user_obj.save()
            return Response({"detail": "your password reset successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



