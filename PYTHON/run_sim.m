function out = run_sim(data_in, m, target_speed_m_s, Crr, Cd, area)
%data format is : lat, long, altitude, distance, gradient

g=9.81;
rho_air = 1.225;
travel_speed = target_speed_m_s;

fprintf('\n running matlab code')
input_table_x_values = data_in(1:900,4)';
input_table_x_values = input_table_x_values - input_table_x_values(1)
input_table_grad_values = data_in(1:900,5)';


options = simset('SrcWorkspace','current');
s=sim('system_sim_test1.slx',[],options);

out = [0,1]  %simout;
out = simout

%disp(input_table_x_values)


figure
plot(s,out)
figure
plot(s,ramp)

figure
plot(input_table_x_values)

figure
plot(input_table_grad_values)

figure
plot(kout)


figure
plot(fout)

figure
plot(x_pos)

end