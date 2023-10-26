import json

from django.db.models import Value, CharField, F
from django.db.models.functions import Concat
from django.views.generic import ListView
from django.shortcuts import render, redirect
from .forms import StorageBoxForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import StorageBox
from .forms import StorageBoxForm
from django.contrib import messages

from booking.models import Booking
from market_place.models import StorageBox

class BoxesView(ListView):
    model = StorageBox
    template_name = 'boxes.html'
    context_object_name = 'available_boxes'

    def get_queryset(self):
        booked_boxes = Booking.objects.values_list('storage_box', flat=True)
        available_boxes = StorageBox.objects.exclude(id__in=booked_boxes)

        sort_criteria = {"price_asc": "price",
                     "price_desc": "-price",
                     "surface_asc": "surface",
                     "surface_desc": "-surface",
                     "address_asc": "full_address",
                     "address_desc": "-full_address"
                     }
        sort = self.request.GET.get('sort')
        if sort:
            if sort in ["address_asc", "address_desc"]:
                available_boxes = available_boxes.annotate(
                    full_address=Concat(
                        Value(' '),
                        F('city'),
                        output_field=CharField()
                    )
                )
            elif sort in ["price_asc", "price_desc"]:
                available_boxes = list(available_boxes)
                prices = [{"amount": float(i.monthly_price.initial[0]), "currency": str(i.monthly_price.initial[1])} for
                          i in available_boxes]
                indexed_qs = list(enumerate(available_boxes))
                indexed_qs.sort(key=lambda ix: prices[ix[0]]['amount'], reverse=(sort == "price_desc"))
                available_boxes = [item[1] for item in indexed_qs]

            else:
                available_boxes = available_boxes.order_by(sort_criteria[sort])

        return available_boxes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prices = [{"amount": str(i.monthly_price.initial[0]), "currency": str(i.monthly_price.initial[1])} for i in self.get_queryset()]

        for box, price in zip(self.get_queryset(), prices):
            box.price = price

        context['available_boxes'] = self.get_queryset()
        return context


def create_storage_box(request):
    if request.method == "POST":
        form = StorageBoxForm(request.POST, request.FILES)
        if form.is_valid():
            storage_box = form.save(commit=False)
            # You can set the slug field here using any logic you prefer.
            # Example: storage_box.slug = slugify(storage_box.title)
            storage_box.save()
            messages.success(request, "StorageBox created successfully!")
            return redirect('boxes')  # Update the name of the redirect view accordingly
    else:
        form = StorageBoxForm()
    return render(request, 'box_form.html', {'form': form})

class StorageBoxCreateView(CreateView):
    model = StorageBox
    form_class = StorageBoxForm
    template_name = 'box_form.html'
    success_url = reverse_lazy('boxes')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "StorageBox created successfully!")
        return response