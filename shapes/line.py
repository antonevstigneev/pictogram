import random


class Line:
    def __init__(self, img_width, img_height):
        x0 = random.randint(0, int(img_width))
        y0 = random.randint(0, int(img_height))
        x1 = random.randint(0, int(img_width))
        y1 = random.randint(0, int(img_height))

        self.points = [
            (x0 + random.randint(-50, 50), y0 + random.randint(-50, 50)),
            (x1 + random.randint(-50, 50), y1 + random.randint(-50, 50))]

        self.width = random.randint(2, 20)

        self.color = (
            random.randint(0, 256),
            random.randint(0, 256),
            random.randint(0, 256),
            255
        )
        self._img_width = img_width
        self._img_height = img_height

    def mutate(self, sigma=1.0):
        mutations = ['shift', 'point', 'width', 'color', 'reset']
        weights = [30, 35, 35, 30, 5]

        mutation_type = random.choices(mutations, weights=weights, k=1)[0]

        if mutation_type == 'shift':
            x_shift = int(random.randint(-50, 50)*sigma)
            y_shift = int(random.randint(-50, 50)*sigma)
            self.points = [(x + x_shift, y + y_shift) for x, y in self.points]

        elif mutation_type == 'point':
            index = random.choice(list(range(len(self.points))))

            self.points[index] = (self.points[index][0] + int(random.randint(-50, 50) * sigma),
                                  self.points[index][1] + int(random.randint(-50, 50) * sigma),)

        elif mutation_type == 'width':
            self.width = self.width + int(random.randint(-2, 2) * sigma)

            # Ensure width is within correct range
            self.width = min(max(self.width, 2), 20)
            
        elif mutation_type == 'color':
            self.color = tuple(
                c + int(random.randint(-50, 50) * sigma) for c in self.color
            )
            self.color = tuple(
                min(max(c, 0), 255) for c in self.color
            )
            self.color = list(self.color) 
            self.color[-1] = 255
            self.color = tuple(self.color)
            
        else:
            new_line = Line(self._img_width, self._img_height)

            self.points = new_line.points
            self.color = new_line.color