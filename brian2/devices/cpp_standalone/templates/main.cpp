#include<stdlib.h>
#include "objects.h"
#include<ctime>
<<<<<<< HEAD
#include<omp.h>
=======
#include "run.h"
>>>>>>> upstream/cpp_standalone_improvements

{% for codeobj in code_objects %}
#include "code_objects/{{codeobj.name}}.h"
{% endfor %}

{% for name in additional_headers %}
#include "{{name}}"
{% endfor %}

#include<iostream>

int main(int argc, char **argv)
{

	std::clock_t start = std::clock();

	brian_start();

	{
		using namespace brian;
		{% for main_line in main_lines %}
		{{ main_line }}
		{% endfor %}
	}

	double _run_duration = (std::clock()-start)/(double)CLOCKS_PER_SEC;
	std::cout << "Simulation time: " << _run_duration << endl;

	brian_end();

	return 0;
}
