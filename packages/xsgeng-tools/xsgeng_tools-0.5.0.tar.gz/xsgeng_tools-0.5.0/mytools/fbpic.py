from numpy import concatenate, flipud, exp, pi, s_
import os 
import re

def get_h5files(path):
    h5files = []
    for file in os.listdir(path):
        if re.match(r'data\d*\.h5', file):
            h5files.append(f'{path}/{file}')

    h5files.sort()
    return h5files

def get_field_slice(field, theta=0, inversed=False):
    field_up = get_field(field, theta)
    field_down = get_field(field, theta+pi)
    fac = -1 if inversed else 1
    return concatenate((fac*flipud(field_down), field_up), axis=0)

def get_field(field, theta=0):
    modes = (field.shape[0] + 1) // 2
    data = field[0]
    for m in range(1, modes):
        data += ((field[2*m-1] + 1j*field[2*m]) * exp(-1j*m*theta)).real
        
    return(data)

def get_field_partial(field, theta=0, sr=s_[:], sz=s_[:]):
    modes = (field.shape[0] + 1) // 2
    data = field[0, sr, sz]
    for m in range(1, modes):
        data += ((field[2*m-1, sr, sz] + 1j*field[2*m, sr, sz]) * exp(-1j*m*theta)).real

    return(data)