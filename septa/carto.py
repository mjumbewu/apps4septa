import itertools
import math
import os
from random import random, randint

# Import imaging libraries
try:
    import cairo
except ImportError:
    # Use PIL as a fallback
    import Image, ImageDraw

import settings


class Cartographer (object):
    pass


class BaseTransitMap (object):
    def __init__(self, w, h):
        self.img_wide = w
        self.img_high = h

    def draw_route(self, route, threshold=0.0):
        w, n, e, s = route.the_geom_900913.extent
        self._calc_t(w, n, e, s)

        self._draw_route(route, threshold, (255, 0, 0), 4)

    def draw_routes(self, routes, threshold=0.0, center=None):
        all_paths = routes[0].the_geom_900913
        for route in routes[1:]:
            all_paths = all_paths.union(route.the_geom_900913)
        w, n, e, s = all_paths.extent
        center.transform(all_paths.srid)
        self._calc_t(w, n, e, s, center)

        legend = {}
        for route in routes:
            color = (randint(0,255),randint(0,255),randint(0,255))
            self._draw_route(route, threshold, color, 4)
            legend[route.route] = "#%x%x%x" % color

        return legend

    def store(self):
        fn = 'map%s.png' % randint(0,1000)
        fullpath = os.path.join(settings.MY_STATIC_ROOT, fn)
        map_url = (settings.STATIC_URL + fn)

        self._store_img(fullpath)
        return map_url

    def _draw_route(self, route, threshold, color, size):
        path_data = route.the_geom_900913.simplify(threshold).coords
        self._draw_poly(path_data, color, size)

    def _calc_t(self, w, n, e, s, center=None):
        self.geo_wide = max(e - center.x, center.x - w)*2
        self.geo_high = max(s - center.y, center.y - n)*2
        self.geo_center = center

        print w, n, e, s, center.x, center.y
        print self.geo_wide, self.geo_high

        self.x_offset = -(center.x - self.geo_wide/2)
        self.y_offset = -(center.y - self.geo_high/2)

        hscale_factor = self.img_wide / self.geo_wide
        vscale_factor = self.img_high / self.geo_high
        self.scale_factor = min(hscale_factor, vscale_factor)

        self.cx_offset = (self.img_wide - self.geo_wide*self.scale_factor) / 2
        self.cy_offset = (self.img_high - self.geo_high*self.scale_factor) / 2

    def _t(self, x, y):
#        print '-'*60
#        print x, y
        x += self.x_offset
        y += self.y_offset

        x *= self.scale_factor
        y *= -self.scale_factor  # flip the vertical
        y += self.img_high

        x += self.cx_offset
        y += self.cy_offset

#        print x, y

#        x -= self.img_wide / 2
#        x = math.log(abs(x), ((self.img_wide / 2) ** 0.1)) * self.img_wide / 20
#        x += self.img_wide / 2

#        y -= self.img_high / 2
#        y = math.log(abs(y), ((self.img_high / 2) ** 0.1)) * self.img_high / 20
#        y += self.img_high / 2
#        print x, y

        return x, y


class PilTransitMap (BaseTransitMap):
    def __init__(self, w, h):
        super(PilTransitMap, self).__init__(w, h)

        self.img = Image.new("RGBA", (w, h), (255, 255, 255))

    def _draw_poly(self, path_data, color, size):

        #
        # This is a recursive function.  ``path_data`` may be a tuple of tuples.
        # Check the first element and see if it is a pair of numbers.  If so,
        # it's a polyline so draw it.  Otherwise, we need to go deeper, so call
        # the function again.
        #

        if len(path_data[0]) == 2 and all([isinstance(coord, (int, float))
                                           for coord in path_data[0]]):
            draw = ImageDraw.Draw(self.img)
            prev = self._t(*path_data[0])
            for coord in path_data[1:]:
                curr = self._t(*coord)
                draw.line(prev + curr, fill=color, width=size)
                prev = curr

        else:
            for sub_path_data in path_data:
                self._draw_poly(sub_path_data, color, size)

    def _store_img(self, fullpath):
        self.img.save(fullpath)


class CairoTransitMap (BaseTransitMap):
    def __init__(self, w, h):
        super(CairoTransitMap, self).__init__(w, h)

        self.img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.ctx = cairo.Context(self.img)
        self.ctx.rectangle(0, 0, w, h)
        self.ctx.set_source_rgb(1,1,1)
        self.ctx.fill()

#    def _transform_to(self, w, n, e, s, center=None):
#        self.geo_wide = max(e - center.x, center.x - w)*2
#        self.geo_high = max(s - center.y, center.y - n)*2
#        self.geo_center = center

#        x_offset = -(center.x - self.geo_wide/2)
#        y_offset = -(center.y - self.geo_high/2)

#        hscale_factor = self.img_wide / self.geo_wide
#        vscale_factor = self.img_high / self.geo_high
#        scale_factor = min(hscale_factor, vscale_factor)

#        cx_offset = (self.img_wide - self.geo_wide*scale_factor) / 2
#        cy_offset = (self.img_high - self.geo_high*scale_factor) / 2

#        self.ctx.translate(cx_offset, cy_offset)
#        self.ctx.translate(0, self.img_high)
#        self.ctx.scale(scale_factor, -scale_factor)
#        self.ctx.translate(x_offset, y_offset)

    def _draw_poly(self, path_data, color, size, stroke=True):

        #
        # This is a recursive function.  ``path_data`` may be a tuple of tuples.
        # Check the first element and see if it is a pair of numbers.  If so,
        # it's a polyline so draw it.  Otherwise, we need to go deeper, so call
        # the function again.
        #

        if len(path_data[0]) == 2 and all([isinstance(coord, (int, float))
                                           for coord in path_data[0]]):
            self.ctx.move_to(*self._t(*path_data[0]))
            for coord in path_data[1:]:
                self.ctx.line_to(*self._t(*coord))

        else:
            for sub_path_data in path_data:
                self._draw_poly(sub_path_data, color, size, stroke=False)

        if stroke:
            self.ctx.set_line_width(size)
            self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            self.ctx.set_source_rgb(*[component/255.0 for component in color])
            self.ctx.stroke()

    def _store_img(self, fullpath):
        self.img.write_to_png(fullpath)
