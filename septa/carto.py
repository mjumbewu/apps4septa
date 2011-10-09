import itertools
try:
    import cairo
except ImportError:
    pass
import Image, ImageDraw

from random import random, randint
#img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
#ctx = cairo.Context(img)
#ctx.scale(100, 100)
#ctx.move_to(0, 0)
#ctx.line_to(30, 50)
#img.write_to_png('hello.png')
#ctx.stroke()


class Cartographer (object):
    pass


class PilTransitMap (object):
    def __init__(self, w, h):
        self.wide = w
        self.high = h

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

#    def _mark_beginnings(self, path_data):

#        if len(path_data[0]) == 2 and all([isinstance(coord, (int, float))
#                                           for coord in path_data[0]]):
#            self.ctx.arc(*(path_data[0]),
#                         )

#        else:
#            for sub_path_data in path_data:
#                self._trace_poly(sub_path_data)

    def _draw_route(self, route, threshold, color, size):
        path_data = route.the_geom_900913.simplify(threshold).coords
        self._draw_poly(path_data, color, size)

#    def _trace_features(self, route):
#        path_data = route.the_geom_900913.coords


    def draw_route(self, route, threshold=0.0):
        w, n, e, s = route.the_geom_900913.extent
        self._calc_t(w, n, e, s)

        self._draw_route(route, threshold, (255, 0, 0), 4)

    def _calc_t(self, w, n, e, s):
        self.x_offset = -w
        self.y_offset = -n

        hscale_factor = self.wide / float(e - w)
        vscale_factor = self.high / float(s - n)
        self.scale_factor = min(hscale_factor, vscale_factor)

        self.cx_offset = (self.wide - (e - w)*self.scale_factor) / 2
        self.cy_offset = (self.high - (s - n)*self.scale_factor) / 2

    def _t(self, x, y):
        x += self.x_offset
        y += self.y_offset

        x *= self.scale_factor
        y *= -self.scale_factor

        y += self.high

        x += self.cx_offset
        y += self.cy_offset

        return x, y

    def draw_routes(self, routes, threshold=0.0):
        all_paths = routes[0].the_geom_900913
        for route in routes[1:]:
            all_paths = all_paths.union(route.the_geom_900913)
        w, n, e, s = all_paths.extent
        self._calc_t(w, n, e, s)

        legend = {}
        for route in routes:
            color = (randint(0,255),randint(0,255),randint(0,255))
            self._draw_route(route, threshold, color, 4)
            legend[route.route] = "#%x%x%x" % color

        return legend

class TransitMap (object):
    def __init__(self, w, h):
        self.wide = w
        self.high = h

        self.img = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        self.ctx = cairo.Context(self.img)
        self.ctx.rectangle(0, 0, w, h)
        self.ctx.set_source_rgb(1,1,1)
        self.ctx.fill()

    def _transform_to(self, w, n, e, s):
        hscale_factor = self.wide / float(e - w)
        vscale_factor = self.high / float(s - n)
        scale_factor = min(hscale_factor, vscale_factor)
        self.ctx.translate(0, self.high)
        self.ctx.scale(scale_factor, -scale_factor)
        self.ctx.translate(-w, -n)

    def _trace_poly(self, path_data):

        #
        # This is a recursive function.  ``path_data`` may be a tuple of tuples.
        # Check the first element and see if it is a pair of numbers.  If so,
        # it's a polyline so draw it.  Otherwise, we need to go deeper, so call
        # the function again.
        #

        if len(path_data[0]) == 2 and all([isinstance(coord, (int, float))
                                           for coord in path_data[0]]):
            self.ctx.move_to(*(path_data[0]))
            for coord in path_data[1:]:
                self.ctx.line_to(*coord)

        else:
            for sub_path_data in path_data:
                self._trace_poly(sub_path_data)

#    def _mark_beginnings(self, path_data):

#        if len(path_data[0]) == 2 and all([isinstance(coord, (int, float))
#                                           for coord in path_data[0]]):
#            self.ctx.arc(*(path_data[0]),
#                         )

#        else:
#            for sub_path_data in path_data:
#                self._trace_poly(sub_path_data)

    def _trace_route(self, route, threshold):
        path_data = route.the_geom_900913.simplify(threshold).coords
        self._trace_poly(path_data)

#    def _trace_features(self, route):
#        path_data = route.the_geom_900913.coords


    def _stroke_route(self, width, color):
        self.ctx.set_line_width(width)
        self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.ctx.set_source_rgb(*color)
        self.ctx.stroke()

    def draw_route(self, route, threshold=0.0):
        w, n, e, s = route.the_geom_900913.extent

        self.ctx.save()
        self._transform_to(w, n, e, s)
        self._trace_route(route, threshold)
        self.ctx.restore()

        self._stroke_route(10, (1, 0, 0))

    def draw_routes(self, routes, threshold=0.0):
        all_paths = routes[0].the_geom_900913
        for route in routes[1:]:
            all_paths = all_paths.union(route.the_geom_900913)
        w, n, e, s = all_paths.extent

        legend = {}

        for route in routes:
            self.ctx.save()
            self._transform_to(w, n, e, s)
            self._trace_route(route, threshold)
            self.ctx.restore()

            color = (random(), random(), random())
            self._stroke_route(10, color)

            legend[route.route] = "#%x%x%x" % color

        return legend
#
#            self.ctx.save()
#            self._transform_to(w, n, e, s)
#            self._trace_features(route)
#            self.ctx.restore()
#
#            self._stroke_route(2, (0,0,0))
