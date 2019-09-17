"""Implement opinionated Py<->R conversion functions."""

import rpy2.robjects as ro
from rpy2.robjects import numpy2ri, pandas2ri

from rpy2.robjects.conversion import (
    converter as template_converter,
    Converter)


# setup converter
template_converter += numpy2ri.converter
template_converter += pandas2ri.converter
converter = Converter('r_wrapper', template=template_converter)


@converter.py2rpy.register(list)
def _(obj):
    print('py2rpy', 'list -> <type>Vector')
    # TODO: handle mixed types better

    if len({type(e) for e in obj}) != 1:
        raise TypeError(f'Mixed types in {obj}')

    vector_type_map = {
        float: ro.FloatVector,
        int: ro.IntVector,
        bool: ro.BoolVector,
        str: ro.StrVector
    }

    for type_, VectorClass in vector_type_map.items():
        if isinstance(obj[0], type_):
            print('Detected:', type_)
            return VectorClass([converter.py2rpy(x) for x in obj])

    raise TypeError(f'No vector class found for {obj}')


@converter.py2rpy.register(dict)
def _(obj):
    print('py2rpy', 'dict -> ro.ListVector')
    print([type(o) for o in obj.values()])

    return ro.vectors.ListVector(
        {k: converter.py2rpy(v) for k, v in obj.items()})


@converter.rpy2py.register(ro.vectors.ListVector)
def _(obj):
    print('rpy2py', 'ro.Vector -> dict')
    print(obj)

    values = [converter.rpy2py(x) for x in obj]
    keys = obj.names

    return dict(zip(keys, values))