from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuditEvent, Role, User
from .otp import OTPError, issue_otp, verify_otp
from .serializers import OTPRequestSerializer, OTPVerifySerializer, UserSerializer


class OTPRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "otp"

    @extend_schema(request=OTPRequestSerializer, responses={200: dict})
    def post(self, request):
        s = OTPRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        _, code = issue_otp(s.validated_data["phone"], s.validated_data["purpose"])
        from django.conf import settings

        body = {"detail": "OTP issued."}
        if getattr(settings, "OTP_RETURN_CODE_IN_RESPONSE", False):
            body["dev_code"] = code  # dev only — never set in prod settings
        return Response(body, status=status.HTTP_200_OK)


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "otp"

    @extend_schema(request=OTPVerifySerializer, responses={200: dict})
    def post(self, request):
        s = OTPVerifySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        phone = s.validated_data["phone"]
        try:
            verify_otp(phone, s.validated_data["code"])
        except OTPError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        role = s.validated_data.get("primary_role") or Role.HOUSEHOLD
        if role not in Role.values:
            role = Role.HOUSEHOLD
        defaults = {"primary_role": role}
        if s.validated_data.get("full_name"):
            defaults["full_name"] = s.validated_data["full_name"]
        user, created = User.objects.get_or_create(phone=phone, defaults=defaults)

        AuditEvent.objects.create(
            actor=user,
            action="auth.signup" if created else "auth.login",
            target_type="User",
            target_id=str(user.pk),
        )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
                "created": created,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=dict, responses={205: None})
    def post(self, request):
        token = request.data.get("refresh")
        if token:
            try:
                RefreshToken(token).blacklist()
            except Exception:
                pass
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=UserSerializer)
    def get(self, request):
        return Response(UserSerializer(request.user).data)
