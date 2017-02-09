function out = run_sim(data_in, m, target_speed_m_s, Crr, Cd, area)
%data format is : lat, long, altitude, distance, gradient
g=9.81;
rho_air = 1.225;
travel_speed = target_speed_m_s;

fprintf('\n running matlab code')
input_table_x_values = data_in(:,4)
input_table_grad_values = data_in(:,5);

sim_out = sim('system_sim.slx');

out = [0,1];

disp(input_table_x_values)

end