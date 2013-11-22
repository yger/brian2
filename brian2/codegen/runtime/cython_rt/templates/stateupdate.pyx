# ITERATE_ALL { _idx }
cdef int _idx
cdef int _vectorisation_idx
#cdef int N
with cython.boundscheck(False):
    for _idx in range(N):
        _vectorisation_idx = _idx
        {% for line in code_lines %}
        {{line}}
        {% endfor %}
