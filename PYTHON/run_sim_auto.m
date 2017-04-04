function out = run_sim_v2(data_in, m, max_allowed_power, absolute_min_permanent_speed, target_speed_m_s, Crr, Cd, area, brake_force, Kp,acc_time, wheel_radius)
%data format is : lat, long, altitude, distance, gradient

clc
fprintf('\nrunning matlab code\n')

g = 9.81;
rho_air = 1.225;

%controlleur
% Kp = 150;
scope_history = 15000;
data_in_len = length(data_in(:,1));

x_in_temp = data_in(:,4)';

fprintf('\nparsing for dx = 0\n')
for i = 2: data_in_len
    dx(i-1) = x_in_temp(i) - x_in_temp(i-1);
end
z_val_indexes = find(dx==0);
dx(z_val_indexes) = [];

fprintf('\n%d points removed',length(z_val_indexes))

grad_in = data_in(:,5)';
x_in = data_in(:,4)';

x_in(z_val_indexes) = [];
grad_in(z_val_indexes) = [];

x_in_m = (x_in - x_in(1))*1000;

%figure
%plot(dx)
%title('dx')
%xlabel('index')
%ylabel('dx in m')


fprintf('\nlast x point in m is : %f \n',x_in_m(length(x_in_m)))

end_x = x_in_m(length(x_in_m));

max_moving_force = max_allowed_power/absolute_min_permanent_speed; % equivalent to start torque or very steep hill

fmax = max_moving_force;

max_brake_force = brake_force; % N
slope = target_speed_m_s/acc_time;

% OPTIONAL : SAVE VARIABLES TO WORKSPACE FOR SEPARATE SIMULINK TEST, DEV AND DEBUG

%save('test_workspace')



% runs the simulation in the same workspace as the current function
options = simset('SrcWorkspace','current');
s = sim('system_sim',[],options);

speed_out_km_h = speed_out * 3.6;

out = struct('inst_spent_energy', inst_spent_energy, 'p_out', p_out,...
    'p_out_positive', p_out_positive, 'speed_out_km_h',speed_out_km_h,'pos_out',pos_out, ...
    'sim_time', sim_time, 's', s, 'force_out', force_out);

