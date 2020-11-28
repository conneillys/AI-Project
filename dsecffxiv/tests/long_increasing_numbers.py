"""
Test program for the genetic algorithm.

Problem:
    Find the highest scoring list of numbers that is length SIZE, where your score is based on the
    longest increasing number chain.

    Score like the following:
    if SIZE = 5

    1 2 3 4 5 => Score 4
    1 2 3 5 4 => Score 2
    5 4 3 2 1 => Score 0
    5 4 1 2 3 => Score 2
    5 5 5 5 5 => Score 0

    The domain of each entry is 0..=SIZE.
"""


from itertools import islice
from random import randint
from typing import List, Tuple

import matplotlib.pyplot as plt
from tqdm import tqdm

from dsecffxiv.algo.types import Domain, Individual, Population
from dsecffxiv.utils import chance


def generate_new_individual(domain: Domain, size: int) -> Individual:
    """Generate a random new Individual of the give size and domain."""
    indiv = list()  # List of action from domain
    for _ in range(0, size):
        indiv.append(new_value_from_domain(domain))
    return Individual(indiv)


def generate_new_population(population_size: int, domain: Domain, size: int) -> Population:
    """Generate a new population give a population size, domain, and individual size."""
    new_population = list()
    for _ in range(0, population_size):
        new_population.append(
            generate_new_individual(domain, size))
    return new_population


def new_value_from_domain(domain: Domain):
    """Generate a new key value randomly from the domain."""
    return domain[randint(0, len(domain)-1)]


def mutate_individual(indiv: Individual, domain: Domain) -> None:
    """Give an individual, mutate one gene."""
    mutate_position = randint(0, len(indiv.value)-1)
    indiv.value[mutate_position] = new_value_from_domain(domain)


def sort_population_by_score(input_population: Population) -> None:
    """Sort the given population using the score, from highest to lowest."""
    input_population.sort(key=score_individual, reverse=True)


def select_individuals(input_population: Population, select_pairs: int) -> List[Tuple[Individual, Individual]]:
    """Given a population, return a subset of the population to be used for breeding."""
    iterator = iter(input_population)
    result_collection = list()
    for _ in range(0, select_pairs):
        select_slice = islice(iterator, 2)
        result_collection.append((next(select_slice), next(select_slice)))
    return result_collection


def crossover_individuals(selection: List[Tuple[Individual, Individual]]) -> Population:
    """Given a list of pairs of individuals, cross them over."""
    result_collection = list()
    for each in selection:
        _new_left, _new_right = crossover_individual_pairs(each[0], each[1])
        result_collection.append(_new_left)
        result_collection.append(_new_right)
    return result_collection


def crossover_individual_pairs(_left: Individual, _right: Individual) -> Tuple[Individual, Individual]:
    """Give two individuals, merge them into children."""
    left_slice_point = (len(_left.value)//2)
    left_first = _left.value[slice(0, left_slice_point)]
    left_last = _left.value[slice(left_slice_point, len(_left.value))]

    right_slice_point = (len(_right.value)//2)
    right_first = _right.value[slice(0, right_slice_point)]
    right_last = _right.value[slice(right_slice_point, len(_right.value))]

    _new_left = Individual(left_first + right_last)
    _new_right = Individual(right_first + left_last)
    return (_new_left, _new_right)


def score_individual(indiv: Individual) -> int:
    """Score a given individual."""
    max_score = 0
    # Select start values
    for each_start in range(0, len(indiv.value) - 1):
        score = 0
        for each in range(each_start, len(indiv.value) - 1):
            if indiv.value[each] + 1 == indiv.value[each+1]:
                score = score + 1
            else:
                break
        if score > max_score:
            max_score = score
    return max_score


def print_individual_score_mapping(input_population: Population) -> None:
    """Given a population, score and print the pop->Score mapping."""
    for each in input_population:
        print("{0} -> {1}".format(str(each), score_individual(each)))


def cull_population(input_population: Population, size: int):
    """Slice the population down to a given size."""
    new_population = input_population[slice(0, size)]
    return new_population


def show_stats(input_population_history: List[Population]) -> None:
    """Show some stats about the population to the user."""
    stat_min = list()
    stat_max = list()

    for generation_pop in tqdm(input_population_history, desc='Generating Stats'):
        stat_min.append(score_individual(generation_pop[-1]))
        stat_max.append(score_individual(generation_pop[0]))

    stat_generation_max = list(range(0, len(stat_max)))
    stat_generation_min = list(range(0, len(stat_min)))

    plt.plot(stat_generation_max, stat_max, label='Max Score')
    plt.plot(stat_generation_min, stat_min, label='Min Score')

    plt.xlabel('Generation')
    plt.ylabel('Score')

    plt.title('Min/Max Score vs Generation')
    plt.legend()
    plt.show()


def print_leaderboard(leaderboard_pop: Population, size=5) -> None:
    """Print top n scoring individuals from the population."""
    print_individual_score_mapping(leaderboard_pop[slice(0, size)])


def crossover_n_point(parents: Tuple[Individual, Individual], crossover_points: int) -> Tuple[Individual, Individual]:
    """Splice together two parents to make two children using n point crossover."""
    _left, _right = parents
    size = len(_left.value)
    points = list()
    for _ in range(crossover_points):
        new_point = randint(0, size)
        while new_point in points:
            new_point = randint(0, size)
        points.append(new_point)
    points.sort()

    _new_left, _new_right = list(), list()
    pick_direction = False

    for i in range(size):
        if i in points:
            pick_direction = not pick_direction

        if pick_direction:
            _new_left.append(_left.value[i])
            _new_right.append(_right.value[i])
        else:
            _new_left.append(_right.value[i])
            _new_right.append(_left.value[i])

    return (Individual(_new_left), Individual(_new_right))


def selection_tournament(_population: Population, tournament_size: int) -> Individual:
    """Tournament select an individual from the population."""
    tournament_pool = list()

    for _ in range(tournament_size):
        # ? Should we allow duplicates in the selection pool?
        tournament_pool.append(_population[randint(0, len(_population)-1)])

    sort_population_by_score(tournament_pool)
    return tournament_pool[0]


def mutate_each(_indiv: Individual, percent_chance: float, domain: Domain):
    """Iterate over all values in the indiv and possibly mutate them."""
    for i in range(len(_indiv.value)):
        if chance(percent_chance):
            _indiv.value[i] = new_value_from_domain(domain)


if __name__ == "__main__":
    POPULATION_SIZE = 500
    GENERATION_LIMIT = 100000
    SIZE = 100
    DOMAIN = list(range(1, SIZE+1))
    SELECTION_PAIR_SIZE = 10
    TOURNAMENT_SIZE = 50
    MUTATION_CHANCE = 0.005

    # Generation initial population
    population = generate_new_population(POPULATION_SIZE, DOMAIN, SIZE)

    # Historical Stats
    population_history = list()

    # print_individual_score_mapping(population)

    try:
        for generation in tqdm(range(0, GENERATION_LIMIT + 1), unit='Generation', desc='Simulating'):
            sort_population_by_score(population)
            population = cull_population(
                population, POPULATION_SIZE)

            population_history.append(population)

            children = list()
            for selection_pair in range(SELECTION_PAIR_SIZE):
                left = selection_tournament(population, TOURNAMENT_SIZE)
                right = selection_tournament(population, TOURNAMENT_SIZE)

                new_left, new_right = crossover_n_point((left, right), 5)

                mutate_each(new_left, MUTATION_CHANCE, DOMAIN)
                mutate_each(new_right, MUTATION_CHANCE, DOMAIN)

                children.append(new_left)
                children.append(new_right)
            population = population + children
            # selected_population = select_individuals(
            #     culled_population, SELECTION_PAIR_SIZE)

            # crossed_over_population = crossover_individuals(
            #     selected_population)

            # for each_indiv in crossed_over_population:
            #     if chance(MUTATION_CHANCE):
            #         mutate_individual(each_indiv, DOMAIN)

            # population = culled_population + crossed_over_population
    except KeyboardInterrupt:
        pass

    # Show stats at the end of a run
    show_stats(population_history)

    # for each in crossed_over_population:
    #     print("Crossover: {0}".format(str(each)))
