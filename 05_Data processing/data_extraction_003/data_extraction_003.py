import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


x_values_of_interest = [0, 4, 8, 12, 16]  # Add more values as needed, not working yet!

def process_csv(file_path, y1_column, y2_column, x_column):
    # Parse the timestamp from the filename
    filename = os.path.basename(file_path)
    timestamp_str = filename.split('_')[3]  # Assuming timestamp is the third element
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d-%H-%M-%S')  # Adjust the format as needed, 2023-11-08-17-35-55
    
    df = pd.read_csv(file_path)
    ''' #work in progress: ignore values over 1000000 ohm
    
    # Apply the filter to exclude values over 1,000,000
    df = df[(df[y1_column] <= 1000000) & (df[y2_column] <= 1000000)]

    if df.empty:
    # Return a default result or handle the empty DataFrame as needed
        return {
            'Timestamp': timestamp,
            'max_value_y1': None,
            'max_value_y2': None,
            'difference_max_value': None,
            'y1_value_at_0V': None,
            'y2_value_at_0V': None,
            'difference_y_at_0V': None,
            'y1_value_at_4V': None,
            'y2_value_at_4V': None,
            'difference_y_at_4V': None,
            'y1_value_at_8V': None,
            'y2_value_at_8V': None,
            'difference_y_at_8V': None,
            'y1_value_at_12V': None,
            'y2_value_at_12V': None,
            'difference_y_at_12V': None,
            'y1_value_at_16V': None,
            'y2_value_at_16V': None,
            'difference_y_at_16V': None,
            'x_for_max_y1': None,
            'x_for_max_y2': None,
            'hysteresis': None,
            'max_derivative_y1': None,
            'max_derivative_y2': None,
            'x_for_max_derivative_y1': None,
            'x_for_max_derivative_y2': None,
            'min_derivative_y1': None,
            'min_derivative_y2': None,
            'x_for_min_derivative_y1': None,
            'x_for_min_derivative_y2': None
            # Add more default values for other fields
        }
    '''
    max_value_y1 = df[y1_column].max()
    max_value_y2 = df[y2_column].max()
    difference_max_value = max_value_y1 - max_value_y2
    y1_value_at_0V = df.loc[df[x_column] == 0, y1_column].values[0]
    y2_value_at_0V = df.loc[df[x_column] == 0, y2_column].values[0]
    difference_y_at_0V = y1_value_at_0V - y2_value_at_0V
    y1_value_at_4V = df.loc[df[x_column] == 4, y1_column].values[0]
    y2_value_at_4V = df.loc[df[x_column] == 4, y2_column].values[0]
    difference_y_at_4V = y1_value_at_4V - y2_value_at_4V
    y1_value_at_8V = df.loc[df[x_column] == 8, y1_column].values[0]
    y2_value_at_8V = df.loc[df[x_column] == 8, y2_column].values[0]
    difference_y_at_8V = y1_value_at_8V - y2_value_at_8V
    y1_value_at_12V = df.loc[df[x_column] == 12, y1_column].values[0]
    y2_value_at_12V = df.loc[df[x_column] == 12, y2_column].values[0]
    difference_y_at_12V = y1_value_at_12V - y2_value_at_12V
    y1_value_at_16V = df.loc[df[x_column] == 16, y1_column].values[0]
    y2_value_at_16V = df.loc[df[x_column] == 16, y2_column].values[0]
    difference_y_at_16V = y1_value_at_16V - y2_value_at_16V
    x_for_max_y1 = df.loc[df[y1_column] == max_value_y1, x_column].values[0]
    x_for_max_y2 = df.loc[df[y2_column] == max_value_y2, x_column].values[0]
    hysteresis = x_for_max_y1 - x_for_max_y2
    derivative_y1 = np.gradient(df[y1_column], df[x_column])
    derivative_y2 = np.gradient(df[y2_column], df[x_column])
    max_derivative_y1 = np.max(derivative_y1)
    max_derivative_y2 = np.max(derivative_y2)
    x_for_max_derivative_y1 = df[x_column][np.argmax(derivative_y1)]
    x_for_max_derivative_y2 = df[x_column][np.argmax(derivative_y2)]
    min_derivative_y1 = np.min(derivative_y1)
    min_derivative_y2 = np.min(derivative_y2)
    x_for_min_derivative_y1 = df[x_column][np.argmin(derivative_y1)]
    x_for_min_derivative_y2 = df[x_column][np.argmin(derivative_y2)]

    return {
        'Timestamp': timestamp,
        'max_value_y1': max_value_y1, 'max_value_y2': max_value_y2, 'difference_max_value': difference_max_value,
        'y1_value_at_0V': y1_value_at_0V, 'y2_value_at_0V':y2_value_at_0V, 'difference_y_at_0V': difference_y_at_0V,
        'y1_value_at_4V': y1_value_at_4V, 'y2_value_at_4V':y2_value_at_4V, 'difference_y_at_4V': difference_y_at_4V,
        'y1_value_at_8V': y1_value_at_8V, 'y2_value_at_8V':y2_value_at_8V, 'difference_y_at_8V': difference_y_at_8V,
        'y1_value_at_12V': y1_value_at_12V, 'y2_value_at_12V':y2_value_at_12V, 'difference_y_at_12V': difference_y_at_12V,
        'y1_value_at_16V': y1_value_at_16V, 'y2_value_at_16V':y2_value_at_16V, 'difference_y_at_16V': difference_y_at_16V,
        'x_for_max_y1': x_for_max_y1, 'x_for_max_y2': x_for_max_y2, 'hysteresis': hysteresis,
        'max_derivative_y1': max_derivative_y1, 'max_derivative_y2': max_derivative_y2,
        'x_for_max_derivative_y1': x_for_max_derivative_y1, 'x_for_max_derivative_y2': x_for_max_derivative_y2,
        'min_derivative_y1': min_derivative_y1, 'min_derivative_y2': min_derivative_y2,
        'x_for_min_derivative_y1': x_for_min_derivative_y1, 'x_for_min_derivative_y2': x_for_min_derivative_y2
    }

def create_plots(data_df, output_folder, id_prefix, element_identifier, date, plot_parameters):
     # Convert the timestamp column to datetime
    data_df['Timestamp'] = pd.to_datetime(data_df['Timestamp'], format='%Y/%m/%d %H:%M:%S')
    
    for param in plot_parameters:
        plt.figure(figsize=(10, 8))
        plt.plot(data_df['Timestamp'], data_df[param['y1']], label=param['label1'])
        plt.plot(data_df['Timestamp'], data_df[param['y2']], label=param['label2'])
        plt.xlabel('Timestamp')
        plt.ylabel(param['ylabel'])
        plt.title(param['title'])
        plt.xticks(rotation=45)
        plt.grid(False)
        plt.legend()
        plot_filename = os.path.join(output_folder, f'{id_prefix}_{element_identifier}_{date}_{param["filename"]}.png')
        plt.savefig(plot_filename)

        # Set the x-axis formatter to show only hours
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))    

# Main directory containing subfolders with combinations
main_directory = r'c:\Users\User\Documents\Git Repository\logs'

# Define column names
y1_column = 'resistance (up) [Ohm]'
y2_column = 'resistance (down) [Ohm]'
x_column = 'gate voltage [V]'

# Loop through subfolders in the main directory
for subdirectory in os.listdir(main_directory):
    subdirectory_path = os.path.join(main_directory, subdirectory)
    if os.path.isdir(subdirectory_path):
        for date_folder in os.listdir(subdirectory_path):
            date_folder_path = os.path.join(subdirectory_path, date_folder)
            if os.path.isdir(date_folder_path):
                chip_identifier, element_identifier, _ = subdirectory.split('_')
                id_prefix, id_number, _ = subdirectory.split('_')
                date = date_folder

                output_folder = os.path.join(date_folder_path, 'parameter_extraction')
                os.makedirs(output_folder, exist_ok=True)

                data_directory = date_folder_path
                csv_filename = os.path.join(output_folder, f'{id_prefix}_{element_identifier}_{date}_parameter analysis.csv')

                if not os.path.exists(csv_filename):
                    data = []
                    for filename in os.listdir(data_directory):
                        if filename.endswith('.csv'):
                            file_path = os.path.join(data_directory, filename)
                            processed_data = process_csv(file_path, y1_column, y2_column, x_column)
                            data.append(processed_data)

                    df = pd.DataFrame(data)
                    df.to_csv(csv_filename, index=False)

                # Plotting
                data_df = pd.read_csv(csv_filename)
                plot_parameters = [
                    
                    # Resistance-based plots
                    {'y1': 'max_value_y1', 'y2': 'max_value_y2', 'ylabel': 'Resistance ($\Omega$)', 'title': 'Rmax evolution', 'label1': 'Rmax (up)', 'label2': 'Rmax (down)', 'filename': 'Rmax'},
                    {'y1': 'difference_max_value', 'y2': 'difference_max_value', 'ylabel': 'Resistance ($\Omega$)', 'title': 'Rmax up - Rmax down evolution', 'label1': '', 'label2': 'R1 - R2', 'filename': 'Rmax1 - Rmax2'},
                    {'y1': 'y1_value_at_0V', 'y2': 'y2_value_at_0V', 'ylabel': 'Resistance ($\Omega$)', 'title': 'R at 0V evolution', 'label1': 'R at 0V (up)', 'label2': 'R at 0V (down)', 'filename': 'R at 0V'},
                    {'y1': 'difference_y_at_0V', 'y2': 'difference_y_at_0V', 'ylabel': 'Resistance ($\Omega$)', 'title': 'R(up) - R(down) at 0V evolution', 'label1': '', 'label2': 'R1 - R2', 'filename': 'R1 - R2 at 0V'},
                    {'y1': 'y1_value_at_4V', 'y2': 'y2_value_at_4V', 'ylabel': 'Resistance ($\Omega$)', 'title': 'R at 4V evolution', 'label1': 'R at 4V (up)', 'label2': 'R at 4V (down)', 'filename': 'R at 4V'},
                    {'y1': 'difference_y_at_4V', 'y2': 'difference_y_at_4V', 'ylabel': 'Resistance ($\Omega$)', 'title': 'R(up) - R(down) at 4V evolution', 'label1': '', 'label2': 'R1 - R2', 'filename': 'R1 - R2 at 4V'},
                    {'y1': 'y1_value_at_8V', 'y2': 'y2_value_at_8V', 'ylabel': 'Resistance ($\Omega$)', 'title': 'R at 8V evolution', 'label1': 'R at 8V (up)', 'label2': 'R at 8V (down)', 'filename': 'R at 8V'},
                    {'y1': 'difference_y_at_8V', 'y2': 'difference_y_at_8V', 'ylabel': 'Resistance ($\Omega$)', 'title': 'R(up) - R(down) at 8V evolution', 'label1': '', 'label2': 'R1 - R2', 'filename': 'R1 - R2 at 8V'},
                    {'y1': 'y1_value_at_12V', 'y2': 'y2_value_at_12V', 'ylabel': 'Resistance ($\Omega$)', 'title': 'R at 12V evolution', 'label1': 'R at 12V (up)', 'label2': 'R at 12V (down)', 'filename': 'R at 12V'},
                    {'y1': 'difference_y_at_12V', 'y2': 'difference_y_at_12V', 'ylabel': 'Resistance ($\Omega$)', 'title': 'R(up) - R(down) at 12V evolution', 'label1': '', 'label2': 'R1 - R2', 'filename': 'R1 - R2 at 12V'},
                    {'y1': 'y1_value_at_16V', 'y2': 'y2_value_at_16V', 'ylabel': 'Resistance ($\Omega$)', 'title': 'R at 16V evolution', 'label1': 'R at 16V (up)', 'label2': 'R at 16V (down)', 'filename': 'R at 16V'},
                    {'y1': 'difference_y_at_16V', 'y2': 'difference_y_at_16V', 'ylabel': 'Resistance ($\Omega$)', 'title': 'R(up) - R(down) at 16V evolution', 'label1': '', 'label2': 'R1 - R2', 'filename': 'R1 - R2 at 16V'},
                    
                    # Gate voltage based plots
                    {'y1': 'x_for_max_y1', 'y2': 'x_for_max_y2', 'ylabel': 'Dirac point', 'title': 'Dirac point evolution', 'label1': 'Vdirac (up)', 'label2': 'Vdirac (down)', 'filename': 'Vdirac'},
                    {'y1': 'hysteresis', 'y2': 'hysteresis', 'ylabel': 'Hysteresis (V)', 'title': 'Hysteresis evolution', 'label1': '', 'label2': 'Hysteresis', 'filename': 'hysteresis'},
                    {'y1': 'max_derivative_y1', 'y2': 'max_derivative_y2', 'ylabel': 'dR/dV max', 'title': 'dR/dV max evolution', 'label1': 'dR/dV (up)', 'label2': 'dR/dV (down)', 'filename': 'dRdV max'},
                    {'y1': 'x_for_max_derivative_y1', 'y2': 'x_for_max_derivative_y2', 'ylabel': 'Vgate at dR/dV max', 'title': 'Vgate at dR/dV max evolution', 'label1': 'Vgate at dR/dV (up)', 'label2': 'Vgate at dR/dV (down)', 'filename': 'Vgate at dRdV max'},
                    {'y1': 'min_derivative_y1', 'y2': 'min_derivative_y2', 'ylabel': 'dR/dV min', 'title': 'dR/dV min evolution', 'label1': 'dR/dV (up)', 'label2': 'dR/dV (down)', 'filename': 'dRdV min'},
                    {'y1': 'x_for_min_derivative_y1', 'y2': 'x_for_min_derivative_y2', 'ylabel': 'Vgate at dR/dV min', 'title': 'Vgate at dR/dV min evolution', 'label1': 'Vgate at dR/dV (up)', 'label2': 'Vgate at dR/dV (down)', 'filename': 'Vgate at dRdV min'},
                    
                    # Add more plot parameters as needed
                ]
                create_plots(data_df, output_folder, id_prefix, element_identifier, date, plot_parameters)
                print([subdirectory] + [date])
                print(' complete')