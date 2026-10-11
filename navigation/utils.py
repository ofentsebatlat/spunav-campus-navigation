import heapq
from collections import deque
from django.db.models import Q
from .models import Location, Path

class Graph:
    def __init__(self):
        self.nodes = set()
        self.edges = {}  # Adjacency list: {start_node_id: [(end_node_id, weight, path_id), ...]}

    def add_node(self, node_id):
        self.nodes.add(node_id)
        if node_id not in self.edges:
            self.edges[node_id] = []

    def add_edge(self, start_node_id, end_node_id, weight, path_id=None):
        self.add_node(start_node_id)
        self.add_node(end_node_id)
        self.edges[start_node_id].append((end_node_id, weight, path_id))

    @classmethod
    def build_from_db(cls):
        graph = cls()
        locations = Location.objects.all()
        for loc in locations:
            graph.add_node(loc.id)
        
        paths = Path.objects.all()
        for path in paths:
            # Dijkstra uses weight = distance * crowd_level
            weight = path.get_weight()
            graph.add_edge(path.start_location.id, path.end_location.id, weight, path.id)
            # Assuming bidirectional paths for campus walkways
            graph.add_edge(path.end_location.id, path.start_location.id, weight, path.id)
            
        return graph

def find_shortest_path(start_location_id, end_location_id):
    """
    Implements Dijkstra's algorithm using a Priority Queue (heapq).
    This demonstrates the use of:
    1. Graph Data Structure (Adjacency List)
    2. Priority Queue (for efficient node selection)
    3. Search Trees (representing the path exploration hierarchy)
    """
    graph = Graph.build_from_db()
    
    # Priority Queue: (total_weight, current_node_id, [list_of_node_ids])
    # This acts as the frontier for our path exploration tree
    pq = [(0, start_location_id, [start_location_id])]
    distances = {start_location_id: 0}
    
    while pq:
        current_weight, current_node_id, path = heapq.heappop(pq)
        
        if current_node_id == end_location_id:
            # Found the shortest path
            locations = Location.objects.filter(id__in=path)
            # To preserve order, we map them back
            loc_map = {loc.id: loc for loc in locations}
            ordered_locations = [loc_map[node_id] for node_id in path]
            
            actual_dist = sum_actual_distance(path)
            return {
                'path': ordered_locations,
                'total_weight': round(current_weight, 2),
                'distance': round(actual_dist, 2),
                'estimated_time': round(current_weight / 80, 1)  # Walking speed ~80m/min
            }
            
        if current_weight > distances.get(current_node_id, float('inf')):
            continue
            
        for neighbor_id, weight, path_id in graph.edges.get(current_node_id, []):
            new_weight = current_weight + weight
            if new_weight < distances.get(neighbor_id, float('inf')):
                distances[neighbor_id] = new_weight
                # Each push represents a branch in our exploration tree
                heapq.heappush(pq, (new_weight, neighbor_id, path + [neighbor_id]))
                
    return None

def get_alternative_routes(start_location_id, end_location_id, max_routes=2):
    """
    Uses Breadth-First Search (BFS) with a Queue (deque) to find alternative routes.
    This demonstrates the use of a Queue for level-order traversal of the graph.
    """
    graph = Graph.build_from_db()
    queue = deque([(start_location_id, [start_location_id])])
    routes = []
    
    while queue and len(routes) < max_routes:
        (current_node, path) = queue.popleft()
        
        if current_node == end_location_id:
            # Only add if it's not already in routes (to avoid duplicates)
            if path not in [r['node_ids'] for r in routes]:
                locations = Location.objects.filter(id__in=path)
                loc_map = {loc.id: loc for loc in locations}
                ordered_locations = [loc_map[node_id] for node_id in path]
                
                routes.append({
                    'path': ordered_locations,
                    'node_ids': path
                })
            continue
            
        for neighbor_id, weight, path_id in graph.edges.get(current_node, []):
            if neighbor_id not in path:
                queue.append((neighbor_id, path + [neighbor_id]))
                
    return routes

def sum_actual_distance(path_node_ids):
    """Calculates the physical distance (not weighted by crowd)"""
    total_distance = 0
    for i in range(len(path_node_ids) - 1):
        u, v = path_node_ids[i], path_node_ids[i+1]
        path_obj = Path.objects.filter(
            Q(start_location_id=u, end_location_id=v) | 
            Q(start_location_id=v, end_location_id=u)
        ).first()
        if path_obj:
            total_distance += path_obj.distance
    return total_distance
