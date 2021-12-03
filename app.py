import streamlit as st
import PIL
import random
from itertools import cycle
from evol import Evolution, Population
from utils.embedding import Embedding
from copy import deepcopy
from painting import Painting
from utils.palette import Palette


generatedResults = []
embedder = Embedding()
st.header('Pictogram')
st.caption('Abstract pictures from text')
st.markdown('##')
imagePreview = st.empty()


def score(x: Painting) -> float:
    """
    Calculate the distance to the text query
    :return: score based on similarity between query embedding and Painting embedding
    """

    current_image = x.draw().convert('RGB')
    query_embedding = embedder.text_embedding.cpu().data.numpy()
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



def print_summary(pop) -> Population:
    img = pop.current_best.chromosome.draw()
    imagePreview.image(img, width=320, caption=f"Current generation: {pop.generation}")
    next(cols).image(img, width=160, caption='')
    return pop


def generate_image(text_query):
    embedder.getTextEmbedding(text_query)

    num_shapes = {
        "ellipses": 3,
        "rectangles": 3,
        "lines": 3,
        "polygons": 3,
    }

    population_size = 50
    color_palettes = Palette(query_embedding=embedder.text_embedding).find_best_matches(topN=5)
    color_palette = random.choice(color_palettes)

    pop = Population(chromosomes=[Painting(num_shapes=num_shapes) for _ in range(population_size)],
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

    pop = pop.evolve(early_evo, n=15)
    pop = pop.evolve(mid_evo, n=30)
    pop = pop.evolve(late_evo, n=60)
    pop = pop.evolve(final_evo, n=100)


text_query = st.text_input('', 'an image of a flower')
button = st.button('Generate image')
cols = cycle(st.columns(4))

if button:
    generate_image(text_query)


hide_streamlit_style = """
<style>
body {background: #ffffff;}
img {padding-top: 32px;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)