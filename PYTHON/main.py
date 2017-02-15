# -*- coding: utf-8 -*-
"""

"""

import csv
import numpy as np
import msvcrt as ms
import matplotlib.pyplot as plt
import matlab.engine
import struct

eng = matlab.engine.start_matlab()

# definition of program variables
stats = []
path_sections_stats = []
path_sections_data = []
m = 150.0  # kg
min_speed = 10.0  # km/h
avg_speed = 15.0
Crr = 0.005
Cd = 1.0
area = 2.0
t_acc = 5.0
eff = 0.9
t_decc = 1.0 # stopping time for 30 km/h to 0


def script_end():
    print 'press enter to continue'
    ms.getch()


def file_read(csv_file_name, dl):

    out = []

    with open(csv_file_name) as csvfile:
        data_reader = csv.reader(csvfile, delimiter=dl)

        for row in data_reader:
            out.append(row)

        out.pop(0)

    return out


def get_route_loc_index_list(precision, loc_data, route_data):

    route_location_index = []
    j = 0
    k = 0
    l = 1

    while l < len(loc_data):

        route_location_index = []

        for row_loc in loc_data:
            i = 0

            for row_route in route_data:
                j += 1

                try:
                    test = (np.sqrt((float(row_route[0]) - float(row_loc[1])) ** 2 + (float(row_route[1]) - float(row_loc[2])) ** 2)) < precision

                except Exception as e:
                    print e
                    k += 1

                if test:
                    route_location_index.append([row_loc[0], i])
                    break

                i += 1

        l = len(route_location_index)
        print '\n\nprecision: %f' % precision
        print 'current list size: ' + str(l)

        
        precision *= 1.25

    return route_location_index


def calculate_power(m, speed_kmh, grad, Crr, Cd, area, t_acceleration):
    speed_ms = speed_kmh / 3.6

    g = 9.81  # m/s^2
    rho_air = 1.225  # kg/m^3

    a = speed_ms / t_acceleration
    theta = np.arctan(grad/100)

    w = m*g
    f_n = w * np.cos(theta)
    f_g = w * np.sin(theta)
    f_i = m * a
    f_rr = f_n * Crr
    f_aero_drag = Cd * area * rho_air * (speed_ms**2)/2

    f_motion = f_i + f_rr + f_aero_drag + f_g

    power = f_motion * speed_ms

    return power  # don't forget to consider mechanical efficiency


def get_section_stats(index_list, rt_data, stop_number):
    ''' using the stop number in stops list, will give stats of each section of trip
    data format is : lat, long, altitude, distance, gradient'''

    data_start = index_list[stop_number-1][1]
    data_end = index_list[stop_number][1]
    print '\ndataset start index : %d' % data_start
    print 'dataset end index : %d' % data_end

    data_r = rt_data[data_start:data_end]
    section_data = np.array(data_r, dtype='float64')

    past_alt = section_data[0, 2]
    vertical_gain = 0

    for i in range(0, len(section_data)):
        current_alt = section_data[i, 2]

        if i == 0:
            continue

        elif current_alt > past_alt:

            vertical_gain += (current_alt - past_alt)

        past_alt = current_alt

    distance = section_data[-1, 3] - section_data[0, 3]
    max_positive_gradient = np.amax(section_data[:, 4])
    avg_positive_gradient = 100 * vertical_gain / (distance * 1000)  # reminder: it's a percentage
    max_altitude = np.amax(section_data[:, 2])

    max_grad_power = calculate_power(150, 10, max_positive_gradient, 0.005, 1, 1, 5)
    avg_power = calculate_power(150, 15, avg_positive_gradient, 0.005, 1, 1, 5)

    return section_data, vertical_gain, max_altitude, distance, max_positive_gradient, avg_positive_gradient, max_grad_power, avg_power


def plot_section(plt_data):
    fig = plt.figure()
    fig.add_subplot(1, 1, 1)

    x = plt_data[:, 3]
    y = plt_data[:, 2]

    plt.plot(x, y)
    plt.show()

    return


def get_trip_stats(dat_in):
    dat = np.array(dat_in, dtype='float64')

    max_d = np.amax(dat[:, 3])
    max_grad = np.amax(dat[:, 4])
    max_p = np.amax(dat[:, 6])

    return max_d, max_grad, max_p


def simulink_leg_sim(i, data_in, eng, m, target_speed, Crr, Cd, area, brake_force, max_allowed_power, absolute_min_permanent_speed_m_s):
    ''' uses matlab python package to run analysed data in simulink for dynamic simulation
    format of data in shoud be : lat, long, altitude, distance, gradient'''

    class trip_section:
        dat = []
        t_speed_m_s = 0
        inst_energy = []
        p_out_pos = []
        p_out = []
        speed_out_km_h = []
        sim_time = []
        s = []
        i = 0
        x_out = []

    print '\nstarting matlab engine'

    data_in = matlab.double(data_in)
    target_speed_m_s = target_speed / 3.6

    section = trip_section()

    [pos_out, inst_spent_energy, p_out_positive, p_out, speed_out_km_h, sim_time, s] = eng.run_sim_v2(data_in, m, max_allowed_power, absolute_min_permanent_speed_m_s, target_speed_m_s, Crr, Cd, area, brake_force)
    section.dat = data_in
    section.t_speed_m_s = target_speed_m_s
    section.inst_energy = inst_spent_energy
    section.p_out_pos = p_out_positive
    section.p_out = p_out
    section.speed_out_km_h = speed_out_km_h
    section.sim_time = sim_time
    section.s = s
    section.i = i
    section.x_out = pos_out


    print '\nsim done'

    return section


# main code section ----------------------------------------------------------------------------------------------------

print '\n\n.......starting program'

route_data = file_read('route_data.csv', ',')
loc_data = file_read('locations.tsv', '\t')

print '\n\n.......data read'


# find index of location from loc_data in route data (km in route)
route_location_index_list = get_route_loc_index_list(0.000582, loc_data, route_data)

print '\n and loc_data length: %d' % len(loc_data)


# get stats for each section of trip
for i in range(1, 24):

    [data, v_gain, max_alt, dist, max_pos_grad, avg_pos_grad, max_grad_p, avg_p] = get_section_stats(route_location_index_list, route_data, i)
    path_sections_stats.append([None, v_gain, max_alt, dist, max_pos_grad, avg_pos_grad, max_grad_p])
    path_sections_data.append(data.tolist())

    print 'iteration: %d' % i
    print v_gain
    print max_alt
    print dist
    print max_pos_grad
    print avg_pos_grad
    print '\n\n'


[max_d, max_grad, max_p] = get_trip_stats(path_sections_stats)

print '\n\n'
print 'max distance : %.3f' % max_d
print 'max gradient : %.3f' % max_grad
print 'max power : %.3f' % max_p
print 'running Matlab sim \n'

brake_force = 1000.0
max_power = 1000.0
min_uphill_speed = 2.0


manual = 1
test = input('do you want to do automatic testing ? 1 for yes, 0 for no ')

if test == 1:

    for i in range(0, 23):

        index_of_sim_section = i
        d = path_sections_data[index_of_sim_section]

        print 'number of legs in trip (stops - 1): %d \n' % len(path_sections_data)
        print 'number of simulated section: %d \n' % (index_of_sim_section + 1)
        print 'length of data in : %d\n' % len(path_sections_data[index_of_sim_section])

        section = simulink_leg_sim(i, d, eng, m, 15.0, Crr, Cd, area, brake_force, max_power, min_uphill_speed)
        print 'length of data out  : %d\n' % len(section.x_out)

else:

    index_of_sim_section = input('index of section you want to test')
    print 'manual testing'
    d = path_sections_data[index_of_sim_section]

    print 'number of legs in trip (stops - 1): %d \n' % len(path_sections_data)
    print 'number of simulated section: %d \n' % (index_of_sim_section + 1)
    print 'length of data in : %d\n' % len(path_sections_data[index_of_sim_section])

    out = simulink_leg_sim(d, eng, m, 15.0, Crr, Cd, area, brake_force, max_power, min_uphill_speed)
    print 'length of data out  : %d\n' % len(out)
    manual = input('do you want to continue : 1 for yes, 0 for no')

script_end()
