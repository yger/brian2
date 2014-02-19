{% extends 'common_group.cpp' %}

{% block maincode %}
    {# USES_VARIABLES { _synaptic_post, _synaptic_pre, N_post } #}
    {% set _target_var_array = get_array_name(_target_var) %}
	//// MAIN CODE ////////////
	// Set all the target variable values to zero
	#pragma omp for schedule(static)
	for (int _target_idx=0; _target_idx<N_post; _target_idx++)
	    {{_target_var_array}}[_target_idx] = 0.0;
	
	#pragma omp master
	{
		for(int _idx=0; _idx<_num_synaptic_post; _idx++)
		{
			{% for line in code_lines %}
			{{line}}
			{% endfor %}
			{{_target_var_array}}[{{_synaptic_post}}[_idx]] += _synaptic_var;
		}
	}
{% endblock %}
