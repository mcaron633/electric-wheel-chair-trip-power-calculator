%function out = run_sim(data_in, m, target_speed_m_s, Crr, Cd, area)
%data format is : lat, long, altitude, distance, gradient
clc
clear % do not do in function
close all
fprintf('\n running matlab code\n')

g = 9.81;
rho_air = 1.225;

dat = load('mat_file.mat');
grad_in = dat.input_table_grad_values;
x_in_m = dat.input_table_x_values*1000;

Crr = 0.005;
Cd = 1;
area = 2;
target_speed_m_s = 4.16;
m = 150;


% runs the simulation in the same workspace as the current function
options = simset('SrcWorkspace','current'); 
s = sim('system_sim_test2.slx',[],options);



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
