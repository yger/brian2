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
		for(int i=0; i<objects.size(); i++)
		{
			double t = clock->t_();
			for(int i=0; i<objects.size(); i++)
			{
                codeobj_func func = objects[i].second;
                #pragma omp barrier
                func();
			}

			#pragma omp single 
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
		if(clock->t_()<minclock->t_())
			minclock = clock;
	}
	// find set of equal clocks
	#pragma omp single
	{
		curclocks.clear();
		double t = minclock->t_();
		for(std::set<Clock*>::iterator i=clocks.begin(); i!=clocks.end(); i++)
		{
			Clock *clock = *i;
			double s = clock->t_();
			if(s==t or fabs(s-t)<=Clock_epsilon)
				curclocks.insert(clock);
		}
	}
	return minclock;
}
