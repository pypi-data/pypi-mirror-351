# No seu Notebook de Teste:
stim_flag_simulator.add_stimulus(
    electrode_id=target_electrode_id_1,
    stimulus_waveform=stimulus_pulse_train_1,
    target_group_name=neuron_group_id_test,
    influence_radius=stim_influence_radius_1,
    cumulative_stim_var='I_stimulus_sum',
    flag_variable_template="stf{id}" # Garanta que isso corresponda ao que neuron_models.py gera
                                    # ou omita se o padrão em add_stimulus for "stf{id}"
)