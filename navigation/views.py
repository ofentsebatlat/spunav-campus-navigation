from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Location, Path, RouteHistory
from .utils import find_shortest_path, get_alternative_routes

def home(request):
    locations = Location.objects.all().order_by('name')
    paths = Path.objects.all()
    return render(request, 'navigation/home.html', {
        'locations': locations,
        'paths': paths
    })

def find_route(request):
    if request.method == 'POST':
        start_id = request.POST.get('start_location')
        end_id = request.POST.get('end_location')
        
        if start_id == end_id:
            return render(request, 'navigation/home.html', {
                'error': "Start and destination cannot be the same.",
                'locations': Location.objects.all().order_by('name')
            })
            
        shortest_route = find_shortest_path(int(start_id), int(end_id))
        alternatives = get_alternative_routes(int(start_id), int(end_id))
        
        # Save to history if user is authenticated (optional)
        if shortest_route:
            RouteHistory.objects.create(
                user=request.user if request.user.is_authenticated else None,
                start_id=start_id,
                destination_id=end_id,
                distance=shortest_route['distance'],
                travel_time=shortest_route['estimated_time']
            )
            
        return render(request, 'navigation/route_result.html', {
            'route': shortest_route,
            'alternatives': alternatives,
            'start': get_object_or_404(Location, id=start_id),
            'destination': get_object_or_404(Location, id=end_id),
        })
    
    return render(request, 'navigation/home.html', {'locations': Location.objects.all().order_by('name')})

def admin_dashboard(request):
    # Analytics for admin
    most_searched = RouteHistory.objects.values('destination__name').annotate(count=Count('destination')).order_by('-count')[:5]
    recent_searches = RouteHistory.objects.all().order_by('-timestamp')[:10]
    high_traffic_paths = Path.objects.filter(crowd_level__gt=1.5).order_by('-crowd_level')
    
    return render(request, 'navigation/admin_dashboard.html', {
        'most_searched': most_searched,
        'recent_searches': recent_searches,
        'high_traffic_paths': high_traffic_paths,
    })
