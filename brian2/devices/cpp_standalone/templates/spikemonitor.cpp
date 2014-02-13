{% extends 'common_group.cpp' %}

{% block maincode %}
	//// MAIN CODE ////////////
    {# USES_VARIABLES { t, i, _clock_t, _spikespace, _count,
                        _source_start, _source_stop} #}
	int _num_spikes = {{_spikespace}}[_num_spikespace-1];
    
    #pragma omp single
    {
        if (_num_spikes > 0)
        {
            int _start_idx = 0;
            int _end_idx = - 1;
            for(int _j=0; _j<_num_spikes; _j++)
            {
                const int _idx = {{_spikespace}}[_j];
                if (_idx >= _source_start) {
                    _start_idx = _j;
                    break;
                }
            }
            for(int _j=_start_idx; _j<_num_spikes; _j++)
            {
                const int _idx = {{_spikespace}}[_j];
                if (_idx >= _source_stop) {
                    _end_idx = _j;
                    break;
                }
            }
            if (_end_idx == -1)
                _end_idx =_num_spikes;
            _num_spikes = _end_idx - _start_idx;
            if (_num_spikes > 0) {
              	for(int _j=_start_idx; _j<_end_idx; _j++)
               	{
              		const int _idx = {{_spikespace}}[_j];
               		{{_dynamic__i}}.push_back(_idx-_source_start);
               		{{_dynamic__t}}.push_back(t);
               	}
            }
        }
        if (_end_idx == -1)
            _end_idx =_num_spikes;
        _num_spikes = _end_idx - _start_idx;
        if (_num_spikes > 0) {
        	for(int _j=_start_idx; _j<_end_idx; _j++)
        	{
        		const int _idx = {{_spikespace}}[_j];
        		{{_dynamic_i}}.push_back(_idx-_source_start);
        		{{_dynamic_t}}.push_back(_clock_t);
        	}
        }
    }

{% endblock %}

{% block extra_functions_cpp %}
void _debugmsg_{{codeobj_name}}()
{
	using namespace brian;
	std::cout << "Number of spikes: " << {{_dynamic_i}}.size() << endl;
}
{% endblock %}

{% block extra_functions_h %}
void _debugmsg_{{codeobj_name}}();
{% endblock %}

{% macro main_finalise() %}
_debugmsg_{{codeobj_name}}();
{% endmacro %}
