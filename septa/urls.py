from django.conf.urls.defaults import patterns, include, url

from views import (MapApp, NearbyRoutesView)

urlpatterns = patterns('septa',
    url(r'^$', MapApp.as_view()),

    url(r'^nearby_routes/(?P<lat>-?\d+(\.\d+)?),(?P<lon>-?\d+(\.\d+)?)',
        NearbyRoutesView.as_view()),
)
