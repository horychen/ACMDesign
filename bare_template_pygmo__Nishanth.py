import pygmo as pg
from pylab import np, plt

class acm_designer(object):
    def __init__(self):
        self.bounds_denorm = [  [10.499999999999998, 27.0], 
                                [0.5, 5], 
                                [35.469240724123004, 53.203861086184496], 
                                [112.5, 135.0], 
                                [12.942477796076938, 19.413716694115404], 
                                [3, 6], 
                                [2.5, 7], 
                                [27.0, 45.0], 
                                [18.0, 21.9375], 
                                [9.100179700366597, 13.650269550549895], 
                                [38.197186342054884, 57.29577951308233], 
                                [2.5, 6], 
                                [2.5, 6] ]
        self.counter_fitness_called = 0
        self.counter_fitness_return = 0

    def evaluate_design(self, x_denorm):
        # modify this function to call matlab and eMach to evaluate the design with free variables as in x_denorm
        return x_denorm[0], x_denorm[1], x_denorm[2]

class Problem_BearinglessSynchronousDesign(object):

    # Define objectives
    def fitness(self, x):
        global ad

        if ad.counter_fitness_called == ad.counter_fitness_return:
            ad.counter_fitness_called += 1
        else:
            # This should not be reachable
            raise Exception('ad.counter_fitness_called')
        print('Call fitness: %d, %d'%(ad.counter_fitness_called, ad.counter_fitness_return))

        x_denorm = x

        try:
            # evaluate x_denorm via FEA tools
            f1, f2, f3 = ad.evaluate_design(x_denorm)

        except KeyboardInterrupt as error:
            raise error

        except Exception as error:
            # deal with exceptions
            pass

            # debug
            raise error

            # or discard this individual
            f1, f2, f3 = get_bad_fintess_values(machine_type='PMSM')
            print(str(error))
            # logger = logging.getLogger(__name__)
            # logger.error(str(error))

        else:
            # - Price
            f1 
            # - Efficiency @ Rated Power
            f2 
            # Ripple Performance (Weighted Sum)
            f3 
            print('f1,f2,f3:',f1,f2,f3)

            # Apply constraints here or you can pygmo's constraint feature
            pass 

        ad.counter_fitness_return += 1
        print('Fitness called: %d, %d\n----------------'%(ad.counter_fitness_called, ad.counter_fitness_return))
        # raise KeyboardInterrupt
        return [f1, f2, f3]

    # Return number of objectives
    def get_nobj(self):
        return 3

    # Return bounds of decision variables (a.k.a. chromosome)
    def get_bounds(self):
        global ad
        print('get_bounds:', ad.bounds_denorm)
        min_b, max_b = np.asarray(ad.bounds_denorm).T 
        return ( min_b.tolist(), max_b.tolist() )

    # Return function name
    def get_name(self):
        return "Bearingless PMSM Design"

#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# Multi-Objective Optimization
#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
if __name__ == '__main__':

    global ad
    ad = acm_designer()

    ################################################################
    # MOO Step 1:
    #   Create UserDefinedProblem and create population
    #   The magic method __init__ cannot be defined for UDP class
    ################################################################
    udp = Problem_BearinglessSynchronousDesign()
    prob = pg.problem(udp)
    print(prob)

    popsize = 78
    print('-'*40 + '\nPop size is', popsize)

    ################################################################
    # MOO Step 2:
    #   Select algorithm (another option is pg.nsga2())
    ################################################################
    # Don't forget to change neighbours to be below popsize (default is 20) decomposition="bi"
    algo = pg.algorithm(pg.moead(gen=1, weight_generation="grid", decomposition="tchebycheff", 
                                 neighbours=20, 
                                 CR=1, F=0.5, eta_m=20, 
                                 realb=0.9, 
                                 limit=2, preserve_diversity=True)) # https://esa.github.io/pagmo2/docs/python/algorithms/py_algorithms.html#pygmo.moead
    print('-'*40, '\n', algo)

    ################################################################
    # MOO Step 3:
    #   Begin optimization
    ################################################################

    # initialization (will call fitness for popsize times to get an initial population)
    pop = pg.population(prob, size=popsize) 

    number_of_finished_iterations = 0
    number_of_iterations = 10
    # logger = logging.getLogger(__name__)

    for _ in range(number_of_finished_iterations, number_of_iterations):
        msg = 'This is iteration #%d. '%(_)
        print(msg)
        # logger.info(msg)
        pop = algo.evolve(pop)

    # print(pop)
    # this shows you the Pareto front plot using f1 versus f2.
    ax = pg.plot_non_dominated_fronts(pop.get_f())
    plt.show()


