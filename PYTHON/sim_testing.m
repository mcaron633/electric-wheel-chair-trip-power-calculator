
clc
clear

load('test_workspace')

fprintf('\nlast x point in m is : %f \n',x_in_m(length(x_in_m)))

scope_history = 85/15*3600/0.1 *1.1;

% runs the simulation in the same workspace as the current function
options = simset('SrcWorkspace','current');
s = sim('system_sim',[],options);

speed_out_km_h = speed_out * 3.6;

out = struct('inst_spent_energy', inst_spent_energy, 'p_out', p_out,...
    'p_out_positive', p_out_positive, 'speed_out_km_h',speed_out_km_h,'pos_out',pos_out, ...
    'sim_time', sim_time, 's', s, 'force_out', force_out);

