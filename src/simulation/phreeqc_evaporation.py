# Import phreeqpy library
from phreeqpy.iphreeqc.phreeqc_dll import IPhreeqc  # type: ignore

# Create an instance of Iphreeqc
iphreeqc = IPhreeqc()

# Load the Phreeqc database
database_path = "/usr/local/share/doc/IPhreeqc/database/phreeqc.dat"
print(f"Trying to load the PHREEQC database: {database_path}")
try:
    iphreeqc.load_database(database_path)
    print("Successfully Loaded the PHREEQC database")
except Exception as e:
    print("Failed to Load the PHREEQC database:", e)
    exit(1)

# Define the PHREEQC input
phreeqc_input = """
SOLUTION 1 # BD_River_Estuary_1_August2nd
    pH      8.5
    temp    19.8 # degrees Celsius
    water   1 # kg
    density 1.0 # g/cm^3
    units   ppm
    Na      8.94
    Cl      10
    Ca      25.6
    K       1.71
    Mg      8.10
    Si      4.50
    SO4     21.1
    Alkalinity 99.5
SELECTED_OUTPUT
    -file false
    -high_precision false
    -simulation true
    -state true
    -solution true
    -pH true
    -temperature true
    -ionic_strength true
    -totals Na Cl
END
"""

# Output settings
step_selected_output = """
SELECTED_OUTPUT
    -file false
    -reset false
    -step true
    -simulation true
    -state true
    -solution true
    -high_precision false
    -pH true
    -pe true
    -temperature true
    -ionic_strength true
    -water true
    -charge_balance true
    -percent_error true
    -alkalinity true
    -totals Na Cl Ca C Mg SO4 HCO3
    -water true

END
"""

# Input the evaporative simulation
evaporation_steps = ""
for i in range(1, 11):
    steps = f"""
USE SOLUTION 1
REACTION {i}
    H2O -0.09
SAVE SOLUTION 1
{step_selected_output}
"""
    evaporation_steps += steps

# Input whole simulation
input_string = phreeqc_input + step_selected_output + evaporation_steps

# Run the PHREEQC
try:
    iphreeqc.run_string(input_string)
    print("Successfully executed PHREEQC")
except Exception as e:
    print("Failed to execute PHREEQC:", e)
    exit(1)

# Print the output step by step
output = iphreeqc.get_selected_output_array()
header = output[0]
step_selected_output = output[1:]

# Print the output
for idx, row in enumerate(step_selected_output, 0):
    print(f"\n=== Step {idx} ===")
    for h, v in zip(header, row):
        # If the data is a float, format it to 3 decimal places
        if isinstance(v, float):
            print(f"{h}: {v:.3e}")
        else:
            print(f"{h}: {v}")
