#include<stdlib.h>
#include "objects.h"
#include<ctime>
#include<omp.h>

{% for codeobj in code_objects %}
#include "code_objects/{{codeobj.name}}.h"
{% endfor %}

#include<iostream>

int main(void)
{
	std::time_t start = std::time(NULL);
	_init_arrays();
	_load_arrays();
	srand((unsigned int)time(NULL));
	const double dt = {{dt}};
	double t = 0.0;
	{% for main_line in main_lines %}
	{{ main_line }}
	{% endfor %}
	std::time_t stop = std::time(NULL);
	double duration = std::difftime(stop, start);
	std::cout << "Simulation time: " << duration << endl;
	_write_arrays();
	_dealloc_arrays();
	return 0;
}
