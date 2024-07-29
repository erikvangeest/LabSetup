import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy
from scipy import interpolate
from scipy import optimize
from scipy.optimize import minimize
from scipy.misc import derivative
from scipy.optimize import fmin
from scipy.optimize import curve_fit
from scipy.optimize import fsolve
from smartsense2.cloud.clients import get_data
import re
import datetime
import matplotlib.dates as mdates
from matplotlib.dates import DayLocator, HourLocator, DateFormatter, drange
import os
import calendar
from datetime import datetime
from scipy.optimize import minimize_scalar
from scipy.fft import fft, ifft
from scipy.signal import butter, filtfilt
from scipy.signal import find_peaks
from scipy.signal import peak_widths, freqz
import scipy.signal
import time
from scipy.interpolate import interp1d

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, PageBreak  # Import PageBreak for adding a new page
from PIL import Image as PILImage
from io import BytesIO

import warnings

# To suppress all warnings
warnings.filterwarnings("ignore")

# constants
e = 1.602176634e-19 # elementary charge in coulombs
hbar = 1.054571817e-34 # reduced planck constant in joule seconds
nu_F = 1e6 # fermi velocity electrons in graphene in m/s
C_ox = 0.26e-5 # geometric capacitance F/cm^2 (F/m^2?)
mu = 8600
N_sq = 1 # no clue what this is
n_0 = 1e15
R_contact = 0

a = e/C_ox
b = (hbar*nu_F*np.sqrt(np.pi))/e

def n(V):
    return (b**2 + 2*a*V + np.sqrt(b**4 + 4*a*(b**2)*np.abs(V)))/(2*a**2)

def R_total(V,R_c,n_0_,mu_,V_0):
    return R_c + N_sq/(np.sqrt(n_0_**2 + n(V-V_0)**2)*e*mu_)

def fit(V_data, R_data):
    opt, cov = curve_fit(R_total, V_data, R_data, p0=[1050,0.42e14,2.35e1,16.7])
    return opt

def derivative_R_total(V, R_c,n_0_,mu_,V_0):
    return derivative(R_total, V, args=([R_c,n_0_,mu_,V_0]), dx=1e-6)

def max_slope(f, fit_param, V):
    V_minimum = optimize.fminbound(f, V[0], V[-1], args=(fit_param))
    return f(V_minimum, *fit_param)

def FWHM(V_data, R_data):

    fit_param = fit(V_data, R_data)
    maximum = minimize_scalar(lambda x: -R_total(x,0,fit_param[1], fit_param[2], fit_param[3]))

    # Maximum value and corresponding x-value
    max_y = -maximum.fun  # Since we took negative of the function
    max_x = maximum.x

    # Find half of the maximum value
    half_max_y = max_y * 0.5
    
    # specify locations on the x axis from where roots are gonna be found, this is kinda ugly
    voltage_intervals = np.linspace(0, 100,5)

    roots=np.array([])

    f = lambda x : R_total(x,0,fit_param[1],fit_param[2],fit_param[3]) - half_max_y

    for i in voltage_intervals:
        #root = root(f, x0=i)['x'][0]
        root_i = fsolve(f,i)[0]
        roots = np.append(roots, round(root_i, 2))
    half_max_x = np.unique(np.sort(roots))
    
    if len(half_max_x) == 1:
        fwhm = 0
    else:
        # Calculate the FWHM
        fwhm = half_max_x[1] - half_max_x[0]
    
    return fwhm, max_y

def analisys1(V, R_up, R_down):
    
    fitting_parameters_up = fit(V, R_up)
    fitting_parameters_down = fit(V, R_down)
    
    maximal_slope_up = max_slope(derivative_R_total, fitting_parameters_up, V)
    V_peak_up = fitting_parameters_up[3]
    
    maximal_slope_down = max_slope(derivative_R_total, fitting_parameters_down, V)
    V_peak_down = fitting_parameters_down[3]
    
    delta_peak = V_peak_down - V_peak_up
    
    return np.array([maximal_slope_up, V_peak_up, maximal_slope_down, V_peak_down, delta_peak]) 

def extract_datetime(string):
    # Define the pattern to match the date and time format 'YYYY-MM-DD-HH-MM-SS'
    datetime_pattern = r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}'

    # Extract datetime using regular expression
    match = re.search(datetime_pattern, string)

    if match:
        datetime_str = match.group()
        # Parse the datetime string into a datetime object
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d-%H-%M-%S')
        return datetime_obj
    else:
        return 'None'
    
def extract_datetime_env(string):
    # Define the pattern to match the date and time format 'YYYY-MM-DD-HH-MM-SS'
    datetime_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'

    # Extract datetime using regular expression
    match = re.search(datetime_pattern, string)

    if match:
        datetime_str = match.group()
        # Parse the datetime string into a datetime object
        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        return datetime_obj
    else:
        return 'None'

def get_humidity(time, environmental_data):
    date_strings = environmental_data['Timestamp2'].to_numpy()
    RH_data = environmental_data['SHT20 Humidity'].to_numpy()
    
    convert_to_datetime = np.vectorize(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    
    datetime_array = convert_to_datetime(date_strings)
    
    # Calculate differences between test date and each date in the array
    differences = np.abs(datetime_array - time)

    # Find the index of the minimum difference
    closest_indices = np.where(differences == np.min(differences))[0]
    closest_index = closest_indices[0]
    
    RH = RH_data[closest_index]
    
    return RH

def get_mfc(time, mfc_value):
    
    date_strings_MFC = MFC1['Timestamp'].to_numpy()
    MFC_value = MFC1['MFC1 Value'].to_numpy()

    convert_to_datetime = np.vectorize(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    datetime_array = convert_to_datetime_mfc(date_strings_MFC)

    
    # Calculate differences between test date and each date in the array
    differences = np.abs(datetime_array - time)

    # Find the index of the minimum difference
    closest_indices = np.where(differences == np.min(differences))[0]
    closest_index = closest_indices[0]
    
    mfc = MFC_value[closest_index]
    
    return mfc

def get_klep(time, environmental_data):
    date_strings = environmental_data['Timestamp2'].to_numpy()
    klep_data = environmental_data['Klep status'].to_numpy()
    
    convert_to_datetime = np.vectorize(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    
    datetime_array = convert_to_datetime(date_strings)
    
    # Calculate differences between test date and each date in the array
    differences = np.abs(datetime_array - time)

    # Find the index of the minimum difference
    closest_indices = np.where(differences == np.min(differences))[0]
    closest_index = closest_indices[0]
    
    Klep = klep_data[closest_index]
    
    return Klep

def R_at_XV_fit(list_of_arrays, Volts):

    resistance_at_XV_fit_poly = []
    
    for data in list_of_arrays:  
        V = data[:,0]
        R_up = data[:,1]
        R_down = data[:,2]
        
        z = np.polyfit(V, R_up, 6)
        p = np.poly1d(z)
        
        resistance_at_XV_fit_poly.append(p(Volts))
        
        
    return resistance_at_XV_fit_poly

def up_min_down_at_XV_fit(list_of_arrays, Volts):

    up_min_down = []
    
    for data in list_of_arrays:  
        V = data[:,0]
        R_up = data[:,1]
        R_down = data[:,2]
        
        zu = np.polyfit(V, R_up, 6)
        pu = np.poly1d(zu)
        
        zd = np.polyfit(V, R_down, 6)
        pd = np.poly1d(zd)
        
        up_min_down.append(pu(Volts)-pd(Volts))
        
        
    return up_min_down

def delta_v(list_of_arrays):
    
    dv_list = []
    
    for data in list_of_arrays:
        V = data[:,0]
        R_up = data[:,1]
        R_down = data[:,2]
        
        dv = analisys1(V, R_up, R_down)[4]
        
        dv_list.append(dv)
    
    return dv_list

def fwhm_(list_of_arrays):
    
    fwhm_u_list = []
    fwhm_d_list = []
    
    for data in list_of_arrays:
        V = data[:,0]
        R_up = data[:,1]
        R_down = data[:,2]
        
        fwhm_u = FWHM(V, R_up)[0]
        fwhm_d = FWHM(V, R_down)[0]
        
        fwhm_u_list.append(fwhm_u)
        fwhm_d_list.append(fwhm_d)
        
    return fwhm_u_list, fwhm_d_list

def max_R(list_of_arrays):
    
    max_R_u_list = []
    max_R_d_list = []
    
    for data in list_of_arrays:
        V = data[:,0]
        R_up = data[:,1]
        R_down = data[:,2]
        
        maxr_u = FWHM(V, R_up)[1]
        maxr_d = FWHM(V, R_down)[1]
        
        max_R_u_list.append(maxr_u)
        max_R_d_list.append(maxr_d)
        
    return max_R_u_list, max_R_d_list

def max_slope_(list_of_arrays):
    
    ms_list_u = []
    ms_list_d = []
    
    for data in list_of_arrays:
        V = data[:,0]
        R_up = data[:,1]
        R_down = data[:,2]
        
        an = analisys1(V, R_up, R_down)
        ms_u = an[0]
        ms_d = an[2]
        
        ms_list_u.append(ms_u)
        ms_list_d.append(ms_d)
    
    return  ms_list_u, ms_list_d

def R0(list_of_arrays):
    
    ro_list_u = []
    ro_list_d = []
    
    for data in list_of_arrays:
        V = data[:,0]
        R_up = data[:,1]
        R_down = data[:,2]
        
        fitje_u = fit(V, R_up)
        fitje_d = fit(V, R_down)
        #print(fitje_u[0])
        
        ro_list_u.append(fitje_u[0])
        ro_list_d.append(fitje_d[0])
    
    return  ro_list_u, ro_list_d

def V0(list_of_arrays):
    
    V0_list_u = []
    V0_list_d = []
    
    for data in list_of_arrays:
        V = data[:,0]
        R_up = data[:,1]
        R_down = data[:,2]
        
        V0_u = analisys1(V, R_up, R_down)[1]
        V0_d = fit(V, R_down)[3]
        
        V0_list_u.append(V0_u)
        V0_list_d.append(V0_d)
    
    return  V0_list_u, V0_list_d

def length(list_of_arrays):
    
    length_list_u = []
    length_list_d = []
    
    for data in list_of_arrays:
        V = data[:,0]
        R_up = data[:,1]
        R_down = data[:,2]
        
        R0_u = fit(V, R_up)[0]
        R0_d = fit(V, R_down)[0]
        
        maxr_u = FWHM(V, R_up)[1]
        maxr_d = FWHM(V, R_down)[1]
        
        
        length_list_u.append(maxr_u-R0_u)
        length_list_d.append(maxr_d-R0_d)
    
    return  length_list_u, length_list_d

def get_data2(year, month, day, start_hour, end_hour, receptor):
    
    
    start_minute = int((start_hour - int(start_hour))*60)
    end_minute = int((end_hour - int(end_hour))*60)
    start_h = int(start_hour)
    end_h = int(end_hour)
    second = 0
    
    start_date_string = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, day, start_h, start_minute, second)
    end_date_string = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, day, end_h, end_minute, second)
    
    data = get_data(start_date_string, end_date_string,10000)
    
    filtered_data = filter_data(data, receptor)
    
    return filtered_data

def get_data3(year, month, start_day, end_day, start_hour, end_hour, receptor):
    
    
    start_minute = int((start_hour - int(start_hour))*60)
    end_minute = int((end_hour - int(end_hour))*60)
    start_h = int(start_hour)
    end_h = int(end_hour)
    second = 0
    
    start_date_string = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, start_day, start_h, start_minute, second)
    end_date_string = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, end_day, end_h, end_minute, second)
    
    data = get_data(start_date_string, end_date_string,10000)
    
    filtered_data = filter_data(data, receptor)
    
    return filtered_data

def filter_data(data, receptor):
    
    receptor_key = 'receptor_uid'
    receptor_value = receptor
    
    
    filtered_data = [d for d in data if d.get(receptor_key) == receptor_value]
    
    return filtered_data

def import_and_match_data_klep(directory, environmental_data):
    # Get a list of all files in the directory
    all_files = os.listdir(directory)

    # Filter out only the CSV files
    csv_files = [file for file in all_files if file.endswith('.csv')]

    # Create an empty list to store NumPy arrays
    numpy_arrays = []
    date_times = []
    klep_data = []

    # Iterate over each CSV file
    for csv_file in csv_files:
        # Read the CSV file into a NumPy array
        file_path = os.path.join(directory, csv_file)
        #print(extract_datetime(csv_file))
        time = extract_datetime(csv_file)
        date_times.append(time)
        data = np.genfromtxt(file_path, delimiter=',')  # Assuming CSV files are comma-separated
        
        # Remove the first row and the last column
        data = data[1:, :-1]
        numpy_arrays.append(data)
        
        # get relative humidity from the environmental data
        klep = get_klep(time, environmental_data)
        klep_data.append(klep)
    
    numpy_arrays = np.array(numpy_arrays)
    date_times = np.array(date_times)
    klep_data = np.array(klep_data)
    
    # Get the indices that would sort the datetime array
    sorted_indices = np.argsort(date_times)
    # Use the sorted indices to reorder all arrays
    sorted_datetimes = date_times[sorted_indices]
    sorted_data_array = numpy_arrays[sorted_indices]
    sorted_klep_data = klep_data[sorted_indices]
        
    return sorted_data_array, sorted_datetimes, sorted_klep_data

def import_sweeps_from_csv(directory):
    
    # Get a list of all files in the directory
    all_files = os.listdir(directory)

    # Filter out only the CSV files
    csv_files = [file for file in all_files if file.endswith('.csv')]

    # Create an empty list to store NumPy arrays
    sweeps_data = []
    date_times = []
    
     # Iterate over each CSV file
    for csv_file in csv_files:
        # Read the CSV file into a NumPy array
        file_path = os.path.join(directory, csv_file)
        #extract time
        time = extract_datetime(csv_file)
        date_times.append(time)
        
        # get sweeps
        data = np.genfromtxt(file_path, delimiter=',')  # Assuming CSV files are comma-separated
        
        # Remove the first row and the last column
        data = data[1:, :-1]
        sweeps_data.append(data)
        
    
    
    sweeps_data_ = np.array(sweeps_data)
    date_times_ = np.array(date_times)
    
    # Get the indices that would sort the datetime array
    sorted_indices = np.argsort(date_times_)
    # Use the sorted indices to reorder all arrays
    sorted_datetimes = date_times_[sorted_indices]
    sorted_data_array = sweeps_data_[sorted_indices]
    
    return sorted_datetimes, sorted_data_array
    
    

def extract_klep(env_data):

    
    date_times = []
    klep_data = []
    
    for timestamp in env_data['Timestamp2']:
        date_times.append(extract_datetime_env(timestamp))
    for klep in env_data['Klep status']:
        klep_data.append(klep)
        
    return date_times, klep_data


def extract_heater(env_data):

    
    date_times = []
    heater_data = []
    
    for timestamp in env_data['Timestamp1']:
        date_times.append(extract_datetime_env(timestamp))
    for klep in env_data['Heater4']:
        heater_data.append(klep)
        
    return date_times, heater_data

def extract_temp(env_data):

    
    date_times = []
    temp_data = []
    
    for timestamp in env_data['Timestamp2']:
        date_times.append(extract_datetime_env(timestamp))
    for klep in env_data['SHT20 Temperature']:
        temp_data.append(klep)
        
    return date_times, temp_data

def R_at_XV(list_of_sweeps, V):
    
    R_up_values = []
    R_down_values = []
    R_up_min_down_values = []
    
    for sweep in list_of_sweeps:
        absolute_diff = np.abs(sweep[:,0] - V)
        closest_index = np.argmin(absolute_diff)
        
        R_up = sweep[closest_index,1]
        R_down = sweep[closest_index,2]
        R_up_min_down =  R_up - R_down
        
        R_up_values.append(R_up)
        R_down_values.append(R_down)
        R_up_min_down_values.append(R_up_min_down)
        
    return np.array(R_up_values), np.array(R_down_values), np.array(R_up_min_down_values)

def R_at_XV_fit_poly(list_of_sweeps, Volt, order):
    
    fit_order = order
    
    R_up_values = []
    R_down_values = []
    R_up_min_down_values = []
    
    for sweep in list_of_sweeps:
        V = sweep[:,0]
        R_up = sweep[:,1]
        R_down = sweep[:,2]
        
        zu = np.polyfit(V, R_up, fit_order)
        pu = np.poly1d(zu)
        
        zdd = np.polyfit(V, R_down, fit_order)
        pdd = np.poly1d(zd)
        
        R_up_values.append(pu(Volt))
        R_down_values.append(pdd(Volt))
        R_up_min_down_values.append(pu(Volt)-pdd(Volt))
        
    return R_up_values, R_down_values, R_up_min_down_values

def R_at_XV_fit_dirac(list_of_sweeps, Volt):
    
    
    R_up_values = []
    R_down_values = []
    R_up_min_down_values = []
    
    for sweep in list_of_sweeps:
        V = sweep[:,0]
        R_up = sweep[:,1]
        R_down = sweep[:,2]
        
        fit_param_up = fit(V, R_up)
        fit_param_down = fit(V, R_down)
        R_up = R_total(Volt, fit_param_up[0], fit_param_up[1], fit_param_up[2], fit_param_up[3])
        R_down = R_total(Volt, fit_param_up[0], fit_param_down[1], fit_param_down[2], fit_param_down[3])

        
        R_up_values.append(R_up)
        R_down_values.append(R_down)
        R_up_min_down_values.append(R_up-R_down)
        
    return R_up_values, R_down_values, R_up_min_down_values

def R_at_XV_fit_dirac_R0(list_of_sweeps, Volt):
    
    
    R_up_values = []
    R_down_values = []
    R_up_min_down_values = []
    
    for sweep in list_of_sweeps:
        V = sweep[:,0]
        R_up = sweep[:,1]
        R_down = sweep[:,2]
        
        fit_param_up = fit(V, R_up)
        fit_param_down = fit(V, R_down)
        R_up = R_total(Volt, 0, fit_param_up[1], fit_param_up[2], fit_param_up[3])
        R_down = R_total(Volt, 0, fit_param_down[1], fit_param_down[2], fit_param_down[3])

        
        R_up_values.append(R_up)
        R_down_values.append(R_down)
        R_up_min_down_values.append(R_up-R_down)
        
    return R_up_values, R_down_values, R_up_min_down_values

def datetime_array_to_epoch(dt_array):
    epoch = datetime.utcfromtimestamp(0)
    delta_array = dt_array - epoch
    return delta_array.astype('timedelta64[s]').astype(int)

def plot_slope_DV(sweep_directory, env_data_directory):
    
    # Import data
    date_times, sweeps = import_sweeps_from_csv(sweep_directory)
    environmental_data = pd.read_csv(env_data_directory)
    
    # Analise data
    DV = delta_v(sweeps)
    
    epoch_times = datetime_array_to_epoch(date_times)
    
    epoch_times = epoch_times - epoch_times[0]
    
    DV_fit_param = np.polyfit(epoch_times, DV, 1)
    DV_fit = np.poly1d(DV_fit_param)
    
    
    return DV_fit_param

def plak(dir_list, env_list):
    
    datetimes_total, sweeps_total = import_sweeps_from_csv(dir_list[0])
    env_total = pd.read_csv(env_list[0])
    
    for i in range(len(env_list)-1):
        datetimes, sweeps = import_sweeps_from_csv(dir_list[i+1])
        sweeps_total = np.concatenate((sweeps_total, sweeps),axis=0)
        datetimes_total = np.concatenate((datetimes_total, datetimes))
        
    for i in range(len(env_list)-1):
        env_data = pd.read_csv(env_list[i+1])
        env_total = pd.concat([env_total, env_data])
        
        
    return datetimes_total, sweeps_total, env_total

def inv(x, A, B, X0):
    return A/(x-X0) + B

def get_humidity(dir_list, env_list):
    
    t, sw, env = plak(dir_list, env_list)
    
    date_times = []
    hum_data_SHT20 = []
    
    for timestamp in env['Timestamp2']:
        date_times.append(extract_datetime_env(timestamp))
    for hum in env['SHT20 Humidity']:
        hum_data_SHT20.append(hum)
        
    epoch_times = datetime_array_to_epoch(np.array(date_times))
    epoch_times = epoch_times - epoch_times[0]
    
    plt.plot(epoch_times, hum_data_SHT20)
    
    return

def baseline_fit_filter_2(times, sweeps):
    
    # convert datetimes to epoch times
    epoch_times = datetime_array_to_epoch(times)
    epoch_times = epoch_times - epoch_times[0]
    
    # Analise data
    R_at_0V_u, R_at_0V_d, Delta0  = R_at_XV(sweeps, 0)
    #plt.plot(epoch_times, R_at_0V_u)
    #print('minup= ', min(R_at_0V_u))
    # copy data
    data_baseline = R_at_0V_u.copy()
    t_baseline = epoch_times.copy()
    
    # make initial fit
    try:
        opt_inv, cov_inv = curve_fit(inv, epoch_times, R_at_0V_u, p0=[517202., min(R_at_0V_u),  -1542.])#, maxfev=10000)
        #print("Optimal parameters:", opt_inv)
    except RuntimeError as e:
        print("Error:", e)
        print("Error: could not find optimal parameters")
        opt_inv = [517202., min(R_at_0V_u),  -1542.]
    
    opt_inv, cov_inv = curve_fit(inv, epoch_times, R_at_0V_u, p0=[517202., min(R_at_0V_u),  -1542.], maxfev=10000)
    #print('parameters:', opt_inv)
    baseline_1 = inv(epoch_times, *opt_inv)

    #filter out all values greater than initial fit
    for i in range(len(epoch_times)):
        if R_at_0V_u[i] > baseline_1[i]:
            data_baseline[i] = np.nan
    
    # Create a mask to identify NaN values
    mask = np.isnan(data_baseline)
    
    # Filter the array to remove entries with NaN values
    t_baseline = t_baseline[~mask]
    data_baseline = data_baseline[~mask]
    
    # Fit a second time
    try:
        opt, cov = curve_fit(inv, t_baseline, data_baseline, p0=opt_inv)#, maxfev=10000)
        #print("Optimal parameters:", opt)
    except RuntimeError as e:
        print("Error:", e)
        print("Error: could not find optimal parameters")
        opt = opt_inv

    baseline_2 = inv(epoch_times, *opt)
    bl_correction = R_at_0V_u - baseline_2

    # Make plot
    fig = plt.figure(figsize=(16, 12))
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)
 
    ax1.plot(epoch_times, bl_correction, linestyle='-', marker=None, label='baseline correction')
    ax2.plot(epoch_times, R_at_0V_u, linestyle='-', marker=None, label='R up')
    ax2.plot(epoch_times, inv(epoch_times, *opt), linestyle='-', marker=None, label='baseline fit')
    #ax2.plot(epoch_times, inv(epoch_times, *opt_inv), linestyle='-', marker=None, label='R up')
    
    #ax1.plot(epoch_times, R_at_0V_d, linestyle='-', marker=None, label='R down')
    
    ax1.set_ylabel(r'R ($\Omega$)')
    ax2.set_ylabel(r'R ($\Omega$)')
    ax2.set_ylabel(r'time (s)')
    ax1.set_xlabel('time (s)')
    ax1.set_title('Baseline fit and correction for R at 0V element 1')
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer


def get_all(year, month, start_day, end_day, start_hour, end_hour, receptor):
    #start_date_string = "{:04d}-{:02d}-{:02d}T00:00:00Z".format(year, month, day)
    #end_date_string = "{:04d}-{:02d}-{:02d}T23:59:59Z".format(year, month, day)
    
    start_min = int((start_hour - int(start_hour))*60)
    end_min = int((end_hour - int(end_hour))*60)
    start_h = int(start_hour)
    end_h = int(end_hour)
    second = 0
    
    start_date_string = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, start_day, start_h, start_min, second)
    end_date_string = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, end_day, end_h, end_min, second)
    
    data = get_data(start_date_string, end_date_string, receptor, 10000)
    sorted_data = sorted(data, key=lambda x: x['timestamp'])
    print('data=',data)
    
    datetimes, hum, temp = get_env_data(sorted_data)
    
    data_element_1 = get_element(data, element=1)
    data_element_2 = get_element(data, element=2)
    data_element_3 = get_element(data, element=3)
    data_element_4 = get_element(data, element=4)
    
    # sort library
    sorted_data_el_1 = sorted(data_element_1, key=lambda x: x['timestamp'])
    sorted_data_el_2 = sorted(data_element_2, key=lambda x: x['timestamp'])
    sorted_data_el_3 = sorted(data_element_3, key=lambda x: x['timestamp'])
    sorted_data_el_4 = sorted(data_element_4, key=lambda x: x['timestamp'])

    
    return sorted_data_el_1, sorted_data_el_2, sorted_data_el_3, sorted_data_el_4, datetimes, hum, temp

def check_dead_elements(data):
    
    test_data = data['measurement']['resistance']
        
    if test_data[0] > 1e5:
        print('element ' + filtered_data['receptor_element_index'] + ' is dead')  

def plot_all(year, month, day, start_hour, end_hour, receptor, element):
    
    data = get_all(year, month, day, start_hour, end_hour, receptor, element)
    
    for d in data:
        #plt.plot(V_sweep, d['measurement']['resistance'])
        plt.plot(d['measurement']['resistance'])

        
    
def get_sweeps(data):
    
    datetimes = []
    sweeps = []
    
    
    for d in data:
        # Get voltage of up and down sweep
        voltage = d['measurement']['voltage']
        v = voltage[:91]
        #v_down = np.flip(voltage[90:])
        
        # get resisitance of up and down sweep
        resistance = d['measurement']['resistance']
        r_up = resistance[:91]
        r_down = np.flip(resistance[90:])
        
        # Stack them together
        sweep = np.column_stack((v, r_up, r_down))
        
        sweeps.append(sweep)
        
        # Get time 
        timestamp = d['timestamp'] / 1000
        
        # Convert timestamp string to datetime object
        datetime_obj = datetime.fromtimestamp(timestamp)
        
        datetimes.append(datetime_obj)
    
    return np.array(datetimes), sweeps

def plot_R_at_0V_cloud(times, sweeps):
    
    # Calculate resistance at 0V
    R_at_0V_u, R_at_0V_d, Delta0  = R_at_XV(sweeps, 0)
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(16, 6))
    ax1.plot_date(times, R_at_0V_u, linestyle='-', marker=None, label='R up')
    ax1.plot_date(times, R_at_0V_d, linestyle='-', marker=None, label='R down')
    
    ax1.set_ylabel(r'R ($\Omega$)')
    ax1.set_xlabel('time (H:M)')
    ax1.set_title('R at 0V')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer

def plot_first_sweep_cloud(element):

    # get element
    element_nr = element[0]['receptor_element_index']
    
    t, sw = get_sweeps(element)
    voltage = sw[0][:,0]
    R_up = sw[0][:,1]
    R_down = sw[0][:,2]
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot(voltage, R_up, linestyle='-', marker=None, label='R up')
    ax1.plot(voltage, R_down, linestyle='-', marker=None, label='R down')
    
    ax1.set_ylabel(r'R ($\Omega$)')
    ax1.set_xlabel('Voltage (V)')
    ax1.set_title('First sweep element '+ str(element_nr))
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper left')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer

def plot_R_at_0V_all_elements_cloud(el_1, el_2, el_3, el_4):
    
    datetimes1, sweeps1 = get_sweeps(el_1)
    datetimes2, sweeps2 = get_sweeps(el_2)
    datetimes3, sweeps3 = get_sweeps(el_3)
    datetimes4, sweeps4 = get_sweeps(el_4)
    
    # Calculate resistance at 0V
    R_at_0V_u1, R_at_0V_d1, Delta01  = R_at_XV(sweeps1, 0)
    R_at_0V_u2, R_at_0V_d2, Delta02  = R_at_XV(sweeps2, 0)
    R_at_0V_u3, R_at_0V_d3, Delta03  = R_at_XV(sweeps3, 0)
    R_at_0V_u4, R_at_0V_d4, Delta04  = R_at_XV(sweeps4, 0)
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(16, 6))
    ax2 = ax1.twinx()
    ax1.plot_date(times, temps, linestyle='-', marker=None, label='temperature')
    #ax1.plot_date(datetimes1, R_at_0V_u1, linestyle='-', marker=None, label='R element 1')
    ax1.plot_date(datetimes2, R_at_0V_u2, linestyle='-', marker=None, label='R element 2')
    #ax1.plot_date(datetimes3, R_at_0V_u3, linestyle='-', marker=None, label='R element 3')
    #ax1.plot_date(datetimes4, R_at_0V_u4, linestyle='-', marker=None, label='R element 4')
    
    ax1.set_ylabel(r'R ($\Omega$)')
    ax1.set_xlabel('time (H:M)')
    ax1.set_title('R at 0V for all four elements')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    #plt.close()
    
    return buffer

def plot_R_at_0V_all_elements_temp_cloud(el_1, el_2, el_3, el_4, times, temps):
    
    datetimes1, sweeps1 = get_sweeps(el_1)
    datetimes2, sweeps2 = get_sweeps(el_2)
    datetimes3, sweeps3 = get_sweeps(el_3)
    datetimes4, sweeps4 = get_sweeps(el_4)
    
    # Calculate resistance at 0V
    R_at_0V_u1, R_at_0V_d1, Delta01  = R_at_XV(sweeps1, 0)
    R_at_0V_u2, R_at_0V_d2, Delta02  = R_at_XV(sweeps2, 0)
    R_at_0V_u3, R_at_0V_d3, Delta03  = R_at_XV(sweeps3, 0)
    R_at_0V_u4, R_at_0V_d4, Delta04  = R_at_XV(sweeps4, 0)
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(16, 6))
    #ax2 = ax1.twinx()
    #ax2.plot_date(times, temps, linestyle='dashed', marker=None, label='temperature', color='red', linewidth=0.5)
    ax1.plot_date(datetimes1, R_at_0V_u1, linestyle='-', marker=None, label='R element 1')
    ax1.plot_date(datetimes2, R_at_0V_u2, linestyle='-', marker=None, label='R element 2')
    ax1.plot_date(datetimes3, R_at_0V_u3, linestyle='-', marker=None, label='R element 3')
    ax1.plot_date(datetimes4, R_at_0V_u4, linestyle='-', marker=None, label='R element 4')
    
    ax1.set_ylabel(r'R ($\Omega$)')
    #ax2.set_ylabel(r'temperature')
    ax1.set_xlabel('time (H:M)')
    ax1.set_title('R at 0V for all four elements')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    #lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer

def plot_R_at_0V_all_elements_temp_cloud2(el_1, el_2, el_3, el_4, times, temps):
    
    datetimes1, sweeps1 = get_sweeps(el_1)
    datetimes2, sweeps2 = get_sweeps(el_2)
    datetimes3, sweeps3 = get_sweeps(el_3)
    datetimes4, sweeps4 = get_sweeps(el_4)
    
    # Calculate resistance at 0V
    R_at_0V_u1, R_at_0V_d1, Delta01  = R_at_XV(sweeps1, 0)
    R_at_0V_u2, R_at_0V_d2, Delta02  = R_at_XV(sweeps2, 0)
    R_at_0V_u3, R_at_0V_d3, Delta03  = R_at_XV(sweeps3, 0)
    R_at_0V_u4, R_at_0V_d4, Delta04  = R_at_XV(sweeps4, 0)
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(16, 6))
    #ax2 = ax1.twinx()
    #ax2.plot_date(times, temps, linestyle='dashed', marker=None, label='temperature', color='red', linewidth=0.5)
    ax1.plot_date(datetimes1, R_at_0V_u1, linestyle='-', marker=None, label='R element 1')
    ax1.plot_date(datetimes2, R_at_0V_u2, linestyle='-', marker=None, label='R element 2')
    ax1.plot_date(datetimes3, R_at_0V_u3, linestyle='-', marker=None, label='R element 3')
    ax1.plot_date(datetimes4, R_at_0V_u4, linestyle='-', marker=None, label='R element 4')
    
    ax1.set_ylabel(r'R ($\Omega$)')
    #ax2.set_ylabel(r'temperature')
    ax1.set_xlabel('time (H:M)')
    ax1.set_title('R at 0V for all four elements')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    #lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    #plt.close()
    
    return buffer


def plot_R_at_20V_cloud(times, sweeps):
    
    # Calculate resistance at 0V
    R_at_0V_u, R_at_0V_d, Delta0  = R_at_XV(sweeps, 20)
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(16, 6))
    ax1.plot_date(times, R_at_0V_u, linestyle='-', marker=None, label='R up')
    ax1.plot_date(times, R_at_0V_d, linestyle='-', marker=None, label='R down')
    
    ax1.set_ylabel(r'R ($\Omega$)')
    ax1.set_xlabel('time (H:M)')
    ax1.set_title('R at 20V')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer

def plot_R_at_40V_cloud(times, sweeps):
    
    # Calculate resistance at 0V
    R_at_0V_u, R_at_0V_d, Delta0  = R_at_XV(sweeps, 40)
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(16, 6))
    ax1.plot_date(times, R_at_0V_u, linestyle='-', marker=None, label='R up')
    ax1.plot_date(times, R_at_0V_d, linestyle='-', marker=None, label='R down')
    
    ax1.set_ylabel(r'R ($\Omega$)')
    ax1.set_xlabel('time (H:M)')
    ax1.set_title('R at 40V')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer

def plot_temp_cloud(times, temps):
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot_date(times, temps, linestyle='-', marker=None, label='temperature')
    
    ax1.set_ylabel(r'Temperature ($C^{\circ}$)')
    ax1.set_xlabel('time (H:M)')
    ax1.set_title('Temperature')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer

def plot_hum_cloud(times, humidity):
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax1.plot_date(times, humidity, linestyle='-', marker=None, label='RH')
    
    ax1.set_ylabel(r'relative humidity (%)')
    ax1.set_xlabel('time (H:M)')
    ax1.set_title('Relative humidity')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer


def plot_BME_VOC(env_data_list):
    
    env_data = plak_env(env_data_list)
    
    tVOC_BME = env_data['BME tVOC'].values
    tVOC_BME_time = env_data['Timestamp3'].values
    
    convert_to_datetime = np.vectorize(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    datetime_array = convert_to_datetime(tVOC_BME_time)
    
    # Make plot
    plt.figure(figsize=(8, 6))
    plt.plot_date(datetime_array, tVOC_BME, fmt='-', label='BME tVOC', linewidth=0.5)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    #plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.tick_params(axis='x', rotation=45)
    plt.xlabel('time (H:M)')
    plt.ylabel('tVOC')
    plt.title('tVOC (BME)')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer

def plot_hysteresis_cloud(times, sweeps):
    

    
    # Analise data
    DV = delta_v(sweeps)
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(16, 6))
    ax1.plot_date(times, DV, linestyle='-', marker=None, label='Hysteresis')
    
    ax1.set_ylabel(r'Hysteresis (V)')
    ax1.set_xlabel('time (H:M)')
   
    ax1.set_title(r'Hysteresis ($CNP_{up}-CNP_{down}$)')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer

def plot_CNP_cloud(date_times, sweeps):
    
    # Analise data
    V0_up, V0_down = V0(sweeps)
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(16, 6))
    
    ax1.plot_date(date_times, V0_up, linestyle='-', marker=None, label='CNP up')
    ax1.plot_date(date_times, V0_down, linestyle='-', marker=None, label='CNP down')
    ax1.set_ylabel(r'CNP (V)')
    ax1.set_xlabel('time (H:M)')
    ax1.set_title(r'$CNP_{up}$ and $CNP_{down}$')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer

def plot_max_R_cloud(date_times, sweeps):
    
    # Analise data
    maxr_u, maxr_d = max_R(sweeps)
    
    # Make plot
    fig, ax1 = plt.subplots(figsize=(16, 6))
    
    ax1.plot_date(date_times, maxr_u, linestyle='-', marker=None, label='max R up')
    ax1.plot_date(date_times, maxr_d, linestyle='-', marker=None, label='max R down')
    ax1.set_ylabel(r'max R ($\Omega$)')
    ax1.set_xlabel('time (H:M)')
    ax1.set_title(r'Max R')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add legend
    lines, labels = ax1.get_legend_handles_labels()
    
    ax1.legend(lines, labels, loc='upper right')
    
    # Save the plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    buffer.seek(0)
    plt.close()
    
    return buffer


def get_receptor(data, receptor):
    
    receptor_key = 'receptor_uid'
    receptor_value = receptor
    
    filtered_data = [d for d in data if d.get(receptor_key) == receptor_value]
    
    return filtered_data

def get_element(data, element):
    
    element_key = 'receptor_element_index'
    element_value = element
    
    filtered_data = [d for d in data if d.get(element_key) == element_value]

    test_data = filtered_data[0]['measurement']['resistance']
        
    if test_data[0] is None or test_data[0] > 1e5:
        print('element ' + str(filtered_data[0]['receptor_element_index']) + ' is dead')
        # Iterate over each dictionary in the list
        for d in filtered_data:
            # Replace the 'resistance' value with an array of the same size with all elements as 2000
            d['measurement']['resistance'] = [2000] * len(d['measurement']['resistance'])
        
    return filtered_data

def filter_all(year, month, day, start_hour, end_hour, receptor):
    
    start_min = int((start_hour - int(start_hour))*60)
    end_min = int((end_hour - int(end_hour))*60)
    start_h = int(start_hour)
    end_h = int(end_hour)
    second = 0

    start_date_string = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, day, start_h, start_min, second)
    end_date_string = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, day, end_h, end_min, second)
    
    data = get_data(start_date_string, end_date_string, 10000)
    
    filtered_data = filter_data(data, receptor)
   
    return filtered_data
        
def get_env_data(data):
    
    datetimes = []
    humidities = []
    temperatures = []
    
    for d in data:
        # Get humidity
        humidity = d['environmental']['RH2']
        humidities.append(humidity)
        
        # Get temperature of up and down sweep
        temperature = d['environmental']['AT2']
        temperatures.append(temperature)
        
        # Get time 
        timestamp = d['timestamp'] / 1000
        
        # Convert timestamp string to datetime object
        datetime_obj = datetime.fromtimestamp(timestamp)
        datetimes.append(datetime_obj)
    
    return np.array(datetimes), np.array(humidities), np.array(temperatures)

def make_datestring_cloud(year, month, start_day, end_day):
    
    if start_day == end_day:
        return str(year)+'-'+str(month)+'-'+str(start_day)
    else:
        return str(year)+'-'+str(month)+'-'+str(start_day)+' / '+str(year)+'-'+str(month)+'-'+str(end_day)
    

def add_image_to_canvas(c, image_buffer, x_position, y_position, desired_width):
    # Convert BytesIO buffer to PIL Image
    image = PILImage.open(image_buffer)

    # Get the size of the image
    image_width, image_height = image.size

    # Calculate the aspect ratio of the image
    aspect_ratio = image_width / image_height

    # Calculate desired height for the image based on the aspect ratio and desired width
    desired_height = desired_width / aspect_ratio

    # Draw the image onto the canvas
    c.drawInlineImage(image, x_position, y_position, width=desired_width, height=desired_height)

def datetime_to_epoch(datetimes):
    epoch_times = []
    for dt in datetimes:
        epoch_times.append(int(dt.timestamp()))
    return epoch_times

    
def create_report_cloud(year, month, start_day, end_day, start_hour, end_hour, file_path, Chip_ID, receptor):   
    
    # Create PDF document
    #file_path = "/Users/timreisinger/Downloads/graph.pdf"
    
    # Import data
    el_1, el_2, el_3, el_4, datetimes, hum, temp = get_all(2024, month, start_day, end_day, start_hour, end_hour, receptor)
    
    # Create canvas
    c = canvas.Canvas(file_path, pagesize=letter)
    
    # Add title to the first page
    title_text = 'Chip ' + Chip_ID + ' report'
    c.setFont("Helvetica-Bold", 16)
    title_width = c.stringWidth(title_text)
    c.drawString((letter[0] - title_width) / 2, 750, title_text)

    # Add subtitle to the first page
    subtitle_text = "Date: " + make_datestring_cloud(year, month, start_day, end_day)
    c.setFont("Helvetica", 12)
    subtitle_width = c.stringWidth(subtitle_text)
    c.drawString((letter[0] - subtitle_width) / 2, 730, subtitle_text)

    # Add description environmental data
    description_text = "Environmental data"
    c.setFont("Helvetica-Bold", 12)
    description_width = c.stringWidth(description_text)
    c.drawString(60, 630, description_text)

    # Create graph buffer for temperature graph
    graph_buffer_temp = plot_temp_cloud(datetimes, temp)

    # Create graph buffer for humidity graph
    graph_buffer_hum = plot_hum_cloud(datetimes, hum)

    # Create graph buffer for first sweeps
    graph_buffer_first_sweep_el_1 = plot_first_sweep_cloud(el_1)
    graph_buffer_first_sweep_el_2 = plot_first_sweep_cloud(el_2)
    graph_buffer_first_sweep_el_3 = plot_first_sweep_cloud(el_3)
    graph_buffer_first_sweep_el_4 = plot_first_sweep_cloud(el_4)

    # define graph width
    width = 280

    # Define the position of the temperature graph on the first page
    x_position_temp = 40
    y_position_temp = 400

    # Define the position of the humidity graph on the first page
    x_position_hum = 300
    y_position_hum = 400

    # Define the position of the first sweep graph on the first page
    x_position_first_1 = 50
    y_position_first_1 = 220

    x_position_first_2 = 320
    y_position_first_2 = 220

    x_position_first_3 = 50
    y_position_first_3 = 70

    x_position_first_4 = 320
    y_position_first_4 = 70

    # Add temperature graph to the canvas
    add_image_to_canvas(c, graph_buffer_temp, x_position_temp, y_position_temp, width)

    # Add humidity graph to the canvas
    add_image_to_canvas(c, graph_buffer_hum, x_position_hum, y_position_hum, width)

    # Add first sweep graph to the canvas
    add_image_to_canvas(c, graph_buffer_first_sweep_el_1, x_position_first_1, y_position_first_1, 200)
    add_image_to_canvas(c, graph_buffer_first_sweep_el_2, x_position_first_2, y_position_first_2, 200)
    add_image_to_canvas(c, graph_buffer_first_sweep_el_3, x_position_first_3, y_position_first_3, 200)
    add_image_to_canvas(c, graph_buffer_first_sweep_el_4, x_position_first_4, y_position_first_4, 200)

    # Add table to the first page
    data = [['Name', 'Age'],
            ['John',  '30'],
            ['Alice', '25'],
            ['Bob',   '35']]

    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    #table.wrapOn(c, 400, 200)
    #table.drawOn(c, 400, 150)

    # Add a page break for the second page
    c.showPage()

    # Add title to the second page
    title_text_2 = "Resistances at various voltages"
    c.setFont("Helvetica-Bold", 16)
    title_width_2 = c.stringWidth(title_text_2)
    c.drawString((letter[0] - title_width_2) / 2, 750, title_text_2)
    
    datetimes1, sweeps1 = get_sweeps(el_1)

    # Create graph buffers
    graph_buffer_0V = plot_R_at_0V_cloud(datetimes1, sweeps1)
    graph_buffer_20V = plot_R_at_20V_cloud(datetimes1, sweeps1)
    graph_buffer_40V = plot_R_at_40V_cloud(datetimes1, sweeps1)

    # Define the position of the second graph on the second page
    x_position_0V = 5
    y_position_0V = 500

    x_position_20V = 5
    y_position_20V = 300

    x_position_40V = 5
    y_position_40V = 100

    width2 = 600

    # Add graphs to the canvas
    add_image_to_canvas(c, graph_buffer_0V, x_position_0V, y_position_0V, width2)
    add_image_to_canvas(c, graph_buffer_20V, x_position_20V, y_position_20V, width2)
    add_image_to_canvas(c, graph_buffer_40V, x_position_40V, y_position_40V, width2)

    # Add a page break for the third page
    c.showPage()

    # Add title to the third page
    title_text_3 = "Hysteresis, CNP and max R"
    c.setFont("Helvetica-Bold", 16)
    title_width_3 = c.stringWidth(title_text_3)
    c.drawString((letter[0] - title_width_3) / 2, 750, title_text_3)

    # Create graph buffers
    graph_buffer_hysteresis = plot_hysteresis_cloud(datetimes1, sweeps1)
    graph_buffer_CNP = plot_CNP_cloud(datetimes1, sweeps1)
    graph_buffer_max_R = plot_max_R_cloud(datetimes1, sweeps1)

    # Define the position of graphs on the page
    x_position_hys = 5
    y_position_hys = 500

    x_position_CNP = 5
    y_position_CNP = 275

    x_position_max_R = 5
    y_position_max_R = 50

    # Add graphs to the canvas
    add_image_to_canvas(c, graph_buffer_hysteresis, x_position_hys, y_position_hys, width2)
    add_image_to_canvas(c, graph_buffer_CNP, x_position_CNP, y_position_CNP, width2)
    add_image_to_canvas(c, graph_buffer_max_R, x_position_max_R, y_position_max_R , width2)

    # Add a page break for the fourth page
    c.showPage()

    # Add title to the third page
    title_text_3 = "Compare elements and make baseline fit"
    c.setFont("Helvetica-Bold", 16)
    title_width_3 = c.stringWidth(title_text_3)
    c.drawString((letter[0] - title_width_3) / 2, 750, title_text_3)

    buffer_all_el = plot_R_at_0V_all_elements_temp_cloud(el_1, el_2, el_3, el_4, datetimes, temp)
    buffer_baseline = baseline_fit_filter_2(datetimes1, sweeps1)
    
    # Define the position of graphs on the page
    x_position_comp = 5
    y_position_comp = 500

    x_position_baseline = 5
    y_position_baseline = 50

    add_image_to_canvas(c, buffer_all_el, x_position_comp, y_position_comp, width2)
    add_image_to_canvas(c, buffer_baseline, x_position_baseline, y_position_baseline, width2)

    # Save the PDF
    c.save()

    print("PDF saved at:", file_path)
    

# make sure data starts at one oclock otherwise baseline fitting will not work properly
start_hour = 0
end_hour = 9
start_day = 26
end_day = 26
month= 7

receptor = 'Receptor1'
chip_ID = '133'


file_path = rf'C:\Users\User\Documents\Git Repository\{chip_ID}_report.pdf'
create_report_cloud(2024, 7, 28, 0, 0, 0, file_path, chip_ID, receptor)
import inspect

#print(inspect.getsource(get_data))