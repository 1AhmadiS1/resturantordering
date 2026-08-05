from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
    
        extra_fields["role"] = User.RoleChoices.PLATFORM_ADMIN
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class RoleChoices(models.TextChoices):
        PLATFORM_ADMIN = "platform_admin", "Platform Admin"
        OWNER = "owner", "Owner"
        WAITER = "waiter", "Waiter"
        CHEF = "chef", "Chef"

    email = models.EmailField(unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role=models.CharField(choices=RoleChoices.choices,max_length=20,default=RoleChoices.WAITER)
    restaurant = models.ForeignKey(
    "restaurant.Restaurant",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="employees"
)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email