import json

from decimal import Decimal

from django.contrib.gis.geos import Point
from django.http import HttpResponse
from django.views import generic as views
from djangorestframework import views as rest
from djangorestframework import resources

from models import SeptaRoutes

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
