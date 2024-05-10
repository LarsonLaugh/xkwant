import bisect
import kwant
import kwant.kpm
import numpy as np
from scipy.integrate import cumtrapz

# __all__ = ['energy_to_density','density_to_energy','get_idos','get_idos_kpm']

def find_position(sorted_list,x):
    index = bisect.bisect_left(sorted_list,x)
    if index != len(sorted_list):
        return index
    return -1

def energy_to_density(idos,energies,energy):
    index = find_position(energies,energy)
    if index == -1:
        raise ValueError("need more eigenstates")
    return idos[index]

def density_to_energy(idos,energies,density):
    index = find_position(idos,density)
    if index == -1:
        raise ValueError("need more eigenstates")
    return energies[index]

def get_idos(syst,energy_range,use_kpm=True):
    """
    Calculate the integrated density of states (IDOS) for a given system over a specified energy range.

    Parameters:
    - system: A Kwant system (kwant.Builder).
    - energy_range: An array of energy values.

    Returns:
    - idos: Integrated density of states.
    - energy_range: The energy range used for the calculation.
    """
    if use_kpm:
        energy_resolution = (max(energy_range)-min(energy_range))*5/len(energy_range)
        dos, energies = get_dos_kpm(syst,energy_resolution)
        idos = cumtrapz(dos,energies,initial=0)
        energy_range = np.array(energy_range)
        energy_range = energies[(energies>=min(energy_range))&(energies<=max(energy_range))] # the energies here should include all possible eigenvalue of energy
        lowest_index = find_position(energies,min(energy_range))
        idos= idos[lowest_index : lowest_index+len(energy_range)] # This ensure the returned idos and energy_range have the same length
    else:
        dos = get_dos(syst,energy_range)
        dos = np.array(dos)
        idos = cumtrapz(dos,energy_range,initial=0)
    return idos, energy_range

def get_dos(syst,energy_range):
    fsyst = syst.finalized()
    num_leads = len(syst.leads)
    rho = kwant.operator.Density(fsyst,sum=True)
    dos = []
    for energy in energy_range:
        wf = kwant.wave_function(fsyst,energy=energy)
        all_states = np.vstack([wf(i) for i in range(num_leads)])
        dos.append(sum(rho(mode) for mode in all_states)/syst.area/(2*np.pi)) # Here syst.area is the actual area / (lattice constant a)**2
    return dos


def get_dos_kpm(syst,energy_resolution):
    fsyst = syst.finalized()
    spectrum = kwant.kpm.SpectralDensity(fsyst,rng=0)
    try:
        spectrum.add_moments(energy_resolution=energy_resolution)
    except ValueError as e:
        pass
    energies, densities = spectrum()
    dos = [density/syst.area for density in densities]
    return dos, energies


