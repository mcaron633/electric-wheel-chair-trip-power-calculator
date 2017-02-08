# -*- coding: utf-8 -*-
"""

"""

import csv
import numpy as np
import msvcrt as ms
import matplotlib.pyplot as plt
import matlab.engine


# definition of program variables
stats = []
m = 150  # kg
min_speed = 10  # km/h
avg_speed = 15
Crr = 0.005
Cd = 1
area = 1
t_acc = 5
eff = 0.9


def wait_for_enter():
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


def get_trip_stats(dat):

    max_d = np.amax(dat[:, 3])
    max_grad = np.amax(dat[:, 4])
    max_p = np.amax(dat[:, 6])

    return max_d, max_grad, max_p


#def get_travel_time(travel_data, power, m, target_speed):









print '\n\n.......starting program'


def simulink_process(stats):
    ''' uses matlab python package to run analysed data in simulink for dynamic simulation'''
    print '\n starting matlab engine'
    # mat_eng = matlab.engine.start_matlab()


route_data = file_read('route_data.csv', ',')

loc_data = file_read('locations.tsv', '\t')

print '\n\n.......data read'


# find index of location from loc_data in route data (km in route)
route_location_index_list = get_route_loc_index_list(0.000582, loc_data, route_data)

print '\n and loc_data length: %d' % len(loc_data)


# get stats for each section of trip
for i in range(1, 24):

    [data, v_gain, max_alt, dist, max_pos_grad, avg_pos_grad, max_grad_p, avg_p] = get_section_stats(route_location_index_list, route_data, i)
    stats.append([None, v_gain, max_alt, dist, max_pos_grad, avg_pos_grad, max_grad_p])
    simulink_process(stats)


    print 'iteration: %d' % i
    print v_gain
    print max_alt
    print dist
    print max_pos_grad
    print avg_pos_grad
    #  plot_section(data)


a_stats = np.array(stats, dtype='float64')
[max_d, max_grad, max_p] = get_trip_stats(a_stats)

print '\n\n max distance : %.3f' % max_d
print ' max gradient : %.3f' % max_grad
print' max power : %.3f' % max_p


wait_for_enter()



