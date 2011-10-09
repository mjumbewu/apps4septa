from django.conf.urls.defaults import patterns, include, url

from views import (MapApp, NearbyRoutesView, IntersectingRoutesView)

urlpatterns = patterns('septa',
    url(r'^$', MapApp.as_view()),

    url(r'^nearby_routes/(?P<lat>-?\d+(\.\d+)?),(?P<lon>-?\d+(\.\d+)?)',
        NearbyRoutesView.as_view()),

    url(r'^routes/(?P<left>-?\d+(\.\d+)?),(?P<bottom>-?\d+(\.\d+)?),'
        '(?P<right>-?\d+(\.\d+)?),(?P<top>-?\d+(\.\d+)?)',
        IntersectingRoutesView.as_view()),
)
