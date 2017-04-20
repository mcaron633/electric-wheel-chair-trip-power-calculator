load('wrkspc_no_13.mat')

options = simset('SrcWorkspace','current');
s = sim('system_sim',[],options);


close all
plot(pos_out/1000,p_out_positive)
title('Puissance entree en fonction de la position')
xlabel('position (km)')
ylabel('puissance (Watts)')

figure
plot(pos_out/1000,p_out_positive_real)
title('Puissance de sortie en fonction de la position')
xlabel('position (km)')
ylabel('puissance (Watts)')

figure()
plot((x_in - x_in(1))/1000,grad_in)
title('Gradient de pente en fonction de la position')
xlabel('position (km)')
ylabel('Gradient %')

figure()
plot(pos_out/1000,speed_out*3.6)
title('Vitesse en fonction de la position')
xlabel('position (km)')
ylabel('Vitesse (km/h)')

figure()
plot(pos_out/1000,current_in)
title('Courant en fonction de la position')
xlabel('position (km)')
ylabel('Courant (Amperes)')

figure()
plot(pos_out/1000,inst_spent_energy)
title('Energie en fonction de la position')
xlabel('position (km)')
ylabel('Energie (J)')

figure()
plot(pos_out/1000,charge_in_a_h)
title('Charge en fonction de la position')
xlabel('position (km)')
ylabel('Charge A-h')

figure()
plot(pos_out/1000,avg_current)
title('Courant moyen en fonction de la position')
xlabel('position (km)')
ylabel('Courant A')

