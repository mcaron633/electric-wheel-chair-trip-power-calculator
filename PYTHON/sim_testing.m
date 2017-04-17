
clc
clear

load('test_workspace')

fprintf('\nlast x point in m is : %f \n',x_in_m(length(x_in_m)))




scope_history = 20000;
Kp = 700;
Kp_braking = 200;
max_allowed_power = 1000;
m = 210;
area = 1.2;
Cd = 0.6; % hummer h2 truck at 0.57, so this value should be more than conservative
eff_data = load('efficiency_curve_24v.txt');



input_rpm_vals = eff_data(:,1);
eff_vals = eff_data(:,2);



% runs the simulation in the same workspace as the current function
options = simset('SrcWorkspace','current');
s = sim('system_sim',[],options);

speed_out_km_h = speed_out * 3.6;

out = struct('inst_spent_energy', inst_spent_energy, 'p_out', p_out,...
    'p_out_positive', p_out_positive, 'speed_out_km_h',speed_out_km_h,'pos_out',pos_out, ...
    'sim_time', sim_time, 's', s, 'force_out', force_out);

