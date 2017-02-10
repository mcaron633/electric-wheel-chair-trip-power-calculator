function out = main_labo4_part3()


k=1;

%moteur
kmm=0.08253;
kbm=0.08735;
lam=0.0033;
ram=1.445;

bmm=0.00006111;
jmm=0.0000532;
jpoulie=1.80E-06;

%gen
kmg=0.08267;
kbg=0.08735;
lag=0.0033;
rag=1.245;
bmg=0.00006111;
jmg=0.0000434;

r=2;
c=24*10^-3;
Ka = 2;
Kp = 1.75;
Ki = 60;
Kd = 0;
jeq= jmg+jmm +jpoulie*2;


fileToRead1 = 'q4e2.txt';
[temps_test, consigne_test, VDaqOut, sortie_test] = conversion_fichier(fileToRead1);

Vmoteur_test = VDaqOut*2;


consigne = consigne_test;

options = simset('SrcWorkspace','current');

%Rouler la sim
s1=sim('Simulation_labo4_r2015a.slx',[],options);



out =v_in_moteur;

plot(out)
end


