#include<iostream>
#include<vector>
#include<algorithm>
#include<inttypes.h>
using namespace std;

//TODO: The data type for indices is currently fixed (int), all floating point
//      variables (delays, dt) are assumed to use the same data type
typedef int32_t DTYPE_int;

template <class scalar>
class CSpikeQueue
{
public:
	vector< vector<DTYPE_int> > queue; // queue[(offset+i)%queue.size()] is delay i relative to current time
	scalar dt;
	unsigned int offset;
	unsigned int *delays;
	int source_start;
	int source_end;
    vector< vector<int> > synapses;

	CSpikeQueue(int _source_start, int _source_end)
		: source_start(_source_start), source_end(_source_end)
	{
		queue.resize(1);
		offset = 0;
		dt = 0.0;
		delays = NULL;
	};

    void prepare(scalar *real_delays, int *sources, unsigned int n_synapses,
                 double _dt)
    {
        if (delays)
            delete [] delays;

        if (dt != 0.0 && dt != _dt)
        {
            // dt changed, we have to get the old spikes out of the queue and
            // reinsert them at the correct positions
            vector< vector<DTYPE_int> > queue_copy = queue; // does a real copy
            const double conversion_factor = dt / _dt;
            const unsigned int oldsize = queue.size();
            const unsigned int newsize = (int)(oldsize * conversion_factor) + 1;
            queue.clear();
            queue.resize(newsize);
            for (unsigned int i=0; i<oldsize; i++)
            {
                vector<DTYPE_int> spikes = queue_copy[(i + offset) % oldsize];
                queue[(int)(i * conversion_factor + 0.5)] = spikes;
            }
            offset = 0;
        }

        delays = new unsigned int[n_synapses];
        synapses.clear();
        synapses.resize(source_end - source_start);

        for (unsigned int i=0; i<n_synapses; i++)
        {
            delays[i] =  (int)(real_delays[i] / _dt + 0.5); //round to nearest int
            synapses[sources[i] - source_start].push_back(i);
        }

        dt = _dt;
    }

	void expand(unsigned int newsize)
	{
		const unsigned int n = queue.size();
		if (newsize<=n)
		    return;
		// rotate offset back to start (leaves the circular structure unchanged)
		rotate(queue.begin(), queue.begin()+offset, queue.end());
		offset = 0;
		// add new elements
		queue.resize(newsize);
	};

	inline void ensure_delay(unsigned int delay)
	{
		if(delay>=queue.size())
		{
			expand(delay+1);
		}
	};

	void push(int *spikes, unsigned int nspikes)
	{
		const unsigned int start = lower_bound(spikes, spikes+nspikes, source_start)-spikes;
		const unsigned int stop = upper_bound(spikes, spikes+nspikes, source_end-1)-spikes;
		for(unsigned int idx_spike=start; idx_spike<stop; idx_spike++)
		{
			const unsigned int idx_neuron = spikes[idx_spike] - source_start;
			vector<int> &cur_indices = synapses[idx_neuron];
			for(unsigned int idx_indices=0; idx_indices<cur_indices.size(); idx_indices++)
			{
				const int synaptic_index = cur_indices[idx_indices];
				const unsigned int delay = delays[synaptic_index];
				// make sure there is enough space and resize if not
				ensure_delay(delay);
				// insert the index into the correct queue
				queue[(offset+delay)%queue.size()].push_back(synaptic_index);
			}
		}
	};

	inline vector<DTYPE_int>* peek()
	{
		return &queue[offset];
	};

	void advance()
	{
		// empty the current queue, note that for most compilers this shouldn't deallocate the memory,
		// although VC<=7.1 will, so it will be less efficient with that compiler
		queue[offset].clear();
		// and advance to the next offset
		offset = (offset+1)%queue.size();
	};
};
