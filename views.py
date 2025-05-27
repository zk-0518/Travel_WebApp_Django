from django.shortcuts import render, redirect
from .forms import SignUp
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models_mongo import Destination
from django.http import HttpResponse
from mongoengine.queryset.visitor import Q

# Create your views here.

# to open home page when server runs
def home(request):
    return render(request, 'home.html')


# new user registeration login
def signup(request):
    if request.method=='POST':
        form=SignUp(request.POST)
        if form.is_valid():
            user=form.save(commit=False) #when registration successful, close it 
            user.set_password(form.cleaned_data['password']) #hashing the password
            user.save()
            return redirect('loged_home') #send user to loged in home page after successful regsitration
    else:
        form=SignUp()
    return render(request, 'signup.html', {'form':form})

# existing user login logic
def login_user(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('loged_home') #redirect to loged in home page if login successful
        else:
            return render(request, 'login.html', {'error':'Invalid Credentials'})
    return render(request, 'login.html')


# to open destination page linked from database and also provide category drop down menu
@login_required
def destination_list(request):
    category = request.GET.get('category')

    if category:
        destinations = Destination.objects.filter(Category=category)
    else:
        destinations = Destination.objects.all()

    # Manually collect all unique categories
    all_destinations = Destination.objects.all()
    categories = list(set(d.Category for d in all_destinations if d.Category))

    return render(request, "destination_list.html", {
        "destinations": destinations,
        "categories": categories,
        "selected_category": category,
    })


# This view will dynamically fetch the correct destination based on MongoDB _id.
def destination_detail(request, id):
    try:
        destination = Destination.objects.get(id=id) 
    except Destination.DoesNotExist:
        return render(request, '404.html', status=404) 
    
    # recommaednation function
    recommendations = recommend_similar_destinations(destination)

    return render(request, 'destination_detail.html', {
    'destination': destination,
    'recommendations': recommendations
    
})

    
# dummy payment gateway page
def payment_page(request, destination_id):
    try:
        destination = Destination.objects.get(id=destination_id)
    except Destination.DoesNotExist:
        return HttpResponse("Destination not found", status=404)

    return render(request, 'payment.html', {'destination': destination})

# itinerary generation logic
def generate_itinerary(request):
    destination_name = request.GET.get('destination')
    num_days = int(request.GET.get('days', 1))
    budget = float(request.GET.get('budget', 0))
    people = int(request.GET.get('people', 1))

    destinations = list(Destination.objects(Destination__iexact=destination_name))
    image_url = destinations[0].image_url if destinations else None
    print(f"Found {len(destinations)} entries for: {destination_name}")

    itinerary = []
    daily_budget = budget / num_days
    daily_hours = 6
    DEFAULT_HOURS = 2

    if not destinations:
        return render(request, 'itinerary.html', {
            'itinerary': [],
            'destination': destination_name,
        })

    dest = destinations[0]
    spots = [s.strip() for s in (dest.PopularSpot or '').split(',')]
    activities = [a.strip() for a in (dest.Activities or '').split(',')]

    
    if len(spots) > len(activities):
        activities += ['General Sightseeing'] * (len(spots) - len(activities))

    price_per_item = float(dest.Price or 0) * people / max(len(spots), 1)

    
    all_blocks = []
    for spot, act in zip(spots, activities):
        all_blocks.append({
            # 'Title': dest.Title,
            'PopularSpot': spot,
            'Activities': act,
            # 'Category': dest.Category,
            'Price': price_per_item,
            # 'image_url': dest.image_url,
            # 'Description': dest.Description
        })

    block_index = 0
    for day in range(num_days):
        used_hours = 0
        spent = 0
        day_plan = []

        while block_index < len(all_blocks):
            block = all_blocks[block_index]
            cost = block['Price']

            if (used_hours + DEFAULT_HOURS <= daily_hours and spent + cost <= daily_budget) or len(day_plan) == 0:
                day_plan.append(block)
                used_hours += DEFAULT_HOURS
                spent += cost
                block_index += 1
            else:
                break

        itinerary.append({
            'day': day + 1,
            'activities': day_plan,
            'total_hours': used_hours,
            'total_cost': spent
        })

    return render(request, 'itinerary.html', {
        'itinerary': itinerary,
        'destination': destination_name,
        'image_url': image_url,
    })

# home page for loged in users
def loged_home(request):
    return render(request, 'loged_home.html')

# user profile
def profile(request):
    return render(request, 'profile.html')

# recommendation logic
def recommend_similar_destinations(destination):
    similar_destinations = Destination.objects(
        Q(Category=destination.Category) 
    ).filter(id__ne=destination.id)[:4]  # only 4 recommendations

    return similar_destinations
