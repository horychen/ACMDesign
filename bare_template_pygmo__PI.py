import pygmo as pg
from pylab import np, plt

import subprocess
import time
import os
work_dir = os.path.dirname(os.path.realpath(__file__))
class acm_designer(object):
    def __init__(self):
        self.bounds_denorm = [  [100, 1000], # BW-current
                                [1.1, 5] ] # delta
        self.counter_fitness_called = 0
        self.counter_fitness_return = 0

    def evaluate_design(self, x_denorm):

        with open('_eval/ACMConfig.h', 'r') as f:
            new_line = []
            for line in f.readlines():
                if '#define CURRENT_LOOP_BANDWIDTH' in line:
                    new_line.append(f'#define CURRENT_LOOP_BANDWIDTH (2*M_PI*{x_denorm[0]:g})\n') # 15
                elif '#define DELTA_THE_DAMPING_FACTOR' in line:
                    new_line.append(f'#define DELTA_THE_DAMPING_FACTOR ({x_denorm[1]:g})\n') # 0.08
                else:
                    new_line.append(line)
        with open('_eval/ACMConfig.h', 'w') as f:
            f.writelines(new_line)

        if os.path.exists(work_dir+'/_eval/main.exe'):
            os.remove(work_dir+'/_eval/main.exe')
        subprocess.run( ["gcc", "_eval/main.c", "_eval/controller.c", "_eval/observer.c", "-o", "_eval/main"] )
        while not os.path.exists(work_dir+'/_eval/main.exe'):
            time.sleep(0.1)
            print('sleep for main.exe')

        # subprocess.run( [work_dir+'/_eval/main.exe'] )
        os.system('cd _eval && main')
        while not os.path.exists(work_dir+'/_eval/pi_opti.dat'):
            time.sleep(0.1)
            print('sleep for .dat')

        speed_profile = np.loadtxt('_eval/pi_opti.dat', skiprows=1)
        os.remove(work_dir+'/_eval/pi_opti.dat')

        TS = 0.000025 # ACMConfig.h
        print( max(speed_profile), 'rpm' )
        print( min(speed_profile, key=lambda x:abs(x-90)), 'rpm' ) # [rpm]
        print( np.abs(speed_profile-90).argmin() * TS * 1000, 'ms' ) # [ms]

        rise_time = np.abs(speed_profile-90).argmin() * TS * 1000

        over_shoot = max(speed_profile)
        if over_shoot<=100:
            over_shoot = 100

        # modify this function to call matlab and eMach to evaluate the design with free variables as in x_denorm
        return over_shoot, rise_time

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

        # evaluate x_denorm via FEA tools
        f1, f2 = ad.evaluate_design(x_denorm)

        ad.counter_fitness_return += 1
        print('Fitness called: %d, %d\n----------------'%(ad.counter_fitness_called, ad.counter_fitness_return))
        # raise KeyboardInterrupt
        return [f1, f2]

    # Return number of objectives
    def get_nobj(self):
        return 2

    # Return bounds of decision variables (a.k.a. chromosome)
    def get_bounds(self):
        global ad
        print('get_bounds:', ad.bounds_denorm)
        min_b, max_b = np.asarray(ad.bounds_denorm).T 
        return ( min_b.tolist(), max_b.tolist() )

    # Return function name
    def get_name(self):
        return "Current loop PI"

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
    number_of_iterations = 2
    # logger = logging.getLogger(__name__)

    for _ in range(number_of_finished_iterations, number_of_iterations):
        msg = 'This is iteration #%d. '%(_)
        print(msg)
        # logger.info(msg)
        pop = algo.evolve(pop)

    # print(pop)
    # this shows you the Pareto front plot using f1 versus f2.
    ax = pg.plot_non_dominated_fronts(pop.get_f())
    print(pop.get_x())

    import utility_json
    utility_json.to_json_recursively(pop, 'pop_PI.json')

    plt.show()
