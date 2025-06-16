# Import library
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

# Result

Result = []

# Define input data

pH_input = 8.5
temp_input = 19.8
Na_input = 8.94
Cl_input = 10
Ca_input = 25.6
K_input = 1.71
Mg_input = 8.10
Si_input = 4.50
SO4_input = 21.1
ALK_input = 1.63
MHC_input = 0
CO2_pressure_input = -3.3  # log10 of CO2 pressure
flow_rate = 2.6e8  # in m3/yr
lake_volume = 2.335e12  # in km3
mol_per_yr = flow_rate * 1000 / (18.015 * lake_volume)


simulation_time = 3  # in years

current_input = {
    "pH": pH_input,
    "ALK": ALK_input,  # Alkalinity in mmol/kgw
    "Na+": Na_input / 22.9898,  # Convert to mol/kgw
    "Cl-": Cl_input / 35.453,  # Convert to mol/kgw
    "Ca+2": Ca_input / 40.078,  # Convert to mol/kgw
    "K+": K_input / 39.0983,  # Convert to mol/kgw
    "Mg+2": Mg_input / 24.305,  # Convert to mol/kgw
    "Si": Si_input / 28.0855,  # Convert to mol/kgw
    "SO4-2": SO4_input / 96.062,  # Convert to mol/kgw
    "MHC": MHC_input,
}

for year in range(simulation_time):

    # Define the river water input
    phreeqc_input = f"""
SOLUTION 1 # Current Lake water
    pH      {current_input['pH']} # pH
    temp    {temp_input} # degrees Celsius
    water   1 # kg
    density 1.0 # g/cm^3
    units   mmol/kgw
    Na      {current_input['Na+']}
    Ca      {current_input['Ca+2']}
    K       {current_input['K+']}
    Mg      {current_input['Mg+2']}
    Si      {current_input['Si']}
    S       {current_input['SO4-2']}
    Cl       {current_input['Cl-']}
    Alkalinity {current_input['ALK']} as HCO3

SOLUTION 2 # Initial river water
    pH      {pH_input} # pH
    temp    {temp_input} # degrees Celsius
    water   {flow_rate / lake_volume} # kg
    density 1.0 # g/cm^3
    units   mmol/kgw
    Na      {Na_input / 22.9898}
    Ca      {Ca_input / 40.078}
    K       {K_input / 39.0983}
    Mg      {Mg_input / 24.305}
    Si      {Si_input / 28.0855}
    S       {SO4_input / 96.062}
    Cl       {Cl_input / 35.453}
    Alkalinity {ALK_input} as HCO3

PHASES
    Monohydrocalcite
    CaCO3:H2O = Ca+2 + HCO3- + H2O - H+
    log_k 3.1488

EQUILIBRIUM_PHASES 1 # Fix CO2(g) at -3.3 log10
    CO2(g) {CO2_pressure_input} 1e+6
    Monohydrocalcite 0 {current_input['MHC']}

MIX 3 # Evaporatied water
    1   1
    2   1
SAVE SOLUTION 3

REACTION 3
    H2O {-flow_rate / (lake_volume * 0.01801528)}

EQUILIBRIUM_PHASES 3 # Fix CO2(g) at -3.3 log10
    CO2(g) {CO2_pressure_input} 1e+6
    Monohydrocalcite 0 {current_input['MHC']}

SELECTED_OUTPUT
    -file false
    -reset false
    -step true
    -simulation true
    -state true
    -solution true
    -high_precision true
    -time true
    -pH true
    -pe true
    -temperature true
    -ionic_strength true
    -water true
    -charge_balance true
    -percent_error true
    -alkalinity true
    -totals Na C Ca Mg K Cl S Si
    -equilibrium_phases Monohydrocalcite
    -si Monohydrocalcite

END
"""

    # Input whole simulation
    input_string = phreeqc_input

    # Run the PHREEQC
    print(f"{year} Step running...")
    try:
        iphreeqc.run_string(input_string)
        print("Successfully executed PHREEQC")
    except Exception as e:
        print("Failed to execute PHREEQC:", e)
        exit(1)

    # Print the output step by step
    output = iphreeqc.get_selected_output_array()
    simulated_output = output[-1]
    Result.append(simulated_output)

    label = output[0]

    values = dict(zip(label, simulated_output))
    current_input["Na+"] = values.get("Na(mol/kgw)", current_input["Na+"])
    current_input["Cl-"] = values.get("Cl(mol/kgw)", current_input["Cl-"])
    current_input["Ca+2"] = values.get("Ca(mol/kgw)", current_input["Ca+2"])
    current_input["K+"] = values.get("K(mol/kgw)", current_input["K+"])
    current_input["Mg+2"] = values.get("Mg(mol/kgw)", current_input["Mg+2"])
    current_input["Si"] = values.get("Si(mol/kgw)", current_input["Si"])
    current_input["SO4-2"] = values.get("S(mol/kgw)", current_input["SO4-2"])
    current_input["ALK"] = values.get("Alk(eq/kgw)", current_input["ALK"])
    current_input["pH"] = values.get("pH", current_input["pH"])
    current_input["MHC"] = values.get("Monohydrocalcite", current_input["MHC"])
