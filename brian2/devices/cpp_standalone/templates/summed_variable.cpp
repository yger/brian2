{% extends 'common_group.cpp' %}

{% block maincode %}
    {# USES_VARIABLES { _synaptic_post, _synaptic_pre, N_post } #}
	//// MAIN CODE ////////////
	// Set all the target variable values to zero
	#pragma omp for schedule(static)
	for (int _target_idx=0; _target_idx<N_post; _target_idx++)
	    _ptr{{_target_var_array}}[_target_idx] = 0.0;
	
	#pragma omp for schedule(static)
	for(int _idx=0; _idx<_num_synaptic_post; _idx++)
	{
		{% for line in code_lines %}
		{{line}}
		{% endfor %}
		_ptr{{_target_var_array}}[_postsynaptic_idx] += _synaptic_var;
	}
{% endblock %}
