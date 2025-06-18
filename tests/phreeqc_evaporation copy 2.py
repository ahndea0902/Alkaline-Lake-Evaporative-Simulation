# Import library
import pandas as pd

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
temp_input = 25
Na_input = 8.94
Cl_input = 10
Ca_input = 25.6
K_input = 1.71
Mg_input = 8.10
Si_input = 4.50
SO4_input = 21.1
ALK_input = 1.63
MHC_input = 0
MSH_input = 0
AMC_input = 0
Water_input = 1
CO2_pressure_input = -3.3  # log10 of CO2 pressure
flow_rate = 2.6e8  # in m3/yr
lake_volume = 2.335e9  # in m3


simulation_time = 100  # in years

current_input = {
    "pH": pH_input,
    "ALK": ALK_input,  # Alkalinity in mmol/kgw
    "Na+": Na_input / 22.9898,  # Convert to mol/kgw
    "Cl-": Cl_input / 35.453,  # Convert to mol/kgw
    "Ca+2": Ca_input / 40.078,  # Convert to mol/kgw
    "K+": K_input / 39.0983,  # Convert to mol/kgw
    "Mg+2": Mg_input / 24.305,  # Convert to mol/kgw
    "Si": Si_input / 28.0855,  # Convert to mol/kgw
    "SO4-2": SO4_input / 32.065,  # Convert to mol/kgw
    "MHC": MHC_input,
    "MSH": MSH_input,
    "AMC": AMC_input,
    "Water": Water_input,
}

for year in range(simulation_time):

    # Define the river water input
    phreeqc_input = f"""
SOLUTION 1 # Current Lake water
    pH      {current_input['pH']}
    temp    {temp_input} # degrees Celsius
    water   {current_input['Water']} # kg
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

PHASES
MHC
    CaCO3:H2O + H+ = Ca+2 + HCO3- + H2O
    log_k 3.1488
MSH
    Mg0.75SiO4H2.5 + 1.5 H+ = 0.75 Mg+2 + H4SiO4
    log_k 6.841
AMC
    MgCO3:3H2O + H+ = Mg+2 + 3 H2O + HCO3-
    log_k 4.7388

REACTION 1
    H2O {-flow_rate / (lake_volume * 0.01801528)}

EQUILIBRIUM_PHASES 3 # Fix CO2(g) at -3.3 log10
    CO2(g) {CO2_pressure_input} 1e+10
    MHC 0 {current_input['MHC']}
    AMC 0 {current_input['AMC']}
    MSH 0 {current_input['MSH']}

SELECTED_OUTPUT
    -file false
    -reset false
    -step false
    -simulation false
    -state false
    -solution false
    -high_precision false
    -time false
    -pH true
    -pe false
    -temperature false
    -ionic_strength false
    -water true
    -charge_balance false
    -percent_error true
    -alkalinity true
    -totals Na C Ca Mg K Cl S Si
    -equilibrium_phases MHC MSH AMC
    -si MHC MSH AMC

END
"""

    # Input whole simulation
    input_string = phreeqc_input

    # Run the PHREEQC
    print(f"{year} Step running...")
    try:
        iphreeqc.run_string(input_string)
        print("\n")
    except Exception as e:
        print("Failed to execute PHREEQC:", e)
        break

    # Print the output step by step
    output = iphreeqc.get_selected_output_array()
    simulated_output = output[-1]
    Result.append(simulated_output)

    label = output[0]

    values = dict(zip(label, simulated_output))
    current_input["Na+"] = values.get(("Na(mol/kgw)"), current_input["Na+"]) * 1000
    current_input["Cl-"] = values.get(("Cl(mol/kgw)"), current_input["Cl-"]) * 1000
    current_input["Ca+2"] = values.get(("Ca(mol/kgw)"), current_input["Ca+2"]) * 1000
    current_input["K+"] = values.get(("K(mol/kgw)"), current_input["K+"]) * 1000
    current_input["Mg+2"] = values.get(("Mg(mol/kgw)"), current_input["Mg+2"]) * 1000
    current_input["Si"] = values.get(("Si(mol/kgw)"), current_input["Si"]) * 1000
    current_input["SO4-2"] = values.get(("S(mol/kgw)"), current_input["SO4-2"]) * 1000
    current_input["ALK"] = values.get(("Alk(eq/kgw)"), current_input["ALK"]) * 1000
    current_input["pH"] = values.get("pH", current_input["pH"])
    current_input["MHC"] = values.get("MHC", current_input["MHC"])
    current_input["MSH"] = values.get("MSH", current_input["MSH"])
    current_input["AMC"] = values.get("AMC", current_input["AMC"])
    current_input["Water"] = values.get("mass_H2O", current_input["Water"])


Result.insert(0, label)

df = pd.DataFrame(Result[1:], columns=Result[0])

df["Na(mol/kgw)"] = df["Na(mol/kgw)"] * 1000 * 22.9898
df["C(mol/kgw)"] = df["C(mol/kgw)"] * 1000 * 12.011
df["Ca(mol/kgw)"] = df["Ca(mol/kgw)"] * 1000 * 40.078
df["Mg(mol/kgw)"] = df["Mg(mol/kgw)"] * 1000 * 24.305
df["K(mol/kgw)"] = df["K(mol/kgw)"] * 1000 * 39.098
df["Cl(mol/kgw)"] = df["Cl(mol/kgw)"] * 1000 * 35.45
df["S(mol/kgw)"] = df["S(mol/kgw)"] * 1000 * 32.065
df["Si(mol/kgw)"] = df["Si(mol/kgw)"] * 1000 * 28.0855

 print(df)
print(df)
