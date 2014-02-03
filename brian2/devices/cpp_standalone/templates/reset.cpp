{% extends 'common_group.cpp' %}
{% block maincode %}
	{# USES_VARIABLES { _spikespace } #}

	const int *_spikes = {{_spikespace}};
	const int _num_spikes = {{_spikespace}}[N];

	//// MAIN CODE ////////////
	#pragma omp for
	for(int _index_spikes=0; _index_spikes<_num_spikes; _index_spikes++)
	{
		const int _idx = _spikes[_index_spikes];
		const int _vectorisation_idx = _idx;
		{% for line in code_lines %}
		{{line}}
		{% endfor %}
	}
{% endblock %}
