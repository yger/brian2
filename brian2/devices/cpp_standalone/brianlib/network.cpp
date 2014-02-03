#include "network.h"
#include<stdlib.h>
#include<iostream>
#include<omp.h>

#define Clock_epsilon 1e-14

Network::Network()
{
	t = 0.0;
}

void Network::clear()
{
	objects.clear();
}

void Network::add(Clock* clock, codeobj_func func)
{
	objects.push_back(std::make_pair<Clock*, codeobj_func>(clock, func));
}

void Network::run(double duration)
{
	Clock* clock;
	double t_end = t + duration;
	// compute the set of clocks
	compute_clocks();
	// set interval for all clocks

	for(std::set<Clock*>::iterator i=clocks.begin(); i!=clocks.end(); i++)
	{
		(*i)->set_interval(t, t_end);
	}

	clock = next_clocks();
	
	#pragma omp parallel
	{
		#pragma omp master
		std::cout << "OpenMP is using " << omp_get_num_threads() << " threads...."  << std::endl;

		while(clock->running())
		{
			double t = clock->t();
			for(int i=0; i<objects.size(); i++)
			{
				Clock *obj_clock = objects[i].first;
				// Only execute the object if it uses the right clock for this step
				if (curclocks.find(obj_clock) != curclocks.end())
				{
	                codeobj_func func = objects[i].second;
	                #pragma omp barrier
	                func(t);
				}
			}

			#pragma omp master 
			{
				for(std::set<Clock*>::iterator i=curclocks.begin(); i!=curclocks.end(); i++)
				{		
					(*i)->tick();
				}
			}
			
			clock = next_clocks();
		}
		t = t_end;
	}
}

void Network::compute_clocks()
{
	clocks.clear();
	for(int i=0; i<objects.size(); i++)
	{
		Clock *clock = objects[i].first;
		clocks.insert(clock);
	}
}

Clock* Network::next_clocks()
{
	// find minclock, clock with smallest t value
	Clock *minclock = *clocks.begin();
	for(std::set<Clock*>::iterator i=clocks.begin(); i!=clocks.end(); i++)
	{
		Clock *clock = *i;
		if(clock->t()<minclock->t())
			minclock = clock;
	}
	#pragma omp master
	{
		// find set of equal clocks
		curclocks.clear();

		double t = minclock->t();
		for(std::set<Clock*>::iterator i=clocks.begin(); i!=clocks.end(); i++)
		{
			Clock *clock = *i;
			double s = clock->t();
			if(s==t or fabs(s-t)<=Clock_epsilon)
				curclocks.insert(clock);
		}
	}
	return minclock;
}
