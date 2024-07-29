#[16:01] Matthew Barnes
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

def find_vcnp(df, window_size, polynomial_order, num_x_points, output_dir, csv_filename, id_number, element_number):
    # Filter values that are greater than 1,000,000
    df = df[(df['resistance1'] <= 1000000) & (df['resistance2'] <= 1000000)]
    
    r_max_idx1 = df['resistance1'].idxmax()
    r_max_idx2 = df['resistance2'].idxmax()

    # Create subsets of data for 'resistance1' and 'resistance2' separately
    df_subset1 = df.iloc[r_max_idx1 - 2 * window_size: r_max_idx1 + (2 * window_size + 1)]
    df_subset_win1 = df.iloc[r_max_idx1 - window_size: r_max_idx1 + window_size + 1]

    df_subset2 = df.iloc[r_max_idx2 - 2 * window_size: r_max_idx2 + (2 * window_size + 1)]
    df_subset_win2 = df.iloc[r_max_idx2 - window_size: r_max_idx2 + window_size + 1]

    # Check if subsets are empty for 'resistance1' and 'resistance2'
    
    if df_subset1.empty or df_subset_win1.empty or df_subset2.empty or df_subset_win2.empty:
        print(f"Empty subset encountered for window_size={window_size}, polynomial_order={polynomial_order}, num_x_points={num_x_points} in {csv_filename}. Skipping.")
        return  # Skip this iteration

    # Continue with data processing for 'resistance1' and 'resistance2' separately
    x1 = df_subset_win1.volt.to_numpy()
    xp1 = np.linspace(x1.min(), x1.max(), num_x_points)
    y1 = df_subset_win1.resistance1.to_numpy()
    z1 = np.polyfit(x1, y1, polynomial_order)
    p1 = np.poly1d(z1)

    x2 = df_subset_win2.volt.to_numpy()
    xp2 = np.linspace(x2.min(), x2.max(), num_x_points)
    y2 = df_subset_win2.resistance2.to_numpy()
    z2 = np.polyfit(x2, y2, polynomial_order)
    p2 = np.poly1d(z2)

    # Create an output folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    plt.scatter(df_subset1.volt, df_subset1.resistance1, label="Raw data (Resistance1)", marker='+', color='k')
    plt.scatter(df_subset_win1.volt, df_subset_win1.resistance1, label="$\pm$%i points subset around R$_{max1}$" % window_size, color='g')
    plt.plot(xp1, p1(xp1), label='Polynomial fit R1', color='b')
    plt.axvline(xp1[np.argmax(p1(xp1))], label="Vcnp1 from fit = %.5f V" % xp1[np.argmax(p1(xp1))], color='b')

    plt.scatter(df_subset2.volt, df_subset2.resistance2, label="Raw data (Resistance2)", marker='x', color='m')
    plt.scatter(df_subset_win2.volt, df_subset_win2.resistance2, label="$\pm$%i points subset around R$_{max2}$" % window_size, color='c')
    plt.plot(xp2, p2(xp2), label='Polynomial fit R2', color='r')
    plt.axvline(xp2[np.argmax(p2(xp2))], label="Vcnp2 from fit = %.5f V" % xp2[np.argmax(p2(xp2))], color='r')

    plt.scatter(df.volt.iloc[r_max_idx1], df.resistance1.iloc[r_max_idx1], label="Raw Vcnp1 = %.2f V" % df.volt.iloc[r_max_idx1], color='y')
    plt.scatter(df.volt.iloc[r_max_idx2], df.resistance2.iloc[r_max_idx2], label="Raw Vcnp2 = %.2f V" % df.volt.iloc[r_max_idx2], color='b')

    plt.title("window size = %i, poly_order = %i, x_points = %i" % (window_size, polynomial_order, num_x_points))
    plt.legend()
    plt.xlabel('Voltage (V)')
    plt.ylabel("Resistance ($\Omega$)")

    # Save the plot directly in the fitting_parameter folder with the same name as the CSV file
    csv_filename_without_extension = os.path.splitext(os.path.basename(csv_filename))[0]
    plot_filename = f"{csv_filename_without_extension}_win_{window_size}_poly-order_{polynomial_order}_x-points_{num_x_points}.png"
    plot_filepath = os.path.join(output_dir, plot_filename)

    plt.savefig(plot_filepath)
    plt.close()

    # Record Vcnp in a CSV file within the fitting_parameter folder
    vcnp_filename = os.path.join(output_dir, f"ID_{id_number}_element {element_number}_Dirac_point_fit_values.csv")
    vcnp_data = pd.DataFrame({"Window_Size": [window_size], "Poly_Order": [polynomial_order], "X_Points": [num_x_points], "Vcnp1": [xp1[np.argmax(p1(xp1))]], "Vcnp2": [xp2[np.argmax(p2(xp2))]]})
    if not os.path.exists(vcnp_filename):
        vcnp_data.to_csv(vcnp_filename, index=False)
    else:
        vcnp_data.to_csv(vcnp_filename, index=False, mode='a', header=False)

def parse_csv_filename(csv_filename):
    # Parse the details from the CSV filename
    filename_parts = csv_filename.split('_')
    id_prefix = filename_parts[0]
    id_number = filename_parts[1]
    element_number = filename_parts[2]
    date = filename_parts[3].split('.')[0]  # Remove the ".csv" extension
    conditions = filename_parts[4]
    cycle_number = filename_parts[5]
    
    return id_prefix, id_number, element_number, date, conditions, cycle_number

def process_id_subdirectories(main_dir):
    # Iterate through "ID_XXX_element n" subdirectories within the main directory
    processed_files = []
    
    for id_subdir in os.listdir(main_dir):
        id_subdir_path = os.path.join(main_dir, id_subdir)
        
        if os.path.isdir(id_subdir_path):
            print(f"Processing ID subdirectory: {id_subdir_path}")
            
            # Now, within each "ID_XXX_element n" subdirectory, iterate through dated folders
            for dated_subdir in os.listdir(id_subdir_path):
                dated_subdir_path = os.path.join(id_subdir_path, dated_subdir)
                
                if os.path.isdir(dated_subdir_path):
                    print(f"Processing dated subdirectory: {dated_subdir_path}")
                    
                    # Construct the output directory path within the dated folder
                    output_dir = os.path.join(dated_subdir_path, "fitting_parameters")
                    
                    # Ensure that the output directory exists
                    os.makedirs(output_dir, exist_ok=True)

                    csv_files = glob.glob(os.path.join(dated_subdir_path, '*.csv'))
                    
                    # Iterate through CSV files in the dated folder
                    for csv_filename in csv_files:
                        if csv_file not in processed_files:
                            print(f"Processing CSV file: {csv_filename}")
                            
                            # Parse the CSV filename to extract details
                            id_prefix, id_number, element_number, date, conditions, cycle_number = parse_csv_filename(csv_filename)
                            
                            # Load the CSV file
                            csv_file = os.path.join(dated_subdir_path, csv_filename)
                            df = pd.read_csv(csv_file, sep=",", header=0, names=("volt", "resistance1", "resistance2"), usecols=[0, 1, 2])
                            
                            windows = [25]                  #[1, 3, 5, 10, 25]
                            polys = [5]                     #[2, 3, 5, 10]
                            xs = [10000]                    #[10, 100, 1000, 10000] 
                            
                            for polynomial_order in polys:
                                for num_x_points in xs:
                                    for window_size in windows:
                                        # Pass the fitting_parameter directory as the output_dir
                                        fitting_parameter_dir = os.path.join(dated_subdir_path, "fitting_parameters")
                                        
                                        # Pass the csv_filename without the path as an argument to find_vcnp function
                                        csv_filename_without_path = os.path.basename(csv_filename)
                                        
                                        # Call find_vcnp with the correct output_dir
                                        find_vcnp(df, window_size, polynomial_order, num_x_points, fitting_parameter_dir, csv_filename_without_path, id_number, element_number)

if __name__ == "__main__":
    main_directory = r'c:\Users\User\Documents\Git Repository\logs'
    process_id_subdirectories(main_directory)
    