from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import RegexValidator

STATE_CHOICES = (("Andhra Pradesh", "Andhra Pradesh"), ("Arunachal Pradesh ", "Arunachal Pradesh "), ("Assam", "Assam"),
                 ("Bihar", "Bihar"), ("Chhattisgarh", "Chhattisgarh"), ("Goa", "Goa"), ("Gujarat", "Gujarat"),
                 ("Haryana", "Haryana"), ("Himachal Pradesh", "Himachal Pradesh"),
                 ("Jammu and Kashmir ", "Jammu and Kashmir "), ("Jharkhand", "Jharkhand"), ("Karnataka", "Karnataka"),
                 ("Kerala", "Kerala"), ("Madhya Pradesh", "Madhya Pradesh"), ("Maharashtra", "Maharashtra"),
                 ("Manipur", "Manipur"), ("Meghalaya", "Meghalaya"), ("Mizoram", "Mizoram"), ("Nagaland", "Nagaland"),
                 ("Odisha", "Odisha"), ("Punjab", "Punjab"), ("Rajasthan", "Rajasthan"), ("Sikkim", "Sikkim"),
                 ("Tamil Nadu", "Tamil Nadu"), ("Telangana", "Telangana"), ("Tripura", "Tripura"),
                 ("Uttar Pradesh", "Uttar Pradesh"), ("Uttarakhand", "Uttarakhand"), ("West Bengal", "West Bengal"),
                 ("Andaman and Nicobar Islands", "Andaman and Nicobar Islands"), ("Chandigarh", "Chandigarh"),
                 ("Dadra and Nagar Haveli", "Dadra and Nagar Haveli"), ("Daman and Diu", "Daman and Diu"),
                 ("Lakshadweep", "Lakshadweep"),
                 ("National Capital Territory of Delhi", "National Capital Territory of Delhi"),
                 ("Puducherry", "Puducherry"))


class LostKid(models.Model):
    name = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/')
    date = models.DateField(default=timezone.now)
    state = models.CharField(max_length=100,
                             choices=STATE_CHOICES)
    description = models.TextField()
    email = models.EmailField()
    found = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=10,
                                    validators=[RegexValidator(r'^\d{1,10}$')], )
    found_location = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return "Kid : {}".format(self.name)


class Parent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10,
                                    validators=[RegexValidator(r'^\d{1,10}$')], )

    def __str__(self):
        return "User : {}".format(self.user.first_name)


class Kid(models.Model):
    name = models.CharField(max_length=50)
    photo_id = models.ImageField(upload_to='users/%Y/%m/%d/')
    parent = models.ForeignKey(to=Parent,
                               on_delete=models.CASCADE)
    lost = models.BooleanField(default=False)
    state = models.CharField(max_length=100,
                             choices=STATE_CHOICES)
    description = models.TextField()
    lost_instance = models.ForeignKey(to=LostKid, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "Kid : {}".format(self.name)


# to add fingerprint and iris later
class VerifyRequest(models.Model):
    photo = models.ImageField(upload_to='users/%Y/%m/%d/')
    location = models.TextField()
