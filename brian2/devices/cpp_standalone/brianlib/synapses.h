#ifndef _BRIAN_SYNAPSES_H
#define _BRIAN_SYNAPSES_H

#include<vector>
#include<algorithm>
#include<omp.h>
#include "spikequeue.h"

template<class scalar> class Synapses;
template<class scalar> class SynapticPathway;

template <class scalar>
class SynapticPathway
{
public:
	int Nsource, Ntarget, _nb_threads;
	std::vector<scalar>& delay;
	std::vector<int> &sources;
	std::vector<int> all_peek;
	scalar dt;
	std::vector< CSpikeQueue<scalar> * > queue;
	SynapticPathway(int _Nsource, int _Ntarget, std::vector<scalar>& _delay, std::vector<int> &_sources,
					scalar _dt, int _spikes_start, int _spikes_stop)
		: Nsource(_Nsource), Ntarget(_Ntarget), delay(_delay), sources(_sources), dt(_dt)
	{
		_nb_threads = OMP_NB_THREADS;
		std::cout << "Constructing SynapticPathway with " << _nb_threads << " threads" << std::endl;
		omp_set_dynamic(0);
		for (int _idx=0; _idx < _nb_threads; _idx++)
			queue.push_back(new CSpikeQueue<scalar>(_spikes_start, _spikes_stop));
	};

	~SynapticPathway()
	{
		#pragma omp parallel
    	{
    		#pragma omp for schedule(static)
			for (int _idx=0; _idx < _nb_threads; _idx++)
				delete(queue[_idx]);
		}
	}

	void push(int *spikes, unsigned int nspikes)
    {
    	queue[omp_get_thread_num()]->push(spikes, nspikes);
    }

	void advance()
    {
    	queue[omp_get_thread_num()]->advance();
    }

	inline vector<DTYPE_int>* peek()
    {
    	#pragma omp single
    	{
    		all_peek.clear();
    		for (int _idx=0; _idx < _nb_threads; _idx++)
    			all_peek.insert(all_peek.begin(), queue[_idx]->peek()->begin(), queue[_idx]->peek()->end());
    	}
    	return &all_peek;
    }

    void prepare(scalar *real_delays, int *sources, unsigned int n_synapses, double _dt)
    {
    	omp_set_dynamic(0);
    	#pragma omp parallel 
    	{
    		omp_set_num_threads(_nb_threads);

    		unsigned int length   = n_synapses/_nb_threads;
    		unsigned int padding  = omp_get_thread_num()*length;

    		double * _loc_delays  = &real_delays[padding];
		    int32_t* _loc_sources = &sources[padding];

		    #pragma omp critical
		    {
		    	std::cout << "Preparing SynapticPathway with " << _nb_threads << " threads" << std::endl;
    			std::cout << "Node " << omp_get_thread_num() << " " << length << "," << padding << std::endl;
    		}

    		queue[omp_get_thread_num()]->prepare(_loc_delays, _loc_sources, length, _dt);
    	}
    }

};

template <class scalar>
class Synapses
{
public:
    int _N_value;
    inline double _N() { return _N_value;};
	int Nsource;
	int Ntarget;
	std::vector< std::vector<int> > _pre_synaptic;
	std::vector< std::vector<int> > _post_synaptic;

	Synapses(int _Nsource, int _Ntarget)
		: Nsource(_Nsource), Ntarget(_Ntarget)
	{
		for(int i=0; i<Nsource; i++)
			_pre_synaptic.push_back(std::vector<int>());
		for(int i=0; i<Ntarget; i++)
			_post_synaptic.push_back(std::vector<int>());
		_N_value = 0;
	};
};

#endif

