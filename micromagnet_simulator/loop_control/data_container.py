from micromagnet_simulator.loop_control.looping import loop_obj 
from micromagnet_simulator.loop_control.setpoint_mgr import setpoint 

from functools import wraps
import copy

import numpy as np


class data_container(np.ndarray):
    def __new__(subtype, input_type=None, shape = (1,)):
        obj = super(data_container, subtype).__new__(subtype, shape, object)

        if input_type is not None:
            obj[0] = input_type

        return obj

    def __copy__(self):
        cpy = data_container(shape = self.shape)

        for i in range(self.size):
            cpy.flat[i] = copy.copy(self.flat[i])

        return cpy

    def move(self, displacement):
        for i in range(self.size):
            self.flat[i].move(displacement)

        return self

def loop_ctrl(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        obj = args[0]

        loop_info_args = []
        loop_info_kwargs = []
        for i in range(1,len(args)):
            if isinstance(args[i], loop_obj):
                loop_info_args.append(_get_loop_info(args[i], i))

        for key in kwargs.keys():
            if isinstance(kwargs[key], loop_obj):
                loop_info_kwargs.append(_get_loop_info(kwargs[key], key))

        for lp in loop_info_args:
            for i in range(len(lp['axis'])-1,-1,-1):
                new_dim, axis = get_new_dim_loop(obj.data.shape, lp['axis'][i], lp['shape'][i])
                lp['axis'][i] = axis
                obj.data = update_dimension(obj.data, new_dim)

                if lp['setpnt'] is not None:
                    lp['setpnt'][i].axis = axis
                    obj._setpoints += lp['setpnt'][i]

        # todo update : (not used atm, but just to be generaric.)
        for lp in loop_info_kwargs:
            new_dim = get_new_dim_loop(obj.data.shape, lp)
            obj.data = update_dimension(obj.data, new_dim)

        loop_over_data(func, obj.data, args, loop_info_args, kwargs, loop_info_kwargs)


    return wrapper 

def get_new_dim_loop(current_dim, axis, shape):
    '''
    function to get new dimensions from a loop spec.
    Args:
        current_dim [tuple/array] : current dimensions of the data object.
        axis [int] : on which axis to put the new loop dimension.
        shape [int] : the number of elements that a are along that loop axis.
    Returns:
        new_dim [array] : new dimensions of the data obeject when one would include the loop spec
        axis [int] : axis on which a loop variable was put (if free assign option was used (axis of -1))
    '''
    current_dim = list(current_dim)
    new_dim = []
    if axis == -1:
        # assume if last dimension has size 1, that you want to extend this direction.
        if current_dim[-1] == 1:
            new_dim = current_dim
            new_dim[-1] = shape
            axis = len(new_dim) - 1
        else:
            new_dim = [shape] + current_dim
            # assign new axis.
            axis = len(new_dim) - 1
    else:
        if axis >= len(current_dim):
            new_dim = [1]*(axis+1)
            for i in range(len(current_dim)):
                new_dim[axis-len(current_dim)+1 + i] = current_dim[i]
            new_dim[0] = shape
        else:
            if current_dim[-1-axis] == shape:
                new_dim = current_dim
            elif current_dim[-1-axis] == 1:
                new_dim = current_dim
                new_dim[-1-axis] = shape
            else:
                raise ValueError("Dimensions on loop axis {} not compatible with previous loops\n\
                    (current dimensions is {}, wanted is {}).\n\
                    Please change loop axis or update the length.".format(axis,
                    current_dim[-axis-1], shape))

    return new_dim, axis

def update_dimension(data, new_dimension_info, use_ref = False):
    '''
    update dimension of the data object to the one specified in new dimension_info
    Args:
        data (np.ndarray[dtype = object]) : numpy object that contains all the segment data of every iteration.
        new_dimension_info (list/np.ndarray) : list of the new dimensions of the array
        use_ref (bool) : use pointer to copy, or take full copy (False is full copy)
    Returns:
        data (np.ndarray[dtype = object]) : same as input data, but with new_dimension_info.
    '''

    new_dimension_info = np.array(new_dimension_info)

    for i in range(len(new_dimension_info)):
        if data.ndim < i+1:
            data = _add_dimensions(data, new_dimension_info[-i-1:], use_ref)

        elif list(data.shape)[-i -1] != new_dimension_info[-i -1]:
            shape = list(data.shape)
            shape[-i-1] = new_dimension_info[-i-1]
            data = _extend_dimensions(data, shape, use_ref)

    return data

def loop_over_data(func, data, args, args_info, kwargs, kwargs_info):
    '''
    recursive function to apply the
    Args:
        func : function to execute
        data : data of the segment
        args: arugments that are provided
        args_info : argument info is provided (e.g. axis updates)
        kwargs : kwargs provided
        kwarfs_info : same as args_info
        loop_dimension
    Returns:
        None
    '''
    shape = list(data.shape)
    n_dim = len(shape)

    # copy the input --> we will fill in the arrays
    args_cpy = list(copy.copy(args))
    kwargs_cpy = copy.copy(kwargs)

    for i in range(shape[0]):
        for arg in args_info:
            if n_dim-1 in arg['axis']:
                args_cpy[arg['nth_arg']] = args[arg['nth_arg']][i]
        for kwarg in kwargs_info:
            if n_dim-1 in kwarg['axis']:
                kwargs_cpy[kwargs_info['nth_arg']] = kwargs[kwargs_info['nth_arg']][i]

        if n_dim == 1:
            # we are at the lowest level of the loop.
            args_cpy[0].data_tmp = data[i]
            data[i] = func(*args_cpy, **kwargs_cpy)
        else:
            # clean up args, kwargs
            loop_over_data(func, data[i], args_cpy, args_info, kwargs_cpy, kwargs_info)

def _get_loop_info(lp, index):
    if lp.no_setpoints or lp.setvals is None:
        setpnt = None
    else:
        setpnt=list()

        for j in range(len(lp.axis)):
            setpnt_single = setpoint(lp.axis[j], label = (lp.labels[j],), unit = (lp.units[j],), setpoint=(lp.setvals[j],))
            setpnt.append(setpnt_single)

    info = {
    'nth_arg': index,
    'shape' : lp.shape,
    'len': len(lp),
    'axis': lp.axis,
    'data' : lp.data,
    'setpnt' : setpnt
    }
    return info

def _extend_dimensions(data, shape, use_ref):
    '''
    Extends the dimensions of a existing array object. This is useful if one would have first defined sweep axis 2 without defining axis 1.
    In this case axis 1 is implicitly made, only harbouring 1 element.
    This function can be used to change the axis 1 to a different size.
    Args:
        data (np.ndarray[dtype = object]) : numpy object that contains all the segment data of every iteration.
        shape (list/np.ndarray) : list of the new dimensions of the array (should have the same lenght as the dimension of the data!)
        use_ref (bool) : use pointer to copy, or take full copy (False is full copy)
    '''
    new_data = data_container(shape = shape)

    for i in range(len(shape)):
        if data.shape[i] != shape[i]:
            if i == 0:
                for j in range(len(new_data)):
                    new_data[j] = cpy_numpy_shallow(data, use_ref)
            else:
                new_data = new_data.swapaxes(i, 0)
                data = data.swapaxes(i, 0)

                for j in range(len(new_data)):
                    new_data[j] = cpy_numpy_shallow(data, use_ref)

                new_data = new_data.swapaxes(i, 0)

    return new_data

def _add_dimensions(data, shape, use_ref):
    """
    Function that can be used to add and extra dimension of an array object. A seperate function is needed since we want to make a copy and not a reference.
    Note that only one dimension can be extended!
    Args:
        data (np.ndarray[dtype = object]) : numpy object that contains all the segment data of every iteration.
        shape (list/np.ndarray) : list of the new dimensions of the array
        use_ref (bool) : use pointer to copy, or take full copy (False is full copy)
    """
    new_data =  data_container(shape = shape)
    for i in range(shape[0]):
        new_data[i] = cpy_numpy_shallow(data, use_ref)
    return new_data

def cpy_numpy_shallow(data, use_ref):
    '''
    Makes a shallow copy of an numpy object array.
    Args:
        data : data element
        use_ref (bool) : use reference to copy
    '''

    if use_ref == True:
        if type(data) != data_container:
            return data

        if data.shape == (1,):
            return data[0]

        shape = data.shape
        data_flat = data.flatten()
        new_arr = np.empty(data_flat.shape, dtype=object)

        for i in range(len(new_arr)):
            new_arr[i] = data_flat[i]

        new_arr = new_arr.reshape(shape)

    else:
        if type(data) != data_container:
            return copy(data)

        if data.shape == (1,):
            return data[0].__copy__()

        shape = data.shape
        data_flat = data.flatten()
        new_arr = np.empty(data_flat.shape, dtype=object)

        for i in range(len(new_arr)):
            new_arr[i] = copy.copy(data_flat[i])

        new_arr = new_arr.reshape(shape)

    
    return new_arr
