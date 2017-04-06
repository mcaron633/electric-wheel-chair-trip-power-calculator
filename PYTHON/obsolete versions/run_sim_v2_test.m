%function out = run_sim_v2(data_in, m, target_speed_m_s, Crr, Cd, area, brake_force)
%data format is : lat, long, altitude, distance, gradient

clc
close all
fprintf('\nrunning matlab code\n')

g = 9.81;
rho_air = 1.225;
Crr = 0.005;
Cd = 1;
area = 2;
target_speed_m_s = 4.16;
m = 150;

%controlleur
Kp = 150;
scope_history = 15000;




dat = load('mat_file.mat');
grad_in = dat.input_table_grad_values;
x_in = dat.input_table_x_values * 3.6; % (fucked up when saved)




%data_in = data_in(1:900,:);
%grad_in = data_in(:,5)';
%x_in_m = data_in(:,4)';


x_in_m = (x_in - x_in(1))*1000;

fprintf('\nlast x point in m is : %f \n',x_in_m(length(x_in_m)))


Crr = 0.005;
Cd = 1;
area = 2;
target_speed_m_s = 4.16;
m = 150;
max_allowed_power = 1000;% watts
absolute_min_permanent_speed = 2;% m/s

end_x = x_in_m(length(x_in_m));


max_moving_force = max_allowed_power/absolute_min_permanent_speed; % equivalent to start torque or very steep hill

fmax = max_moving_force;

max_bake_force = 1000; % N

% runs the simulation in the same workspace as the current function
options = simset('SrcWorkspace','current'); 
s = sim('system_sim_v2_test1.slx',[],options);

end_time = sim_time(length(sim_time));

end_time_str = datestr(end_time/(24*60*60), 'HH:MM:SS.FFF');

end_pos = pos_out(length(pos_out));

fprintf('sim end position is : %f m \n', end_pos)

fprintf('\n\nsimulation end travel time : %f s \n\n or HH:MM:SS : %s \n',end_time, end_time_str)



figure
plot(s,speed_out*3.6)
title('speed out')
xlabel('time (s)')
ylabel('speed (km/h)')

figure
plot(s,p_out)
title('power out')
xlabel('time (s)')
ylabel('power (watts)')

out = p_out;
