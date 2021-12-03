import random
import os
import argparse
from evol import Evolution, Population
from utils.embedding import Embedding
from copy import deepcopy
from painting import Painting
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'


parser = argparse.ArgumentParser()
parser.add_argument("--query", help="type a query to generate image.",
                    type=str, required=True)
parser.add_argument("--population", help="population number.",
                    type=int, default=50)
parser.add_argument("--rectangles", help="number of rectangles.",
                    type=int, default=5)
parser.add_argument("--triangles", help="number of triangles.",
                    type=int, default=5)
parser.add_argument("--ellipses", help="number of ellipses.",
                    type=int, default=5)
parser.add_argument("--lines", help="number of lines.",
                    type=int, default=5)
parser.add_argument("--polygons", help="number of polygons.",
                    type=int, default=5)
args = parser.parse_args()


embedder = Embedding()

def score(x: Painting) -> float:
    """
    Calculate the distance to the text query
    :return: score based on similarity between query embedding and Painting embedding
    """

    current_image = x.draw().convert('RGB')
    query_embedding = embedder.query_embedding.cpu().data.numpy()
    current_embedding = embedder.getImageEmbedding(current_image).cpu().data.numpy()

    score = 100 - (100.0 * current_embedding @ query_embedding.T)

    return score


def pick_best_and_random(pop, maximize=False):
    evaluated_individuals = tuple(filter(lambda x: x.fitness is not None, pop))
    if len(evaluated_individuals) > 0:
        mom = max(evaluated_individuals, key=lambda x: x.fitness if maximize else -x.fitness)
    else:
        mom = random.choice(pop)
    dad = random.choice(pop)
    return mom, dad


def pick_random(pop):
    mom = random.choice(pop)
    dad = random.choice(pop)
    return mom, dad


def mutate_painting(x: Painting, rate=0.04, swap=0.5, sigma=1) -> Painting:
    x.mutate_shapes(rate=rate, swap=swap, sigma=sigma)
    return deepcopy(x)


def mate(mom: Painting, dad: Painting):
    child_a, child_b = Painting.mate(mom, dad)

    return deepcopy(child_a)


def print_summary(pop, img_template="output%d.png", results_path="output") -> Population:
    avg_fitness = sum([i.fitness for i in pop.individuals])/len(pop.individuals)

    print("\nCurrent generation %d, best score %f, pop. avg. %f " % (pop.generation,
                                                                     pop.current_best.fitness,
                                                                     avg_fitness))

    img = pop.current_best.chromosome.draw()
    # img.save(img_template % pop.generation, 'PNG')

    return pop


def generate_image(text_query):
    embedder.getTextEmbedding(text_query)

    num_shapes = {
      "triangles": 5,
      "ellipses": 5,
      "rectangles": 5,
      "lines": 5,
      "polygons": 5,
    }

    population_size = 50

    pop = Population(chromosomes=[Painting(num_shapes, background_color=(0, 0, 0)) for _ in range(population_size)],
                     eval_function=score, maximize=False)

    early_evo = (Evolution()
                 .survive(fraction=0.15)
                 .breed(parent_picker=pick_random, combiner=mate, population_size=population_size)
                 .mutate(mutate_function=mutate_painting, rate=0.75, swap=0.75)
                 .evaluate(lazy=False)
                 .apply(print_summary))

    mid_evo = (Evolution()
               .survive(fraction=0.10)
               .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
               .mutate(mutate_function=mutate_painting, rate=0.50, swap=0.50)
               .evaluate(lazy=False)
               .apply(print_summary))

    late_evo = (Evolution()
                .survive(fraction=0.05)
                .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
                .mutate(mutate_function=mutate_painting, rate=0.25, swap=0.25)
                .evaluate(lazy=False)
                .apply(print_summary))

    final_evo = (Evolution()
                 .survive(fraction=0.025)
                 .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
                 .mutate(mutate_function=mutate_painting, rate=0.15, swap=0, sigma=0.15)
                 .evaluate(lazy=False)
                 .apply(print_summary))

    pop = pop.evolve(early_evo, n=20)
    pop = pop.evolve(mid_evo, n=40)
    pop = pop.evolve(late_evo, n=80)
    pop = pop.evolve(final_evo, n=120)



# if __name__ == "__main__":
#     results_path = f'./output/'

#     timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
#     output_folder = results_path + f'{timestamp}'
#     os.makedirs(output_folder)

#     image_template = os.path.join(output_folder, "drawing_%05d.png")

#     num_shapes = {
#       "triangles": args.triangles,
#       "ellipses": args.ellipses,
#       "rectangles": args.rectangles,
#       "lines": args.lines,
#       "polylines": args.polylines,
#     }

#     population_size = args.population

#     embedder = Embedding(query=args.query)
#     print('Starting to generate an image...')
#     print(f'Text query: {args.query}')
#     query_embedding = embedder.query_embedding

#     pop = Population(chromosomes=[Painting(num_shapes, background_color=(0, 0, 0)) for _ in range(population_size)],
#                      eval_function=score, maximize=False)

#     early_evo = (Evolution()
#                  .survive(fraction=0.15)
#                  .breed(parent_picker=pick_random, combiner=mate, population_size=population_size)
#                  .mutate(mutate_function=mutate_painting, rate=0.75, swap=0.75)
#                  .evaluate(lazy=False)
#                  .apply(print_summary,
#                         img_template=image_template,
#                         results_path=results_path))

#     mid_evo = (Evolution()
#                .survive(fraction=0.10)
#                .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
#                .mutate(mutate_function=mutate_painting, rate=0.50, swap=0.50)
#                .evaluate(lazy=False)
#                .apply(print_summary,
#                       img_template=image_template,
#                       results_path=results_path))

#     late_evo = (Evolution()
#                 .survive(fraction=0.05)
#                 .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
#                 .mutate(mutate_function=mutate_painting, rate=0.25, swap=0.25)
#                 .evaluate(lazy=False)
#                 .apply(print_summary,
#                        img_template=image_template,
#                        results_path=results_path))

#     final_evo = (Evolution()
#                  .survive(fraction=0.025)
#                  .breed(parent_picker=pick_best_and_random, combiner=mate, population_size=population_size)
#                  .mutate(mutate_function=mutate_painting, rate=0.15, swap=0, sigma=0.15)
#                  .evaluate(lazy=False)
#                  .apply(print_summary,
#                         img_template=image_template,
#                         results_path=results_path))

#     pop = pop.evolve(early_evo, n=20)
#     pop = pop.evolve(mid_evo, n=40)
#     pop = pop.evolve(late_evo, n=80)
#     pop = pop.evolve(final_evo, n=120)
