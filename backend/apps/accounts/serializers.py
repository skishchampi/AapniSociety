from rest_framework import serializers

from .models import OTPChallenge, Role, User

# Roles a user may self-assign at signup. Privileged roles (connector, moderator,
# operator, admin) are granted only via Django admin / management commands — never
# from a client-supplied field.
SELF_ASSIGNABLE_ROLES = [Role.HOUSEHOLD, Role.WORKER]


class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    purpose = serializers.ChoiceField(
        choices=OTPChallenge.Purpose.choices,
        default=OTPChallenge.Purpose.LOGIN,
    )


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=12)
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    primary_role = serializers.ChoiceField(
        choices=SELF_ASSIGNABLE_ROLES, required=False, default=Role.HOUSEHOLD
    )


class UserSerializer(serializers.ModelSerializer):
    has_worker_profile = serializers.SerializerMethodField()
    has_household_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "email",
            "full_name",
            "primary_role",
            "is_staff",
            "date_joined",
            "has_worker_profile",
            "has_household_profile",
        ]
        read_only_fields = fields

    def get_has_worker_profile(self, obj) -> bool:
        return hasattr(obj, "worker_profile")

    def get_has_household_profile(self, obj) -> bool:
        return hasattr(obj, "household_profile")
