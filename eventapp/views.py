from django.http import JsonResponse
from django.shortcuts import render
from .models import Event
from .forms import EventForm
def add_event(request):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        
        if Event.objects.filter(name=request.POST.get('name')).exists():
            return JsonResponse({"error": "Event with this name already exists"}, status=400)

        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Successfully added event"}, status=201)
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        form = EventForm()
        return render(request, 'add_event.html', {'form': form})

def events_list(request):
    if request.method=="GET":
      events = Event.objects.all()
      events_list = [
        {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "image": event.image.url if event.image else ""
        } for event in events
    ]
    return JsonResponse({'events_list':events_list})