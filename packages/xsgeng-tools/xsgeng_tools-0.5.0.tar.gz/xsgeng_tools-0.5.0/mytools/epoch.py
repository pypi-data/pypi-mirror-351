import os
import re
import sdf
import h5py
import numpy as np
from scipy.constants import m_e, c

_field_names = {
        'Ex': 'Electric Field/Ex', 'Ey' : 'Electric Field/Ey' , 'Ez' : 'Electric Field/Ez' ,
        'Bx' : 'Magnetic Field/Bx', 'By' : 'Magnetic Field/By' , 'Bz' : 'Magnetic Field/Bz' ,
}


def get_sdffiles(path, prefix=''):
    sdffiles = []
    with open(os.path.join(path, f'{prefix}.visit'), 'r') as f:
        sdffiles = f.read().splitlines()
    
    for i in range(len(sdffiles)):
        sdffiles[i] = os.path.join(path, sdffiles[i])

    return sdffiles


def get_extent(result_path, ts=None, prefix=''):
    '''
    get 2D extent
    '''
    if result_path[-4:] == '.sdf':
        sdffile_name = result_path
    elif isinstance(ts, int):
        ts = f'{ts:04d}'
        sdffile_name = f'{result_path}/{prefix}{ts}.sdf'
    f = sdf.read(sdffile_name, dict=True)
    
    extent = [
        f['Grid/Grid'].data[0][0],
        f['Grid/Grid'].data[0][-1],
        f['Grid/Grid'].data[1][0],
        f['Grid/Grid'].data[1][-1],
    ]
    
    return np.array(extent)


def get_field(result_path, component, ts=None, prefix='', slice=()) -> np.ndarray:
    if result_path[-4:] == '.sdf':
        sdffile_name = result_path
    elif isinstance(ts, int):
        ts = f'{ts:04d}'
        sdffile_name = f'{result_path}/{prefix}{ts}.sdf'
    
    f = sdf.read(sdffile_name, dict=True)
    
    if component in _field_names.keys():
        dset = f.pop(_field_names[component]).data
    else:
        dset = f.pop(f'Derived/Number_Density/{component}').data
        
    if len(dset.shape) == 2:
        return dset[slice].T
    else:
        return dset[slice]


def get_particles(result_path, name, component : str, ts=None, prefix='') -> np.ndarray:
    if result_path[-4:] == '.sdf':
        sdffile_name = result_path
    elif isinstance(ts, int):
        ts = f'{ts:04d}'
        sdffile_name = f'{result_path}/{prefix}{ts}.sdf'

    f = sdf.read(sdffile_name, dict=True)
    
    if component not in ['px', 'py', 'pz', 'x', 'y', 'z', 'w', 'id']:
        raise KeyError(f'{component} not supported.')

    if component in ['px', 'py', 'pz']:
        dset = f.pop(f'Particles/{component.capitalize()}/{name}').data
        return dset[()] / m_e / c
    
    if component in ['x', 'y', 'z']:
        dset = f.pop(f'Grid/Particles/{name}').data
        return dset[{'x' : 0, 'y' : 1, 'z' : 2}[component]]

    if component == 'w':
        dset = f.pop(f'Particles/Weight/{name}').data
        return dset[()]

    if component == 'id':
        dset = f.pop(f'Particles/ID/{name}').data
        return dset[()]
    

def _get_all_ids(sdffiles, name, comm):
    nt = len(sdffiles)
    rank = 0 if comm is None else comm.Get_rank()
    comm_size = 1 if comm is None else comm.Get_size()

    ids = set()
    for i in range(rank, nt, comm_size):
        sdffile = sdffiles[i]

        f = sdf.read(sdffile,dict=True)

        ids.update(set(f[f'Particles/ID/{name}'].data[()])) 
    
    if comm is not None:
        ids_all = set()
        ids = comm.Gater(ids, root=0)
        
        for ids_ in ids:
            ids_all.update(ids_)
        return np.array(ids_all, dtype=int)
    else:
        return np.array(ids, dtype=int)
        
        
        
def sort(result_path, name, selected_ids=None, props=None, prefix='', comm=None):
    all_props = {
        'vx' : f'Particles/Vx/{name}',
        'vy' : f'Particles/Vy/{name}',
        'vz' : f'Particles/Vz/{name}',
        'px' : f'Particles/Px/{name}',
        'py' : f'Particles/Py/{name}',
        'pz' : f'Particles/Pz/{name}',
        'x'  : f'Grid/Particles/{name}', 
        'y'  : f'Grid/Particles/{name}', 
        # 'z'  : f'Grid/Particles/{name}', 
    }
    sdffiles = get_sdffiles(result_path, prefix)
    if props is None:
        f = sdf.read(sdffiles[-1], dict=True)
        props = []
        for prop in all_props.keys():
            if all_props[prop] in f.keys():
                props.append(prop)
    else:
        pass

    nt = len(sdffiles)
    rank = 0 if comm is None else comm.Get_rank()
    comm_size = 1 if comm is None else comm.Get_size()

    if selected_ids is None:
        selected_ids = _get_all_ids(sdffiles, name, comm)
    else:
        selected_ids = set(selected_ids)

    npart = len(selected_ids)
    print(f'{npart} particles selected')

    ordermap = {id_ : i for i, id_ in enumerate(selected_ids)}

    mpio_kws = {}
    if comm is not None:
        mpio_kws = {'driver' : 'mpio', 'comm' : comm}
    with h5py.File(os.path.join(result_path, f'TrackParticles_{prefix}_{name.split("/")[-1]}.h5'), 'w', **mpio_kws) as h5f:
        for prop in props:
            h5f.create_dataset(prop, (nt, npart), fillvalue=np.nan, dtype='float64')
        h5f.create_dataset('t', (nt, ), fillvalue=np.nan, dtype='float64')
        
        for i in range(rank, nt, comm_size):
            sdffile = sdffiles[i]
            print(sdffile)
            f = sdf.read(sdffile,dict=True)
            ids = f[f'Particles/ID/{name}'].data[()]

            if len(set(ids) & selected_ids) == 0:
                continue

            # selected = np.any(selected_ids[:, np.newaxis] == ids, axis=0)
            selected = np.array([id in selected_ids for id in ids])
            ids = ids[selected]
            orders = [ordermap[id] for id in ids]
            
            for prop in props:
                buf = np.full(npart, np.nan)
                if prop in ['x', 'y', 'z']:
                    buf[orders] = f[all_props[prop]].data[{'x':0, 'y':1, 'z':2}[prop]][selected]
                else:
                    buf[orders] = f[all_props[prop]].data[()][selected]
                h5f[prop][i, :] = buf
            h5f['t'][i] = f['Header']['time']
