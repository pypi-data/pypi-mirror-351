# src/pyneurorg/simulation/simulator_DEBUG.py

"""
DEBUG VERSION of Simulator class.
Defines the Simulator class for orchestrating pyneurorg simulations.
"""

import brian2 as b2
import numpy as np 
from ..organoid.organoid import Organoid 
from ..mea.mea import MEA 
from ..electrophysiology import brian_monitors as pbg_monitors
import traceback # For detailed error printing

class Simulator:
    def __init__(self, organoid: Organoid, mea: MEA = None, brian2_dt=None):
        print("--- DEBUG [Simulator.__init__]: Initializing Simulator ---")
        if not isinstance(organoid, Organoid):
            print(f"DEBUG: Error - organoid is not an instance of Organoid. Type: {type(organoid)}")
            raise TypeError("organoid must be an instance of pyneurorg.organoid.Organoid.")
        if mea is not None and not isinstance(mea, MEA):
            print(f"DEBUG: Error - mea is not an instance of MEA. Type: {type(mea)}")
            raise TypeError("mea must be an instance of pyneurorg.mea.MEA or None.")

        self.organoid = organoid
        self.mea = mea
        print(f"DEBUG: Organoid: {self.organoid.name}, MEA: {self.mea.name if self.mea else 'None'}")

        self.brian_network = None
        self.monitors = {} 
        
        if brian2_dt is not None:
            if not isinstance(brian2_dt, b2.Quantity) or not (brian2_dt.dimensions == b2.second.dimensions):
                raise TypeError("brian2_dt must be a Brian2 Quantity with time units.")
            self.brian_dt = brian2_dt
            b2.defaultclock.dt = self.brian_dt 
        else:
            self.brian_dt = b2.defaultclock.dt 
        print(f"DEBUG: Simulator brian_dt set to: {self.brian_dt}")
        
        self._network_objects = list(self.organoid.brian2_objects)
        print(f"DEBUG: Initial _network_objects count: {len(self._network_objects)}")
        self._stimulus_current_sources = []
        self._stimulus_namespace_counter = 0 
        self._cumulative_stim_vars_reset_added = set()
        print("--- DEBUG [Simulator.__init__]: Finished ---")


    def set_mea(self, mea_instance: MEA):
        if not isinstance(mea_instance, MEA):
            raise TypeError("mea_instance must be an instance of pyneurorg.mea.MEA.")
        self.mea = mea_instance
        print(f"DEBUG [Simulator.set_mea]: MEA set to: {mea_instance.name}")

    def add_stimulus(self, electrode_id: int, stimulus_waveform: b2.TimedArray,
                     target_group_name: str, influence_radius,
                     cumulative_stim_var: str = 'I_stimulus_sum',
                     flag_variable_template: str = "stf{id}"):
        print(f"--- DEBUG [Simulator.add_stimulus]: Called for electrode {electrode_id}, group '{target_group_name}' ---")
        if self.mea is None: raise ValueError("No MEA set for this simulator.")
        if not isinstance(stimulus_waveform, b2.TimedArray): raise TypeError("stimulus_waveform must be a TimedArray.")

        target_ng = self.organoid.get_neuron_group(target_group_name)
        print(f"DEBUG: Target NeuronGroup: {target_ng.name}")

        if cumulative_stim_var not in target_ng.variables:
            print(f"DEBUG: Error - Cumulative stim var '{cumulative_stim_var}' not in target_ng.variables. Available: {list(target_ng.variables.keys())}")
            raise AttributeError(f"Target NG '{target_group_name}' needs var '{cumulative_stim_var}'.")

        current_flag_name = flag_variable_template.format(id=electrode_id)
        print(f"DEBUG: Current flag name to check: '{current_flag_name}'")
        if current_flag_name not in target_ng.variables:
            print(f"DEBUG: Error - Flag var '{current_flag_name}' not in target_ng.variables. Available: {list(target_ng.variables.keys())}")
            raise AttributeError(
                f"Target NeuronGroup '{target_group_name}' does not have the boolean flag variable "
                f"'{current_flag_name}' defined in its equations."
            )
        print(f"DEBUG: Flag variable '{current_flag_name}' found in NeuronGroup.")

        target_neuron_indices_np = self.mea.get_neurons_near_electrode(
            organoid=self.organoid, neuron_group_name=target_group_name,
            electrode_id=electrode_id, radius=influence_radius
        )
        print(f"```python
# src/pyneurorg/simulation/simulator_DEBUG.py

"""
DEBUG VERSION of Simulator class for orchestrating pyneurorg simulations.
"""

import brian2 as b2
import numpy as np 
import traceback # For detailed error printing
from ..organoid.organoid import Organoid 
from ..mea.mea import MEA 
from ..electrophysiology import brian_monitors as pbg_monitors

class Simulator:
    def __init__(self, organoid: Organoid, mea: MEA = None, brian2_dt=None):
        print("--- DEBUG: Simulator.__init__ called ---")
        if not isinstance(organoid, Organoid):
            print(f"DEBUG: Error - organoid is not an instance of Organoid. Type: {type(organoid)}")
            raise TypeError("organoid must be an instance of pyneurorg.organoid.Organoid.")
        if mea is not None and not isinstance(mea, MEA):
            print(f"DEBUG: Error - mea is not an instance of MEA. Type: {type(mea)}")
            raise TypeError("mea must be an instance of pyneurorg.mea.MEA or None.")
        print(f"DEBUGDEBUG: Found {len(target_neuron_indices_np)} target neurons for electrode {electrode_id}.")

        if len(target_neuron_indices_np) == 0:
            print(f"Warning: No neurons found for stimulus from electrode {electrode_id} in group '{target_group_name}'.")
            return

        # 1. Set the specific boolean flag
        print(f"DEBUG: Setting flag '{current_flag_name}' for indices: {target_neuron_indices_np[:5]}...") # Print first 5
        try:
            # Ensure the entire flag array is boolean and can be set
            if not isinstance(getattr(target_ng, current_flag_name).get_value(), np.ndarray) or \
               getattr(target_ng, current_flag_name).get_value().dtype != bool :
                 print(f"Warning: Flag variable '{current_flag_name}' might not be a boolean array as expected.")
            
            getattr(target_ng, current_flag_name)[:] = False # Reset all for this flag first
            getattr(target_ng, current_flag_name)[target_neuron_indices_np] = True
            print(f"DEBUG: Flag '{current_flag_name}' set successfully.")
        except Exception as e_flag:
            print(f"DEBUG: Error setting flag '{current_flag_name}': {e_flag}")
            traceback.print_exc()
            raise

        # 2. TimedArray in namespace
        ta_name_in_ns = stimulus_waveform.name
        is_generic_name = ta_name_in_ns is None or \
                          ta_name_in_ns.startswith(('_timedarray', 'timedarray'))
        if is_generic_name or \
           (ta_name_in_ns in target_ng.namespace and \
            target_ng.namespace[ta_name_in_ns] is not stimulus_waveform):
            ta_name_in_ns = f'pyneurorg_stim_ta_{self._stimulus_namespace_counter}': Organoid: {organoid.name}, MEA: {mea.name if mea else 'None'}")

        self.organoid = organoid
        self.mea = mea
        self.brian_network = None
        self.monitors = {} 
        
        if brian2_dt is not None:
            if not isinstance(brian2_dt, b2.Quantity) or not (brian2_dt.dimensions == b2.second.dimensions):
                raise TypeError("brian2_dt must be a Brian2 Quantity with time units.")
            self.brian_dt = brian2_dt
            b2.defaultclock.dt = self.brian_dt 
        else:
            self.brian_dt = b2.defaultclock.dt 
        print(f"DEBUG: Simulator dt set to: {self.brian_dt}")
        
        self._network_objects = list(self.organoid.brian2_objects)
        self._stimulus_current_sources = []
        self._stimulus_namespace_counter = 0 
        self._cumulative_stim_vars_reset_added = set()
        print(f"--- DEBUG: Simulator.__init__ finished. self.monitors: {self.monitors} ---")


    def set_mea(self, mea_instance: MEA):
        print(f"--- DEBUG: Simulator.set_mea called with MEA: {mea_instance.name if mea_instance else 'None'} ---")
        if not isinstance(mea_instance, MEA):
            raise TypeError("mea
            self._stimulus_namespace_counter += 1
        target_ng.namespace[ta_name_in_ns] = stimulus_waveform
        print(f"DEBUG: TimedArray '{stimulus_waveform.name}' added to namespace as '{ta_name_in_ns}'.")
        
        # 3. Reset operation for cumulative_stim_var
        reset_op_key = (target_group_name, cumulative_stim_var)
        if reset_op_key not in self._cumulative_stim_vars_reset_added:
            reset_op_name = f'reset__{target_group_name}__{cumulative_stim_var}'
            reset_code = f"{cumulative_stim_var} = 0*amp"
            if target_ng.variables[cumulative_stim_var].dim == (b2.amp/b2.meter**2).dim:
                 reset_code = f"{cumulative_stim_var} = 0*amp/meter**2"
            
            print(f"DEBUG: Creating reset operation '{reset_op_name}' with code: '{reset_code}'")
            reset_operation = target_ng.run_regularly(
                reset_code, dt=self.brian_dt, when='start', order=-1, name=reset_op_name 
            )
            if reset_operation not in self._network_objects:
                self._network_objects.append(reset_operation)
            self._cumulative_stim_vars_reset_added.add(reset_op_key)
            print(f"DEBUG: Added reset operation '{reset_op_name}'.")

        # 4. Code for summing stimulus
        # Standard approach (should work if flag variable is correctly recognized)
        sum_code_if_statement = f"if {current_flag_name} == True:\n    {cumulative_stim_var} = {cumulative_stim_var} + {ta_name_in_ns}(t)"
        
        # Alternative approach (multiplication by boolean)
        sum_code_boolean_mult = f"{cumulative_stim_var} = {cumulative_stim_var} + ({current_flag_name} * {ta_name_in_ns}(t))"

        # --- CHOOSE WHICH sum_code TO TEST ---
        # sum_code_to_test = sum_code_if_statement
        sum_code_to_test = sum_code_boolean_mult # << TRY THIS FIRST TO BYPASS 'if' PARSING ISSUE
        # ---

        print(f"--- DEBUG: sum_code for run_regularly (electrode {electrode_id}) ---")
        print(f"Using flag: '{current_flag_name}'")
        print(f"Using TimedArray in namespace: '{ta_name_in_ns}'")
        print(f"Cumulative variable: '{cumulative_stim_var}'")
        print(f"Generated code string:\n{sum_code_to_test}")
        print(f"repr(sum_code_to_test): {repr(sum_code_to_test)}")
        print("--- END DEBUG SUM_CODE ---")
        
        op_name = f'sum_stim_e{electrode_id}_to_{cumulative_stim_var}_in_{target_group_name}'
        
        try:
            print(f"DEBUG: Attempting to create run_regularly operation '{op_name}'...")
            stim_sum_operation = target_ng.run_regularly(
                sum_code_to_test, 
                dt=self.brian_dt, 
                when='start', 
                order=0,      
                name=op_name
            )
            if stim_sum_operation not in self._network_objects:
                self._network_objects.append(stim_sum_operation)
            self._stimulus_current_sources.append(stimulus_waveform)
            print(f"DEBUG: Summing stimulus operation '{op_name}' added for electrode {electrode_id}.")
        except Exception as e:
            print_instance must be an instance of pyneurorg.mea.MEA.")
        self.mea = mea_instance
        print(f"DEBUG: Simulator MEA successfully set to: {self.mea.name}")


    def add_stimulus(self, electrode_id: int, stimulus_waveform: b2.TimedArray,
                     target_group_name: str, influence_radius,
                     cumulative_stim_var: str = 'I_stimulus_sum',
                     flag_variable_template: str = "stf{id}"):
        print(f"--- DEBUG: Simulator.add_stimulus called: electrode_id={electrode_id}, target_group='{target_group_name}', cumulative_var='{cumulative_stim_var}' ---")
        if self.mea is None: 
            print("DEBUG: Error - MEA not set in Simulator.")
            raise ValueError("No MEA has been set for this simulator.")
        if not isinstance(stimulus_waveform, b2.TimedArray): 
            print(f"DEBUG: Error - stimulus_waveform is not a TimedArray. Type: {type(stimulus_waveform)}")
            raise TypeError("stimulus_waveform must be a TimedArray.")

        try:
            target_ng = self.organoid.get_neuron_group(target_group_name)
            print(f"DEBUG: Target NeuronGroup '{target_ng.name}' found.")
        except KeyError:
            print(f"DEBUG: Error - Target NeuronGroup '{target_group_name}' not found in organoid.")
            raise

        if cumulative_stim_var not in target_ng.variables:
            print(f"DEBUG: Error - Cumulative stim var '{cumulative_stim_var}' not in target_ng variables. Available: {list(target_ng.variables.keys())}")
            raise AttributeError(f"Target NG '{target_group_name}' needs var '{cumulative_stim_var}'.")

        current_flag_name = flag_variable_template.format(id=electrode_id)
        print(f"DEBUG: Generated flag variable name: '{current_flag_name}'")
        if current_flag_name not in target_ng.variables:
            print(f"DEBUG: Error - Flag variable '{current_flag_name}' not in target_ng variables. Available: {list(target_ng.variables.keys())}")
            raise AttributeError(
                f"Target NeuronGroup '{target_group_name}' does not have flag variable '{current_flag_name}'."
            )

        target_neuron_indices_np = self.mea.get_neurons_near_electrode(
            organoid=self.organoid, neuron_group_name=target_group_name,
            electrode_id=electrode_id, radius=influence_radius
        )
        print(f"DEBUG: Neurons near electrode {electrode_id} (radius {influence_radius}): {len(target_neuron_indices_np)} indices - {target_neuron_indices_np[:10] if len(target_neuron_indices_np)>0 else '[]'}...")

        if len(target_neuron_indices_np) == 0:
            print(f"DEBUG: No neurons found for stimulus from electrode {electrode_id}. Aborting add_stimulus for this call.")
            return

        # 1. Set the specific boolean flag
        print(f"DEBUG: Setting flag '{current_flag_name}' for {len(target_neuron_indices_np)} neurons.")
        try:
            getattr(target_ng, current_flag_name)[:] = False # Reset all for this specific flag first
            getattr(target_ng, current_flag_name)[target_neuron_indices_np] = True
            print(f"DEBUG: Flag '{current_flag_name}' successfully set.")
        except Exception as e_flag:
            print(f"DEBUG: Error setting flag '{current_flag_name}': {e_flag}")
            traceback.print_exc()
            raise

        # 2. Ensure TimedArray is in the(f"DEBUG: Error configuring summing run_regularly for stimulus on '{cumulative_stim_var}': {e}")
            traceback.print_exc()
            if ta_name_in_ns in target_ng.namespace and target_ng.namespace[ta_name_in_ns] is stimulus_waveform:
                del target_ng.namespace[ta_name_in_ns]
            raise
        print(f"--- DEBUG [Simulator.add_stimulus]: Finished for electrode {electrode_id} ---")


    def add_recording(self, monitor_name: str, monitor_type: str, target_group_name: str, **kwargs):
        # ... (implementation as before, no debug prints needed here unless issues arise) ...
        if monitor_name in self.monitors:
            raise ValueError(f"Monitor with name '{monitor_name}' already exists.")
        target_group = self.organoid.get_neuron_group(target_group_name)
        monitor_object = None
        brian2_monitor_internal_name = kwargs.pop('name', f"pyb_mon_{monitor_name}_{target_group.name}")
        if monitor_type.lower() == "spike":
            monitor_object = pbg_monitors.setup_spike_monitor(target_group, name=brian2_monitor_internal_name, **kwargs)
        elif monitor_type.lower() == "state":
            if 'variables' not in kwargs: raise KeyError("'variables' (str or list) is required for 'state' monitor.")
            monitor_object = pbg_monitors.setup_state_monitor(target_group, name=brian2_monitor_internal_name, **kwargs)
        elif monitor_type.lower() == "population_rate":
            monitor_object = pbg_monitors.setup_population_rate_monitor(target_group, name=brian2_monitor_internal_name, **kwargs)
        else:
            raise ValueError(f"Unsupported monitor_type: '{monitor_type}'. Supported: 'spike', 'state', 'population_rate'.")
        if monitor_object is not None:
            self.monitors[monitor_name] = monitor_object
            if monitor_object not in self._network_objects: self._network_objects.append(monitor_object)
        return monitor_object

    def build_network(self, **network_kwargs):
        # ... (implementation as before) ...
        self.brian_network = b2.Network(self._network_objects, **network_kwargs)

    def run(self, duration: b2.units.fundamentalunits.Quantity, report=None, report_period=10*b2.second, **run_kwargs):
        # ... (implementation as before) ...
        if not isinstance(duration, b2.Quantity) or not (duration.dimensions == b2.second.dimensions):
            raise TypeError("duration must be a Brian2 Quantity with time units.")
        if self.brian_network is None: self.build_network(**run_kwargs.pop('network_kwargs', {}))
        if self.brian_network is None: raise RuntimeError("Brian2 Network could not be built.")
        self.brian_network.run(duration, report=report, report_period=report_period, **run_kwargs)

    def get_data(self, monitor_name: str):
        # ... (implementation as before) ...
        if monitor_name not in self.monitors: raise KeyError(f"Monitor '{monitor_name}' not found. Available: {list(self.monitors.keys())}")
        return self.monitors[monitor_name]

    def store_simulation(self, filename="pyneurorg_sim_state"):
        # ... (implementation as before) ...
        if self.brian_network is None: print("Warning: Network not built. Nothing to store."); return
        self.brian_network.store(name=filename); print(f"State stored in '{filename}.bri'")

    def restore_simulation(self, filename="pyneurorg_sim_state"):
        # ... (implementation as before) ...
        if self.brian_network is None: print("Warning: Network not explicitly built before restore.")
        b2.restore(name=filename); print(f"State restored from '{filename}.bri'. Network may need rebuild.")
        self.brian_network = None; self.brian_dt = b2.defaultclock.dt

    def __str__(self):
        # ... (implementation as before) ...
        status = "Built" if self.brian_network else "Not Built"; num_monitors = len(self.monitors)
        return (f"<Simulator for Organoid '{self.organoid.name}' "
                f"with {num_monitors} monitor(s). Network Status: {status}>")
    def __repr__(self): return self.__str__()