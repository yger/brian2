from brian2.core.base import BrianObject
from brian2.core.scheduler import Scheduler
from brian2.core.variables import Variables
from brian2.units.allunits import second, hertz
from brian2.units.fundamentalunits import Unit, Quantity
from brian2.groups.group import GroupCodeRunner

__all__ = ['PopulationRateMonitor']


class PopulationRateMonitor(GroupCodeRunner):
    '''
    Record instantaneous firing rates, averaged across neurons from a
    `NeuronGroup` or other spike source.

    Parameters
    ----------
    source : (`NeuronGroup`, `SpikeSource`)
        The source of spikes to record.
    when : `Scheduler`, optional
        When to record the spikes, by default uses the clock of the source
        and records spikes in the slot 'end'.
    name : str, optional
        A unique name for the object, otherwise will use
        ``source.name+'_ratemonitor_0'``, etc.
    codeobj_class : class, optional
        The `CodeObject` class to run code with.
    '''
    def __init__(self, source, when=None, name='ratemonitor*',
                 codeobj_class=None):

        # run by default on source clock at the end
        scheduler = Scheduler(when)
        if not scheduler.defined_clock:
            scheduler.clock = source.clock
        if not scheduler.defined_when:
            scheduler.when = 'end'

        self.codeobj_class = codeobj_class
        BrianObject.__init__(self, when=scheduler, name=name)

        self.variables = Variables(self)
        self.variables.add_clock_variables(self.clock)
        self.variables.add_dynamic_array('_rate', size=0, unit=hertz,
                                         constant_size=False)
        self.variables.add_dynamic_array('_t', size=0, unit=second,
                                         constant_size=False)
        self.variables.add_constant('_num_source_neurons', unit=Unit(1),
                                    value=len(source))

        GroupCodeRunner.__init__(self, source, 'ratemonitor', when=scheduler)

    def reinit(self):
        '''
        Clears all recorded rates
        '''
        raise NotImplementedError()

    @property
    def rate(self):
        '''
        Array of recorded rates (in units of Hz).
        '''
        return Quantity(self.variables['_rate'].get_value(), dim=hertz.dim,
                        copy=True)

    @property
    def rate_(self):
        '''
        Array of recorded rates (unitless).
        '''
        return self.variables['_rate'].get_value().copy()

    @property
    def t(self):
        '''
        Array of recorded time points (in units of second).
        '''
        return Quantity(self.variables['_t'].get_value(), dim=second.dim,
                        copy=True)

    @property
    def t_(self):
        '''
        Array of recorded time points (unitless).
        '''
        return self.variables['_t'].get_value().copy()

    def __repr__(self):
        description = '<{classname}, recording {source}>'
        return description.format(classname=self.__class__.__name__,
                                  source=self.source.name)
