import random
import math


def generatePolygonPoints(cX, cY, radius, irregularity, spikeyness, vertices):
    '''Start with the centre of the polygon at cX, cY, 
    then creates the polygon by sampling points on a circle around the centre. 
    Randon noise is added by varying the angular spacing between sequential points,
    and by varying the radial distance of each point from the centre.

    Params:
    cX, cY - coordinates of the "centre" of the polygon
    radius - in px, the average radius of this polygon, this roughly controls how large the polygon is, really only useful for order of magnitude.
    irregularity - [0,1] indicating how much variance there is in the angular spacing of vertices. [0,1] will map to [0, 2pi/numberOfVerts]
    spikeyness - [0,1] indicating how much variance there is in each vertex from the circle of radius radius. [0,1] will map to [0, radius]
    vertices - self-explanatory

    Returns a list of vertices, in CCW order.
    '''
    irregularity = clip( irregularity, 0,1 ) * 2 * math.pi / vertices
    spikeyness = clip( spikeyness, 0,1 ) * radius

    # generate n angle steps
    angleSteps = []
    lower = (2*math.pi / vertices) - irregularity
    upper = (2*math.pi / vertices) + irregularity
    sum = 0
    for i in range(vertices) :
        tmp = random.uniform(lower, upper)
        angleSteps.append( tmp )
        sum = sum + tmp

    # normalize the steps so that point 0 and point n+1 are the same
    k = sum / (2 * math.pi)
    for i in range(vertices) :
        angleSteps[i] = angleSteps[i] / k

    # now generate the points
    points = []
    angle = random.uniform(0, 2 * math.pi)
    for i in range(vertices) :
        r_i = clip( random.gauss(radius, spikeyness), 0, 2 * radius )
        x = cX + r_i*math.cos(angle)
        y = cY + r_i*math.sin(angle)
        points.append( (int(x),int(y)) )

        angle = angle + angleSteps[i]

    return points

def clip(x, min, max) :
    if( min > max ) :  return x    
    elif( x < min ) :  return min
    elif( x > max ) :  return max
    else :             return x


class Polygon:
    def __init__(self, img_width, img_height):
        self.color = (
            random.randint(0, 256),
            random.randint(0, 256),
            random.randint(0, 256),
            255
        )
        self._img_width = img_width
        self._img_height = img_height
        self.points = self.getPolygonPoints()
        self.width = random.randint(2, 8)

    def getPolygonPoints(self): 
      padding = 64
      cX = random.randint(padding, int(self._img_width) - padding)
      cY = random.randint(padding, int(self._img_height) - padding)
      points = generatePolygonPoints(cX = cX, 
                                     cY = cY, 
                                     radius = random.randint(20, 120), 
                                     irregularity = random.uniform(0, 1),
                                     spikeyness = random.uniform(0, 1),
                                     vertices = random.randint(4, 12))
      return points

    def mutate(self, sigma=1.0):
        mutations = ['shift', 'point', 'color', 'reset']
        weights = [30, 35, 30, 5]

        mutation_type = random.choices(mutations, weights=weights, k=1)[0]

        if mutation_type == 'shift':
            x_shift = int(random.randint(-50, 50)*sigma)
            y_shift = int(random.randint(-50, 50)*sigma)
            self.points = [(x + x_shift, y + y_shift) for x, y in self.points]

        elif mutation_type == 'point':
            index = random.choice(list(range(len(self.points))))

            self.points[index] = (self.points[index][0] + int(random.randint(-50, 50) * sigma),
                                  self.points[index][1] + int(random.randint(-50, 50) * sigma),)    
                                  
        elif mutation_type == 'color':
            self.color = tuple(
                c + int(random.randint(-50, 50) * sigma) for c in self.color
            )

            # Ensure color is within correct range
            self.color = tuple(
                min(max(c, 0), 255) for c in self.color
            )
            self.color = list(self.color) 
            self.color[-1] = 255
            self.color = tuple(self.color)

        else:
            new_polygon = Polygon(self._img_width, self._img_height)

            self.points = new_polygon.points
            self.color = new_polygon.color