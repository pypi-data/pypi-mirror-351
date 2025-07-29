# src/pyneurorg/core/neuron_models.py

"""
Collection of predefined neuron models for use with Brian2 in pyneurorg simulations.

Each function in this module returns a dictionary containing the necessary
components (equations, parameters, threshold, reset conditions, refractory period,
and integration method) to define a `brian2.NeuronGroup`.

All models include 'I_synaptic : amp' and 'I_stimulus_sum : amp' to allow for
separate inputs from synaptic connections and external stimuli (like MEA).
They also include boolean flags 'stim_target_flagX : boolean' for targeted stimulation.
"""

import brian2 as b2

def _add_stimulus_components_to_model(base_eqs, base_namespace, num_stimulus_flags=16):
    """
    Appends stimulus summation current and boolean flags to model equations
    and corresponding default initializers to the namespace.

    Parameters
    ----------
    base_eqs : str
        The base model equations string.
    base_namespace : dict
        The base namespace dictionary for the model.
    num_stimulus_flags : int, optional
        Number of boolean stimulus flags to create (e.g., stim_target_flag0, stim_target_flag1).
        (default: 16)

    Returns
    -------
    tuple
        (full_eqs_str, updated_namespace_dict)
    """
    # Define common current inputs if not already implied by base_eqs structure
    # These will be summed into a total current if the base model uses such a variable.
    # Or, the base model should be modified to use these directly.
    stimulus_component_eqs = [
        "I_stimulus_sum : amp # Sum of all external timed stimuli for this neuron",
        "I_synaptic : amp     # Sum of all synaptic currents for this neuron"
    ]
    
    flag_eqs_list = []
    default_flags_init = {}
    for i in range(num_stimulus_flags):
        flag_name = f"stim_target_flag{i}" # New flag naming convention
        flag_eqs_list.append(f"{flag_name} : boolean")
        default_flags_init[f"{flag_name}_default_init"] = False 

    # Combine base equations with new components
    # Check if base_eqs already defines these, to avoid duplication if models are refactored later
    final_eqs_parts = [base_eqs]
    if "I_stimulus_sum : amp" not in base_eqs:
        final_eqs_parts.append(stimulus_component_eqs[0])
    if "I_synaptic : amp" not in base_eqs:
        final_eqs_parts.append(stimulus_component_eqs[1])
    final_eqs_parts.extend(flag_eqs_list)
    
    full_eqs = "\n".join(final_eqs_parts)
    
    updated_namespace = base_namespace.copy()
    # Add default initializers for current terms if not specified by model's base_namespace
    if 'I_stimulus_sum_default_init' not in updated_namespace:
        updated_namespace['I_stimulus_sum_default_init'] = 0*b2.amp
    if 'I_synaptic_default_init' not in updated_namespace:
        updated_namespace['I_synaptic_default_init'] = 0*b2.amp
    updated_namespace.update(default_flags_init)
    
    return full_eqs, updated_namespace


def LIFNeuron(tau_m=10*b2.ms, v_rest=0*b2.mV, v_reset=0*b2.mV,
              v_thresh=20*b2.mV, R_m=100*b2.Mohm, I_tonic=0*b2.nA,
              refractory_period=2*b2.ms, num_stimulus_flags=16):
    """
    Defines a Leaky Integrate-and-Fire (LIF) neuron model with stimulus capabilities.
    """
    base_eqs = """
    dv/dt = (-(v - v_rest_val) + R_m_val * (I_synaptic + I_stimulus_sum + I_tonic_val)) / tau_m_val : volt (unless refractory)
    """
    base_namespace = {
        'tau_m_val': tau_m, 'v_rest_val': v_rest, 'R_m_val': R_m, 'I_tonic_val': I_tonic,
        'v_default_init': v_rest,
    }
    full_eqs, full_namespace = _add_stimulus_components_to_model(
        base_eqs, base_namespace, num_stimulus_flags
    )
    return {
        'model': full_eqs, 'threshold': f'v > {v_thresh!r}', 'reset': f'v = {v_reset!r}',
        'refractory': refractory_period, 'namespace': full_namespace, 'method': 'exact'
    }


def IzhikevichNeuron(a=0.02/b2.ms, b=0.2*b2.nS, c=-65*b2.mV, d=2*b2.pA,
                     v_init=-70*b2.mV, u_init=None, C_m=100*b2.pF,
                     k=0.7*b2.nS/b2.mV, v_rest_iz=-60*b2.mV, v_thresh_iz=-40*b2.mV,
                     v_peak=30*b2.mV, I_tonic=0*b2.pA, num_stimulus_flags=16):
    """ Defines an Izhikevich neuron model with stimulus capabilities. """
    u_init_val = b * (v_init - v_rest_iz) if u_init is None else u_init
    base_eqs = """
    dv/dt = (k_val * (v - v_rest_iz_val) * (v - v_thresh_iz_val) - u + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt
    du/dt = a_val * (b_val * (v - v_rest_iz_val) - u) : amp / second 
    """
    base_namespace = {
        'a_val': a, 'b_val': b, 'k_val': k, 'C_m_val': C_m,
        'v_rest_iz_val': v_rest_iz, 'v_thresh_iz_val': v_thresh_iz,
        'I_tonic_val': I_tonic, 'v_default_init': v_init, 'u_default_init': u_init_val,
    }
    full_eqs, full_namespace = _add_stimulus_components_to_model(
        base_eqs, base_namespace, num_stimulus_flags
    )
    return {
        'model': full_eqs, 'threshold': f'v >= {v_peak!r}',
        'reset': f'v = {c!r}; u += {d!r}',
        'namespace': full_namespace, 'method': 'euler'
    }


def AdExNeuron(C_m=281*b2.pF, g_L=30*b2.nS, E_L=-70.6*b2.mV,
               V_T=-50.4*b2.mV, Delta_T=2*b2.mV, tau_w=144*b2.ms,
               a_adex=4*b2.nS, b_adex=0.0805*b2.nA, V_reset=-70.6*b2.mV, # Renamed params to avoid conflict
               V_peak=0*b2.mV, I_tonic=0*b2.nA, refractory_period=0*b2.ms,
               num_stimulus_flags=16):
    """ Defines an Adaptive Exponential I&F (AdEx) neuron model with stimulus capabilities. """
    base_eqs = """
    dv/dt = (g_L_val * (E_L_val - v) + g_L_val * Delta_T_val * exp((v - V_T_val)/Delta_T_val) - w + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt (unless refractory)
    dw/dt = (a_adex_val * (v - E_L_val) - w) / tau_w_val : amp (unless refractory)
    """
    base_namespace = {
        'C_m_val': C_m, 'g_L_val': g_L, 'E_L_val': E_L, 'V_T_val': V_T,
        'Delta_T_val': Delta_T, 'tau_w_val': tau_w, 'a_adex_val': a_adex,
        'I_tonic_val': I_tonic, 'v_default_init': E_L, 'w_default_init': 0*b2.nA,
    }
    full_eqs, full_namespace = _add_stimulus_components_to_model(
        base_eqs, base_namespace, num_stimulus_flags
    )
    return {
        'model': full_eqs, 'threshold': f'v > {V_peak!r}',
        'reset': f'v = {V_reset!r}; w += {b_adex!r}',
        'refractory': refractory_period, 'namespace': full_namespace, 'method': 'euler'
    }


def QIFNeuron(tau_m=20*b2.ms, v_rest=0*b2.mV, v_c=10*b2.mV, # v_c is v_critical
              v_reset=-10*b2.mV, v_peak=30*b2.mV, R_m=100*b2.Mohm,
              I_tonic=0*b2.nA, refractory_period=1*b2.ms, num_stimulus_flags=16):
    """ Defines a Quadratic Integrate-and-Fire (QIF) neuron model with stimulus capabilities. """
    base_eqs = """
    dv/dt = ( (v - v_rest_val) * (v - v_critical_val) / (1*volt) + R_m_val * (I_synaptic + I_stimulus_sum + I_tonic_val) ) / tau_m_val : volt (unless refractory)
    """
    base_namespace = {
        'tau_m_val': tau_m, 'v_rest_val': v_rest, 'v_critical_val': v_c,
        'R_m_val': R_m, 'I_tonic_val': I_tonic, 'v_default_init': v_rest,
    }
    full_eqs, full_namespace = _add_stimulus_components_to_model(
        base_eqs, base_namespace, num_stimulus_flags
    )
    return {
        'model': full_eqs, 'threshold': f'v >= {v_peak!r}',
        'reset': f'v = {v_reset!r}', 'refractory': refractory_period,
        'namespace': full_namespace, 'method': 'euler'
    }


def SimpleHHNeuron(C_m=1*b2.uF/b2.cm**2, E_Na=50*b2.mV, E_K=-77*b2.mV, E_L=-54.4*b2.mV,
                   g_Na_bar=120*b2.mS/b2.cm**2, g_K_bar=36*b2.mS/b2.cm**2, g_L_bar=0.3*b2.mS/b2.cm**2,
                   V_T_hh=-60*b2.mV, I_tonic=0*b2.uA/b2.cm**2, refractory_period=0*b2.ms,
                   num_stimulus_flags=16):
    """ Defines a simplified Hodgkin-Huxley (HH) model with stimulus capabilities.
    Currents (I_synaptic, I_stimulus_sum, I_tonic_val) must be current densities (A/m^2).
    """
    numerical_spike_threshold = 0*b2.mV
    base_eqs = """
    dv/dt = (I_Na + I_K + I_L + I_synaptic + I_stimulus_sum + I_tonic_val) / C_m_val : volt (unless refractory)
    I_Na = g_Na_bar_val * m**3 * h * (E_Na_val - v) : amp/meter**2
    dm/dt = alpha_m * (1-m) - beta_m * m : 1
    dh/dt = alpha_h * (1-h) - beta_h * h : 1
    alpha_m = (0.1/mV) * (v - (V_T_hh_val + 25*mV)) / (1 - exp(-(v - (V_T_hh_val + 25*mV))/(10*mV))) / ms : Hz
    beta_m = (4.0) * exp(-(v - (V_T_hh_val + 0*mV))/(18*mV)) / ms : Hz
    alpha_h = (0.07) * exp(-(v - (V_T_hh_val + 0*mV))/(20*mV)) / ms : Hz
    beta_h = (1.0) / (1 + exp(-(v - (V_T_hh_val + 30*mV))/(10*mV))) / ms : Hz
    I_K = g_K_bar_val * n**4 * (E_K_val - v) : amp/meter**2
    dn/dt = alpha_n * (1-n) - beta_n * n : 1
    alpha_n = (0.01/mV) * (v - (V_T_hh_val + 10*mV)) / (1 - exp(-(v - (V_T_hh_val + 10*mV))/(10*mV))) / ms : Hz
    beta_n = (0.125) * exp(-(v - (V_T_hh_val + 0*mV))/(80*mV)) / ms : Hz
    I_L = g_L_bar_val * (E_L_val - v) : amp/meter**2
    """
    base_namespace = {
        'C_m_val': C_m, 'E_Na_val': E_Na, 'E_K_val': E_K, 'E_L_val': E_L,
        'g_Na_bar_val': g_Na_bar, 'g_K_bar_val': g_K_bar, 'g_L_bar_val': g_L_bar,
        'V_T_hh_val': V_T_hh, 'I_tonic_val': I_tonic,
        'v_default_init': E_L, 'm_default_init': 0.05, 'h_default_init': 0.6, 'n_default_init': 0.32,
    }
    
    full_eqs, full_namespace = _add_stimulus_components_to_model(
        base_eqs, base_namespace, num_stimulus_flags
    )
    # Adjust units for HH model's current densities if helper added them as 'amp'
    if "I_synaptic : amp" in full_eqs:
        full_eqs = full_eqs.replace("I_synaptic : amp", "I_synaptic : amp/meter**2")
        full_namespace['I_synaptic_default_init'] = 0*b2.uA/b2.cm**2
    if "I_stimulus_sum : amp" in full_eqs:
        full_eqs = full_eqs.replace("I_stimulus_sum : amp", "I_stimulus_sum : amp/meter**2")
        full_namespace['I_stimulus_sum_default_init'] = 0*b2.uA/b2.cm**2

    return {
        'model': full_eqs, 'threshold': f'v > {numerical_spike_threshold!r}', 'reset': '', 
        'refractory': refractory_period, 'namespace': full_namespace,
        'method': ('exponential_euler', {'simplify': True, 'split_వ': True})
    }