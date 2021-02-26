from django.contrib import admin
from .models import *


# Register your models here.

class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 3


class HotelAdmin(admin.ModelAdmin):
    inlines = [HotelImageInline, ]


admin.site.register(Hotel, HotelAdmin)


admin.site.register(Room)
admin.site.register(Receptionist)
admin.site.register(Guest)
admin.site.register(ReservationActive)
admin.site.register(ReservationInactive)
