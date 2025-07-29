import os
import numpy as np
from scipy.constants import pi
import h5py
from pathlib import Path

def read_scalar(path: str, keyword: str=None) -> np.ndarray|dict:
    '''
    read scalar data from scalars.txt
    if keyword is None, return a dict of all scalars
    '''
    path = Path(path)
    scalars = path / 'scalars.txt'

    keys = []
    with open(scalars, mode='r') as f:
        for lino, line in enumerate(f):
            if line == '#\n':
                f.readline()
                data = np.loadtxt(f)
                break
            else:
                keys.append(line.split()[2])

    if keyword:
        return data[:, keys.index(keyword)]
    
    # convert to dict
    return {key: data[:, i] for i, key in enumerate(keys)}

def get_timesteps(result_path, number=0):
    with h5py.File(os.path.join(result_path, f'Fields{number}.h5'), 'r', locking=False) as h5f:
        ts = list(h5f['data'].keys())   
    return ts


def get_extent(result_path, number=0, component='Ey', lambda0=0.8e-6):
    '''
    get 2D extent
    '''
    with h5py.File(os.path.join(result_path, f'Fields{number}.h5'), 'r', locking=False) as h5f:
        ts = list(h5f['data'].keys())
        nx, ny = h5f['data'][ts[0]][component].shape
        dx, dy = h5f['data'][ts[0]][component].attrs['gridSpacing']

    return np.array([0, nx*dx, 0, ny*dy]) / 2/pi * lambda0 /1e-6


def get_cellsize(result_path, number=0, component='Ey', lambda0=0.8e-6):
    '''
    get 2D or 3D cell size in um
    '''
    with h5py.File(os.path.join(result_path, f'Fields{number}.h5'), 'r', locking=False) as h5f:
        ts = list(h5f['data'].keys())
        dset = h5f['data'][ts[0]][component]
        if dset.dims == 2:
            dx, dy = dset.attrs['gridSpacing']
            return dx/2/pi*lambda0/1e-6, dy/2/pi*lambda0/1e-6

        if dset.dims == 3:
            dx, dy, dz = dset.attrs['gridSpacing']
            return dx/2/pi*lambda0/1e-6, dy/2/pi*lambda0/1e-6, dz/2/pi*lambda0/1e-6

def get_field(result_path, ts, component, number=0, slice=()) -> np.ndarray:
    if isinstance(ts, int):
        ts = f'{ts:010d}'
    with h5py.File(os.path.join(result_path, f'Fields{number}.h5'), 'r', locking=False) as h5f:
        dset = h5f['data'][ts][component]
        if len(dset.shape) == 2:
            return dset[slice].T
        else:
            return dset[slice]


def get_traj(result_path, name, component):
    with h5py.File(os.path.join(result_path, f'TrackParticles_{name}.h5'), 'r', locking=False) as h5f:
        return h5f[component][()]

def get_particle(result_path: [Path|str], t, name, components):
    if isinstance(result_path, str):
        result_path = Path(result_path)
        
    with h5py.File(result_path/f'TrackParticlesDisordered_{name}.h5', 'r', locking=False) as f:
        if isinstance(t, str):
            dset = f['data'][t]
        else:
            ts = list(f['data'].keys())
            dset = f['data'][ts[t]]
        ret = [dset['particles'][name][component][()] for component in components]
        return ret
