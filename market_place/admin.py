from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.filters import DateFieldListFilter
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from booking.models import Booking
from .models import StorageBox


class DateRangeFilter(DateFieldListFilter):
    def __init__(self, *args, **kwargs):
        super(DateRangeFilter, self).__init__(*args, **kwargs)

    def queryset(self, request, queryset):
        if self.used_parameters.get('start_date__gte', None) and self.used_parameters.get('end_date__lte', None):
            start_date = self.used_parameters['start_date__gte']
            end_date = self.used_parameters['end_date__lte']

            booked_boxes = Booking.objects.filter(
                Q(start_date__lte=end_date) & Q(end_date__gte=start_date)
            ).values_list('storage_box', flat=True)

            return queryset.exclude(id__in=booked_boxes)

        return super(DateRangeFilter, self).queryset(request, queryset)


class AvailabilityListFilter(SimpleListFilter):
    title = _('availability')
    parameter_name = 'availability'

    def lookups(self, request, model_admin):
        return (
            ('available', _('Available')),
            ('booked', _('Booked')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'available':
            booked_boxes = Booking.objects.values_list('storage_box', flat=True)
            return queryset.exclude(id__in=booked_boxes)

        elif self.value() == 'booked':
            booked_boxes = Booking.objects.values_list('storage_box', flat=True)
            return queryset.filter(id__in=booked_boxes)


# Update the StorageBoxAdmin class:

@admin.register(StorageBox)
class StorageBoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'surface', 'display_monthly_price', 'display_owner')
    ordering = ('-id',)
    list_filter = (
        'surface',
        AvailabilityListFilter,
        ('booking__start_date', DateRangeFilter),
        ('booking__end_date', DateRangeFilter)
    )

    def display_monthly_price(self, obj):
        return f"{obj.monthly_price.initial[0]} {obj.monthly_price.initial[1]}"

    display_monthly_price.short_description = "Monthly Price"

    def display_owner(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}"

    display_owner.short_description = "Owner"