# -*- coding: utf-8 -*-
"""

"""

import csv
import numpy as np
import msvcrt as ms
import matplotlib.pyplot as plt
import matlab.engine
import struct
import xlwt

eng = matlab.engine.start_matlab()
# eng.eval('close all')

# definition of program variables
stats = []
path_sections_stats = []
path_sections_data = []
energy = []
max_output_power = []
speed_out = []
x_out = []
force_out = []
s_time = []


m = 150.0  # kg
min_speed = 10.0  # km/h
eff = 0.9
t_decc = 1.0 # stopping time for 30 km/h to 0

min_uphill_speed = 2.0
motor_input_Voltage = 48.0


class tripSectionClass:
    def __init__(self):
        self.dat = []
        self.tar_speed_m_s = 15.0/3.6
        self.inst_energy = []
        self.p_out = []
        self.p_out_pos = []
        self.speed_out_km_h = []
        self.sim_time = []
        self.s = []
        self.i = 0
        self.x_out = []
        self.m = 150.0
        self.Crr = 0.005
        self.Cd = 1.0
        self.area = 2.0
        self.brake_force = 1000.0
        self.max_allowed_power = 1000.0
        self.min_uphill_speed = 1.5 # lower gives more torque
        self.force_out = []
        self.Kp = 150.0
        self.t_acc = 5.0
        self.wheel_radius = 0.2538 # m


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


def plot_section_xy(x, y, title):
    fig = plt.figure()
    fig.add_subplot(1, 1, 1)

    plt.plot(x, y)
    plt.title(title)
    plt.show()

    return


def plot_section_output(energy ,power, speed, position, force_out, time):

    x = time
    y = energy
    plot_section_xy(x, y,'energy')

    y = power
    plot_section_xy(x, y,'power')

    y = speed
    plot_section_xy(x, y,'speed')

    y = position
    plot_section_xy(x, y,'position')

    y = force_out
    plot_section_xy(x, y,'force_out')

    return


def print_section_output_stats(nrgy ,power, speed, position, frc_out, time, motor_tension):

    a_speed = np.mean(speed)
    print 'avg speed is : %.3f' % a_speed

    max_speed = np.amax(speed)
    print 'max speed is : %.3f' % max_speed

    min_speed = np.amin(speed)
    print 'min speed is : %.3f' % min_speed

    max_power_out = np.amax(power)
    print 'max power out is : %.3f' % max_power_out

    total_distance_travelled = np.amax(position)
    print 'total distance is : %.3f' % total_distance_travelled

    end_time = np.amax(time)
    print 'travel time is : %.3f' % end_time

    total_energy_output = np.amax(nrgy)
    print 'total energy output is : %.3f' % total_energy_output

    battery_req_charge = np.amax(np.array(nrgy))/(motor_tension * 3600.0)
    print 'battery req charge is : %.3f Ampere-hours' % battery_req_charge

    max_out_force = np.amax(frc_out)
    print 'max force out is : %.3f' % max_out_force


def get_trip_stats(dat_in):
    dat = np.array(dat_in, dtype='float64')

    max_d = np.amax(dat[:, 3])
    max_grad = np.amax(dat[:, 4])
    max_p = np.amax(dat[:, 6])

    return max_d, max_grad, max_p


def con_ml_db_tolist(dat_in):
    arr = np.array(dat_in)
    out = (arr[:, 0]).tolist()
    return out


def simulink_leg_sim(sectionClIn, eng):
    ''' uses matlab python package to run analysed data in simulink for dynamic simulation
    format of data in shoud be : lat, long, altitude, distance, gradient'''

    print '\nstarting matlab engine'

    data_in = matlab.double(sectionClIn.dat)
    target_speed_m_s = sectionClIn.tar_speed_m_s

    out_ml = eng.run_sim_auto(data_in, sectionClIn.m, sectionClIn.max_allowed_power, sectionClIn.min_uphill_speed,
                            target_speed_m_s, sectionClIn.Crr, sectionClIn.Cd, sectionClIn.area,
<<<<<<< HEAD
                            sectionClIn.brake_force, sectionClIn.Kp, sectionClIn.t_acc, sectionClIn.wheel_radius)
=======
                            sectionClIn.brake_force, sectionClIn.Kp, sectionClIn.t_acc)
>>>>>>> origin/master

    sectionClIn.inst_energy = con_ml_db_tolist(out_ml['inst_spent_energy'])
    sectionClIn.p_out_pos = con_ml_db_tolist(out_ml['p_out_positive'])
    sectionClIn.p_out = con_ml_db_tolist(out_ml['p_out'])
    sectionClIn.speed_out_km_h = con_ml_db_tolist(out_ml['speed_out_km_h'])
    sectionClIn.sim_time = con_ml_db_tolist(out_ml['sim_time'])
    sectionClIn.s = con_ml_db_tolist(out_ml['s'])
    sectionClIn.x_out = con_ml_db_tolist(out_ml['pos_out'])
    sectionClIn.force_out = con_ml_db_tolist(out_ml['force_out'])


    print '\nsim done'

    return sectionClIn


def call_section_sim(eng, i, path_sections_data, section_cl):

    print 'number of legs in trip (stops - 1): %d \n' % len(path_sections_data)
    print 'number of simulated section: %d \n' % (i + 1)
    print 'length of data in : %d\n' % len(path_sections_data[i])

    section_cl.dat = path_sections_data[i]
    section_cl.tar_speed_m_s = 15.0 / 3.6
    section_cl.i = i
    section_cl = simulink_leg_sim(section_cl, eng)

    print 'length of data out  : %d\n' % len(section_cl.x_out)

    return section_cl


def complete_data_summary(nrgy_l ,power_l, speed_l, position_l, frc_out_l, trip_time_list, motor_tension):

    # get single data to eval :

    a_speed = []
    max_speed = []
    min_speed = []
    max_power_out = []
    total_distance_travelled = []
    end_time = []
    total_energy_output = []
    battery_req_charge = []
    max_out_force = []

    sections_testing_range = range(0,len(trip_time_list))

    for i in sections_testing_range:
        end_time.append(np.amax(trip_time_list[i]))

        a_speed.append(np.mean(speed_l[i]))
        max_speed.append(np.amax(speed_l[i]))
        min_speed.append(np.amin(speed_l[i])) # skipping possibly problematic first points, check if due to too small Kp
        max_power_out.append(np.amax(power_l[i]))
        total_distance_travelled.append(np.amax(position_l[i]))
        total_energy_output.append(np.amax(nrgy_l[i]))
        battery_req_charge.append(np.amax(np.array(nrgy_l[i])) / (motor_tension * 3600.0))
        max_out_force.append(np.amax(frc_out_l[i]))

    trip_min_avg_speed = np.amin(a_speed)
    trip_max_avg_speed = np.amax(a_speed)
    trip_max_speed = np.amax(max_speed)
    trip_min_speed = np.amin(min_speed)
    trip_max_power = np.amax(max_power_out)
    trip_max_section_distance = np.amax(total_distance_travelled)
    trip_max_energy_output = np.amax(total_energy_output)
    trip_max_battery_req_charge = np.amax(battery_req_charge)
    trip_max_out_force = np.amax(max_out_force)

    print '\n trip_min_avg_speed %f : ' % trip_min_avg_speed
    print '\n trip_max_avg_speed %f : ' % trip_max_avg_speed
    print '\n trip_max_speed %f : ' % trip_max_speed
    print '\n trip_min_speed %f : ' % trip_min_speed
    print '\n trip_max_power %f : ' % trip_max_power
    print '\n trip_max_section_distance %f : ' % trip_max_section_distance
    print '\n trip_max_energy_output %f : ' % trip_max_energy_output
    print '\n trip_max_battery_req_charge %f : ' % trip_max_battery_req_charge
    print '\n trip_max_out_force %f : ' % trip_max_out_force


    print 'writing data to excel file'

    xls_output('sim_out.xls', nrgy_l, power_l, speed_l, position_l, frc_out_l, trip_time_list)


def xls_output(filename, nrgy_l, power_l, speed_l, position_l, frc_out_l, trip_time_list):
    book = xlwt.Workbook()

    sh_l = []
    for i in range(0, len(nrgy_l)):
        sh_l.append(book.add_sheet(str(i+1)))

    i = 0
    for sh in sh_l:
        variables = [nrgy_l[i], power_l[i], speed_l[i], position_l[i], frc_out_l[i], trip_time_list[i]]
        e_desc = 'energy'
        p_desc = 'power'
        s_desc = 'speed'
        x_desc = 'x'
        f_desc = 'force out'
        t_desc = 'time sec'

        desc = [e_desc, p_desc, s_desc, x_desc, f_desc, t_desc]
        n = 0
        for col in variables:

            sh.write(1, n+1, desc[n])
            j = 1
            for item in col[20:]: #skipping first items
                sh.write(j+1, n+1, item)
                j+=1
            n += 1
        i+=1

    book.save(filename)


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

# summary of prelim analysis
[max_d, max_grad, max_p] = get_trip_stats(path_sections_stats)

print '\n\n'
print 'max distance : %.3f' % max_d
print 'max gradient : %.3f' % max_grad
print 'max power : %.3f' % max_p
print 'running Matlab sim \n'


manual = 1
test = input('do you want to do automatic testing ? 1 for yes, 0 for no ')

# FOR TESTING!!!! normal val is 23
test_i = 23



if test == 1:

    for i in range(0, test_i):

        section_cl = tripSectionClass()
        section_cl = call_section_sim(eng, i, path_sections_data, section_cl)

        energy.append(section_cl.inst_energy)
        max_output_power.append(section_cl.p_out_pos)
        speed_out.append(section_cl.speed_out_km_h)
        x_out.append(section_cl.x_out)
        force_out.append(section_cl.force_out)
        s_time.append(section_cl.sim_time)

    plot_data = input('do you want to plot data from one specific index ?, enter 1 for yes')
    while plot_data == 1:

        index = input('which index?')

        plot_section_output(energy[index], max_output_power[index], speed_out[index], x_out[index], force_out[index],
                            s_time[index])

        print_section_output_stats(energy[index], max_output_power[index], speed_out[index], x_out[index],
                                   force_out[index], s_time[index], motor_input_Voltage)

        plot_data = input('do you want to plot data from one specific index ?, enter 1 for yes')

    complete_data_summary(energy, max_output_power, speed_out, x_out, force_out, s_time, motor_input_Voltage)

else:

    while manual ==1:
        print '\nmanual testing'
        index = input('index of section you want to test')

        section_cl = tripSectionClass()
        section_cl = call_section_sim(eng, index, path_sections_data, section_cl)

        plot_section_output(section_cl.inst_energy, section_cl.p_out_pos, section_cl.speed_out_km_h, section_cl.x_out,
                            section_cl.force_out, section_cl.sim_time)

        print_section_output_stats(section_cl.inst_energy, section_cl.p_out_pos, section_cl.speed_out_km_h,
                                   section_cl.x_out, section_cl.force_out, section_cl.sim_time, motor_input_Voltage)

        manual = input('do you want to continue : 1 for yes, 0 for no')


script_end()
