import numpy as np
from scipy.integrate import simps
# from decimal import Decimal
# Based on code from V. Martinetto 
# Written, and packaged by Anthony R. Osborne


def atomic_potentials(Z: int = 1, x: np.ndarray = None, d: float = 0.0, potential_type: int = 1):
    """
    INPUT: 
        Z: int, atomic number
        x: ndarray, grid to evaluate on.
        d: float, spacing parameter for diatomic systems.
        potential_type: int, select either monatomic or diatomic system. Currently only those two are supported.
    
    Returns: 
        potential: ndarray, either monatomic or diatomic potential evaluated on the grid. 
    
    Raises: 
        NotImplementedError: Only raised when requesting a potential that is not monatomic or diatomic.
    """
    
    if potential_type ==1 : 
        potential = -Z/(np.abs(x)+.5)
    elif potential_type == 2:
        potential = -Z/(abs(x + 0.5*d) + 1.0) -Z/(abs(x - 0.5*d) + 1.0)
    else: 
        raise NotImplementedError("Only monatomic or diatomic molecules are currently supported")
    return potential

## Occupation functions
### Spin String function
def occ_string(N):
    """
    Function to write an up/down spin string
    """
    occ_string = ''
    for i in range(N):
        i+=1
        if i%2==0:
            occ_string += 'd'
        else:
            occ_string += 'u'
    return occ_string

def occupier(Ei: np.ndarray = None, mu: float= 0, tau: float=0, N: int=1, occupation_type: int = 0):
    """
    INPUT: 
        Ei: ndarray, eignevalues
        mu: float, chemical potential
        tau: float, electronic temperature
        N: int, particle number
        occupation_type: int, dictates which occupation scheme is used. Only  Fermi-like or Boltzman occupations are available. 

    Returns: 
        occupations: Either Boltzman or Fermi-like occupations
        
    Raises: 
        NotImplementedError: only rasied if occupation_type is not 1 or 2
    """

    if occupation_type == 1: 
        # do Fermi occupations
        occupation = 1/(1+np.exp((Ei-mu)/tau))
    elif occupation_type == 2: 
        # do Boltzman occupations
        kb = 3.166811563e-6 # Boltzman constant in Hartrees
        beta = 1/kb*tau # beta 
        nstates = len(Ei) # number of states 
        w = np.empty((nstates,N))
        partition_function = 0 
        for i in range(nstates): 
            for j in range(N):
                w[j,i] = np.exp(-beta*(Ei[i]-(mu*j)))
                partition_function += w[j,i]
        #renormalize boltzman weights
        w = w/partition_function
        occupation = w
    else: 
        raise NotImplementedError("Only Boltzman or Fermi-like occupations are currently supported")
    return occupation
## Root finding tools

def secant_method(function, guess1:float = 0, guess2:float = 0, criterion: float = 1e-6, max_iter: float = 100, print_opt:float = 0):
    """
    INPUT: 
        function : function, function of which to find the roots 
        guess1 : float, lower guess for the root
        guess2 : float, lower guess for the root
        criterion : float, convergence criterion for the root finding method
        max_iter : float, maximum number of iterations for the root finding method
    Returns: 
        root : float, The root of the function 
    Raises: 
        Excpetion: Divide by zero warning if guess1 and guess2 are equal
    """

    x1, x2 = guess1, guess2
    if abs(x1-x2) == 0:
        raise Exception("Warning you are inadvertently trying to divide by zero, the lower and upper guesses are the same value")
    
    fx1 = function(x1)
    fx2 = function(x2)
    error = 1
    iteration = 0
    
    while abs(error) > criterion:
        numerator = x2 - x1
        denominator = fx2 - fx1
        root = x2 - fx2 * (numerator/denominator)
        fx1 = fx2  
        x1 = x2   
        x2 = root  
        fx2 = function(x2)  
        
        error = abs(x2 - x1)  
        iteration += 1
        
        if print_opt == 1:
            print(f'For iteration number {iteration}, the value of x is {x2}')
            print(f'The error estimate is {error}')
        if iteration > max_iter:
            break
    return x2, function(x2)
## Particle number tools

### Fermi weight functions

#### Function to calculate density
def density_weighter(init_dens: np.ndarray = None, dens_type: int=0, Ei: np.ndarray = None, mu: float= 0, tau: float=0, N: int=1):
    """
    INPUT: 
        init_dens: ndarray, density to be weighted
        density_type: int, dictates which occupation scheme is used. Only Boltzman and Fermi-like are available. 
    Returns: 
        density: Density weighted with either Boltzman or Fermi-like occupations
        
    Raises: 
        NotImplementedError: only rasied if density_type is not Fermi-like or Boltzman weighted
    """
    if dens_type == 1: 
        density = occupier(Ei, mu, tau, N, 1)*init_dens
    elif dens_type == 2: 
        density = occupier(Ei, mu, tau, N, 2)*init_dens
    else: 
        raise NotImplementedError("Only densities weighted by Fermi-like or Boltzman occupations are currently supported ")
    return density

def particle_number(denisty:np.ndarray = None, x:np.ndarray= None):
    """
    INPUT: 
        densty : ndarray, density for integration
        x : ndarray, grid to integrate on
    Returns: 
        particle_number : float, The number of particles 
    Raises: 
        Error: condition
    """
    particle_number = simps(denisty, x)
    return particle_number

### Function to calculate number of particles for a given mu and tau (shifted)
def particle_number_shifter_function(init_dens: np.ndarray = None, dens_type: int=0, Ei: np.ndarray = None, tau: float=0, N: int=1, x:np.ndarray= None, target_Ne: int = 0):
    """
    INPUT: 
        densty : ndarray, density for integration
        x : ndarray, grid to integrate on
    Returns: 
        particle_number : float, The number of particles 
    Raises: 
        Error: condition
    """
    def particle_number_shift(mu):
        denisty = density_weighter(init_dens, dens_type, Ei, mu, tau, N)
        Ne = simps(denisty, x)
        return Ne - target_Ne
    return particle_number_shift
## Chemical potential calculation functions

### Search function to search over a range of \tau that returns \mu for each \tau such that a number of particles is conserved
def tau_search(taus:np.ndarray = None, guess1:float = 0, guess2:float = 0, vals:np.ndarray = None, x:np.ndarray = None, N:int = 0, occupation_type: int = 0, criterion:float = 1e-10, target_N:float = 2):
    """
    INPUT: 
        taus : ndarray, array of electronic temperatures
        guess1 : float, lower guess for mu
        guess2 : float, lower guess for mu
        vals : ndarray, array of eigenvalues
        x : ndarray, grid to evaluate the function on
        N : int, number of particles
        occupation_type : int, dictates whether Fermi-like or Boltzman occupations are used
        target_N : int, the target number of electrons
        criterion : float, convergence criterion for the root finding method
    Returns: 
        mu_array : ndarray, The value of mu at each tau such that particle number is conserved. 
    """
        
    dtau = taus[1]-taus[0]
    mu_array = np.empty((len(taus)))
    mu0 = guess1
    mu1 = guess2
    for i, tau in enumerate(taus):
        func = particle_number_shifter_function(tau, occupation_type, vals, tau, N, x, target_N)
        mu1, fx0 = secant_method(func, mu0, mu1, criterion)

        mu_array[i] = mu1

        mu0 = mu1-(dtau+(0.1*dtau*i))

    return mu_array