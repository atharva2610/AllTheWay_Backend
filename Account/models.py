from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from uuid import uuid4
from Address.models import Location


from django.contrib.auth.models import BaseUserManager

class MyAccountManager(BaseUserManager):

    def create_user(self,email,name,phone,password=None):
        if not email:
            raise ValueError("Email address required.")
        if not phone:
            raise ValueError("Phone no. is required.")
        if not name:
            raise ValueError("Name required.")
        user = self.model(
            email = self.normalize_email(email),
            name = name,
            phone = phone,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,name,phone,password):
        user  = self.create_user(
            email = self.normalize_email(email),
            name = name,
            phone = phone,
            password = password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def phoneNoLength(phone):
    if len(str(phone)) != 10:
        raise ValidationError('Phone No. should have 10 digits.')

class Account(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key = True, default = uuid4, editable = False)
    email = models.EmailField(verbose_name="email", max_length=50, unique=True)
    name = models.CharField(verbose_name='name', max_length=50)
    phone = models.PositiveBigIntegerField(verbose_name='phone no.', validators=[phoneNoLength])
    join_date = models.DateTimeField(verbose_name="join date", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MyAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    def __str__(self):
        return self.name


   
class DeliveryLocation(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='delivery_locations')
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='location')
    is_deleted= models.BooleanField(default=False)

    def __str__(self):
        return self.location.full_address