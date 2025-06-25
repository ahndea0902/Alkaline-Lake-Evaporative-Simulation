# Import library
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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

# Define input data

pH_input = 8.5
temp_input = 25  # Celcius
Na_input = 8.94  # ppm
Cl_input = 10  # ppm
Ca_input = 25.6  # ppm
K_input = 1.71  # ppm
Mg_input = 8.10  # ppm
Si_input = 4.50  # ppm
SO4_input = 21.1  # ppm
ALK_input = 1.63  # meq/L

current_input = {
    "pH": pH_input,
    "ALK": ALK_input,  # Alkalinity in mmol/kgw
    "Na+": Na_input / 22.9898,  # Convert to mol/kgw
    "Cl-": Cl_input / 35.453,  # Convert to mol/kgw
    "Ca+2": Ca_input / 40.078,  # Convert to mol/kgw
    "K+": K_input / 39.0983,  # Convert to mol/kgw
    "Mg+2": Mg_input / 24.305,  # Convert to mol/kgw
    "Si": Si_input / 28.0855,  # Convert to mol/kgw
    "SO4-2": SO4_input / 96.06,  # Convert to mol/kgw
}

# Define the phreeqc command
phreeqc_input = f"""

PHASES
Monohydrocalcite
    CaCO3:H2O + H+ = Ca+2 + H2O + HCO3-
    log_k     3.1488
AMC_TK
    MgCO3:3H2O + H+ = 3H2O + HCO3- + Mg+2
    log_k     4.7388
MSH075KF
    Mg0.75SiO4H2.5 + 1.5H+ = H4SiO4 + 0.75Mg+2
    log_k     6.841

SOLUTION 1 # Lake water
    pH      {current_input['pH']}
    temp    25 # degrees Celsius
    -water  1 # kg
    density 1.0 # g/cm^3
    units   mmol/kgw
    Na      {current_input['Na+']}
    Ca      {current_input['Ca+2']}
    K       {current_input['K+']}
    Mg      {current_input['Mg+2']}
    Si      {current_input['Si']}
    S(6)    {current_input['SO4-2']}
    Cl      {current_input['Cl-']}
    Alkalinity {current_input['ALK']} as HCO3

REACTION 1 # Evaporation of inflow water
    H2O        -1
    55.505 moles in 100 steps

EQUILIBRIUM_PHASES 1
    CO2(g)    -3.3 1000
    Monohydrocalcite 0 0
    AMC_TK    0 0
    MSH075KF  0 0

SELECTED_OUTPUT
    -file                 false
    -high_precision       false
    -reset                false
    -step                 true
    -pH                   true
    -alkalinity           true
    -water                true
    -totals               Na  Ca  S(6)  C(4) K Si Mg Cl
    -equilibrium_phases   AMC_TK  Monohydrocalcite  MSH075KF
    -saturation_indices   AMC_TK  Monohydrocalcite  MSH075KF
    -activities           Na+ Ca+2 K+ Mg+2 HCO3- Cl- SO4-2 Si
    -molalities           Na+ Ca+2 K+ Mg+2 HCO3- Cl- SO4-2 Si
    -gases                CO2(g)

"""

# Input whole simulation
input_string = phreeqc_input

# Run the PHREEQC
print("Running...")
try:
    iphreeqc.run_string(input_string)
except Exception as e:
    print("Failed to execute PHREEQC:", e)


# Print the output
output = iphreeqc.get_selected_output_array()

header = output[0]
data = output[1:]
df = pd.DataFrame(data, columns=header)

df.plot(x="mass_H2O", y="pH")
plt.show()

exit()
