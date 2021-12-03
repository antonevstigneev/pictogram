from shapes.ellipse import Ellipse
from shapes.rectangle import Rectangle
from shapes.line import Line
from shapes.polygon import Polygon
from random import shuffle, randint
from PIL import Image, ImageDraw
import random


class Painting:
    def __init__(self, num_shapes, background_color=(255, 255, 255)):
        self._img_width = 256
        self._img_height = 256
        self.num_shapes = num_shapes
        self.ellipses = [Ellipse(self._img_width, self._img_height) for _ in range(num_shapes['ellipses'])]
        self.rectangles = [Rectangle(self._img_width, self._img_height) for _ in range(num_shapes['rectangles'])]
        self.lines = [Line(self._img_width, self._img_height) for _ in range(num_shapes['lines'])]
        self.polygons = [Polygon(self._img_width, self._img_height) for _ in range(num_shapes['polygons'])]
        self.shapes = [self.ellipses, self.rectangles, self.lines, self.polygons]
        self._background_color = (*background_color, 255)

    @property
    def get_background_color(self):
        return self._background_color[:3]

    @property
    def get_img_width(self):
        return self._img_width

    @property
    def get_img_height(self):
        return self._img_height

    def mutate_shapes(self, rate=0.05, swap=0.5, sigma=1.0):
        for shape in self.shapes:
            total_mutations = int(rate * len(shape))
            random_indices = list(range(len(shape)))
            shuffle(random_indices)

            for i in range(total_mutations):
                index = random_indices[i]
                shape[index].mutate(sigma=sigma)

            if random.random() < swap:
                shuffle(random_indices)
                shape[random_indices[0]], shape[random_indices[1]] = shape[random_indices[1]], shape[random_indices[0]]


    def draw(self, scale=4) -> Image:
        image = Image.new("RGBA", (self._img_width*scale, self._img_height*scale))
        draw = ImageDraw.Draw(image)

        if not hasattr(self, '_background_color'):
            self._background_color = (255, 255, 255, 255)

        draw.polygon([(0, 0), (0, self._img_height*scale), (self._img_width*scale, self._img_height*scale), (self._img_width*scale, 0)],
                     fill=self._background_color)

        for shape in self.shapes:
            for s in shape:
                new_s = Image.new("RGBA", (self._img_width*scale, self._img_height*scale))
                s_draw = ImageDraw.Draw(new_s)

                if shape == self.polygons:
                    s_draw.polygon([(x*scale, y*scale) for x, y in s.points], fill=s.color)
                elif shape == self.rectangles:
                    s_draw.rectangle([(x*scale, y*scale) for x, y in s.points], fill=s.color)
                elif shape == self.ellipses:
                    s_draw.ellipse([(x*scale, y*scale) for x, y in s.points], fill=s.color)
                elif shape == self.lines:
                    s_draw.line([(x*scale, y*scale) for x, y in s.points], fill=s.color, width=s.width)

                image = Image.alpha_composite(image, new_s)

        return image

    @staticmethod
    def mate(a, b):
        ab = a.get_background_color
        bb = b.get_background_color
        new_background = (int((ab[i] + bb[i]) / 2) for i in range(3))

        num_shapes_init = {n: 0 for n in a.num_shapes}

        child_a = Painting(num_shapes_init, background_color=new_background)
        child_b = Painting(num_shapes_init, background_color=new_background)

        for i in range(len(a.shapes)):
            for a_shape, b_shape in zip(a.shapes[i], b.shapes[i]):
                if randint(0, 1) == 0:
                    child_a.shapes[i].append(a_shape)
                    child_b.shapes[i].append(b_shape)
                else:
                    child_a.shapes[i].append(b_shape)
                    child_b.shapes[i].append(a_shape)

        return child_a, child_b
        

