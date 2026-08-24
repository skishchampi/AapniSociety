from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Manager for the phone-first custom User model."""

    use_in_migrations = True

    def _create_user(self, phone, password=None, **extra):
        if not phone:
            raise ValueError("A phone number is required.")
        email = extra.pop("email", None)
        if email:
            email = self.normalize_email(email)
        user = self.model(phone=phone, email=email, **extra)
        # OTP-first: most users have no usable password.
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra)

    def create_superuser(self, phone, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("primary_role", "admin")
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(phone, password, **extra)
