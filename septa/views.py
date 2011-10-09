import json
import os

from decimal import Decimal
from random import randint

from django.contrib.gis.geos import Point, Polygon
from django.http import HttpResponse
from django.views import generic as views
from djangorestframework import views as rest
from djangorestframework import resources

import settings

from models import SeptaRoutes
from carto import PilTransitMap

class MapApp (views.TemplateView):
    template_name = 'index.html'


class NearbyRoutesView (rest.View):

    def get(self, request, lat, lon, *args, **kwargs):
        srid = request.REQUEST.get('srid', '900913')
        radius = request.REQUEST.get('radius', None)
        count = request.REQUEST.get('count', None)

        radius = float(radius) if radius else None
        count = int(count) if count else None

        lat = float(lat)
        lon = float(lon)

        origin = Point(lat, lon, srid=srid)
        routes = get_nearby_routes(origin,
                                   radius=radius,
                                   count=count,
                                   srid=srid)

        return [json.loads(route.geojson) for route in routes]

# Simply constructs a query
def get_nearby_routes(origin, radius=None, count=None, srid='900913'):
    routes = SeptaRoutes.objects.all() \
        .distance(origin, field_name='the_geom_{0}'.format(srid)) \
        .order_by('distance') \
        .geojson()

    if radius:
        filter_params = {
            'the_geom_{0}__distance_lt'.format(srid): (origin, radius)
        }
        routes = routes.filter(**filter_params)

    if count:
        routes = routes[:count]

    return routes

class IntersectingRoutesView (rest.View):

    def get(self, request, left, bottom, right, top, *args, **kwargs):
        srid = request.REQUEST.get('srid', '4326')
        width = request.REQUEST.get('width', None)
        height = request.REQUEST.get('height', None)
        count = request.REQUEST.get('count', None)

        width = int(width) if width else 1024
        height = int(height) if height else 768
        count = int(count) if count else 10
        left = float(left)
        bottom = float(bottom)
        right = float(right)
        top = float(top)

        bbox = Polygon.from_bbox((left, bottom, right, top))
        bbox.srid = int(srid)
        origin = Point((left+right)/2.0, (top+bottom)/2.0)
        routes = get_intersecting_routes(bbox,
                                   count=count,
                                   srid=srid,
                                   center=origin)

        transit_map = PilTransitMap(width, height)
        legend = transit_map.draw_routes(routes)

        fn = 'map%s.png' % randint(0,1000)
        transit_map.img.save(os.path.join(settings.MY_STATIC_ROOT, fn))
        map_url = (settings.STATIC_URL + fn)

        res = {
            'routes': [{
                'route': route.route,
                'label': route.label,
                'color': legend[route.route],
                'distance': route.distance,
            } for route in routes],
            'map_url': map_url,
            'centroid': "[%s, %s]" % (origin.x, origin.y),
        }

#        return [json.loads(route.geojson) for route in routes]
        return res

def get_intersecting_routes(bbox, count=10, srid='4326', center=Point(0,0)):
    routes = SeptaRoutes.objects.all() \
        .distance(center, field_name='the_geom_' + srid) \
        .order_by('distance')

    filter_params = {
        'the_geom_' + srid + '__intersects': bbox
    }
    routes = routes.filter(**filter_params)

    if count:
        routes = routes[:count]

    return routes
