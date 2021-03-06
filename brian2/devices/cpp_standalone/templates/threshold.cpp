{% extends 'common_group.cpp' %}

{% block maincode %}
	{# USES_VARIABLES { t, _spikespace } #}
	// not_refractory and lastspike are added as needed_variables in the
	// Thresholder class, we cannot use the USES_VARIABLE mechanism
	// conditionally

	//// MAIN CODE ////////////
	long _cpp_numspikes = 0;
	for(int _idx=0; _idx<N; _idx++)
	{
	    const int _vectorisation_idx = _idx;
		{% for line in code_lines %}
		{{line}}
		{% endfor %}
		if(_cond) {
			{{_spikespace}}[_cpp_numspikes++] = _idx;
			{% if _uses_refractory %}
			// We have to use the pointer names directly here: The condition
			// might contain references to not_refractory or lastspike and in
			// that case the names will refer to a single entry.
			{{not_refractory}}[_idx] = false;
			{{lastspike}}[_idx] = t;
			{% endif %}
		}
	}
	{{_spikespace}}[N] = _cpp_numspikes;
{% endblock %}
