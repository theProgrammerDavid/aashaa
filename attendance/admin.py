from django.contrib import admin
from .models import LostKid, Parent, Kid, VerifyRequest


admin.site.register(LostKid)
admin.site.register(Parent)
admin.site.register(Kid)
admin.site.register(VerifyRequest)

