function out = run_sim(data_in, m, target_speed_m_s, Crr, Cd, area)
    %data format is : lat, long, altitude, distance, gradient
    fprintf('\n running matlab code')
    
    g = 9.81;
    rho_air = 1.225;
    travel_speed = target_speed_m_s;
    input_table_x_values = data_in(1:900,4)';
    input_table_x_values = (input_table_x_values - input_table_x_values(1))/3.6;
    input_table_grad_values = data_in(1:900,5)';

    save('mat_file.mat','input_table_x_values', 'input_table_grad_values')


    % runs the simulation in the same workspace as the current function
    options = simset('SrcWorkspace','current'); 
    s = sim('system_sim.slx',[],options);

    out = [0,1];
    out = simout;

    %  disp(input_table_x_values)


    figure
    plot(s,out)
    title('simout')

    %figure
    %plot(s,ramp)

    %figure
    %plot(input_table_x_values)
    %title('x du parcours')

    %figure
    %plot(input_table_grad_values)
    %title('grad du parcours')

    %figure
    %plot(s, kout)
    %title('k out (x - la fraction)')


    %figure
    %plot(s, fout)
    %title('fraction entre les 2 pts de x')

    %figure
    %plot(s, x_pos)
    %title('evolution de la positon de x durant la sim')



end