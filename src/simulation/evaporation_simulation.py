# import library
import math
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from phreeqpy.iphreeqc.phreeqc_dll import IPhreeqc  # type: ignore

# create an iphreeqc instance
iphreeqc = IPhreeqc()

# database path and lists
db_path = "/usr/local/share/doc/IPhreeqc/database"
db_list = sorted(os.listdir(db_path))

# calculate rows for 1 col and total cols of database list
db_list_rows = 5
db_list_cols = math.ceil(len(db_list) / db_list_rows)

# create table
db_list_table = []
for i in range(db_list_rows):
    row = []
    for j in range(db_list_cols):
        idx = j * db_list_rows + i
        if idx < len(db_list):
            row.append(f"{idx+1}. {db_list[idx]}")
        else:
            row.append("")
    db_list_table.append(row)

# calculate max col width
db_list_cols_widths = [
    max(len(db_list_table[r][c]) for r in range(db_list_rows))
    for c in range(db_list_cols)
]

# print available database list
print("\nAvailable database list:\n")
for row in db_list_table:
    for c, cell in enumerate(row):
        print(cell.ljust(db_list_cols_widths[c] + 2), end="")
    print()

# select the number of the database
while True:
    select_db = input(
        f"\nInput the number (1-{len(db_list)}) of the database to load: "
    ).strip()
    try:
        n = int(select_db)
        if not (1 <= n <= len(db_list)):
            raise ValueError
    except ValueError:
        print(
            "\nFailed to load the database. Please enter the number from 1 to "
            f"{len(db_list)}"
        )
        for row in db_list_table:
            for c, cell in enumerate(row):
                print(cell.ljust(db_list_cols_widths[c] + 2), end="")
            print()
        continue
    else:
        break

# load phreeqc database
selected_db = db_list[n - 1]
sel_db_path = f"/usr/local/share/doc/IPhreeqc/database/{selected_db}"

# load phreeqc database
print(f"\nTrying to load the PHREEQC database: {selected_db}")
try:
    iphreeqc.load_database(sel_db_path)
    print(f"\nSuccessfully Loaded the PHREEQC database: {selected_db}\n")
except Exception as e:
    print("Failed to Load the PHREEQC database:", e)
    exit(1)

# Load field data from CSV as a pandas DataFrame
parent_dir = Path(__file__).resolve().parent.parent.parent
csv_path = parent_dir / "data" / "calculated_data.csv"
calculated_data = pd.read_csv(csv_path)

# Load river water data from calculated data
river_rowdata = (
    (calculated_data["Sample type"] == "Water")
    & (calculated_data["Water body type"] == "River")
    & (calculated_data["pH"].notna())
    & (calculated_data["Temperature [C]"].notna())
    & (calculated_data["Na+ concentration [ppm]"].notna())
    & (calculated_data["Ca++ concentration [ppm]"].notna())
    & (calculated_data["Cl- concentration [ppm]"].notna())
    & (calculated_data["Ca++ concentration [ppm]"].notna())
    & (calculated_data["K+ concentration [ppm]"].notna())
    & (calculated_data["Mg++ concentration [ppm]"].notna())
    & (calculated_data["SO4-- concentration [ppm]"].notna())
    & (calculated_data["Alkalinity [meq/L]"].notna())
)

river_data = calculated_data[river_rowdata]

# Define molar masses for elements and compounds
Na_molar_mass = 22.9898
Cl_molar_mass = 35.453
Ca_molar_mass = 40.078
K_molar_mass = 39.0983
Mg_molar_mass = 24.305
Si_molar_mass = 28.0855
SO4_molar_mass = 96.06
HCO3_molar_mass = 61.016
NO2_molar_mass = 46.0055
NO3_molar_mass = 62.0049

# Input data
sim_time = 2000  # time
bts_river_inflow = 2.6e11  # L/time
bts_lake_volume = 2.335e12  # L
temp_river_inflow = 0.1  # L/time
temp_lake_volume = 1  # L
MHC_log_k = 3.1488  # Monohydrocalcite log_k
AMC_log_k = 4.7388  # AMC_TK log_k
MSH_log_k = 6.841  # MSH075KF log_k

# Loop for each river data simulation
print("Starting evaporation simulation...\n")
for idx, row in river_data.iterrows():
    current_input = {
        "pH": row["pH"],
        "Na+": row["Na+ concentration [ppm]"] / Na_molar_mass,  # Convert to mmol/kgw
        "Cl-": row["Cl- concentration [ppm]"] / Cl_molar_mass,  # Convert to mmol/kgw
        "Ca+2": row["Ca++ concentration [ppm]"] / Ca_molar_mass,  # Convert to mmol/kgw
        "K+": row["K+ concentration [ppm]"] / K_molar_mass,  # Convert to mmol/kgw
        "Mg+2": row["Mg++ concentration [ppm]"] / Mg_molar_mass,  # Convert to mmol/kgw
        "Si": row["Si concentration [ppm]"] / Si_molar_mass,  # Convert to mmol/kgw
        "SO4-2": row["SO4-- concentration [ppm]"]
        / SO4_molar_mass,  # Convert to mmol/kgw
        "NO2-": row["NO2- concentration [ppm]"] / NO2_molar_mass,  # Convert
        "NO3-": row["NO3- concentration [ppm]"] / NO3_molar_mass,  # Convert
        "ALK": row["Alkalinity [meq/L]"],  # mmol/kgw
        "MHC": 0,
        "AMC": 0,
        "MSH": 0,
        "Gypsum": 0,
    }
    print(
        f"\nSimulating river data index: {row["Sample name"]} ({idx + 1}/{len(calculated_data)})"
    )
    if row["Water system name"] == "Boon Tsagaan Lake":
        # Use Boon Tsagaan Lake specific values
        river_inflow = bts_river_inflow
        lake_volume = bts_lake_volume
        time_unit = "years"
    else:
        # Use the river data values
        river_inflow = temp_river_inflow
        lake_volume = temp_lake_volume
        time_unit = "Temporary inflow and volume values"
    evap_volume = river_inflow

    # Result export path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    parent_dir = Path(__file__).resolve().parent.parent.parent
    output_path = (
        parent_dir
        / "data"
        / "Simulated data"
        / f"Evap_sim_{row['Sample name']}({row['Sampling Date']})_{timestamp}.csv"
    )

    # Define log path and entry
    log_path = parent_dir / "data" / "Simulated data" / "Simulation_log.csv"
    log_entry = {
        "Index": idx,
        "Timestamp": timestamp,
        "Water system name": row["Water system name"],
        "Sample name": row["Sample name"],
        "Sampling date": row["Sampling Date"],
        "File name": output_path.name,
        "Simulation time": sim_time,
        "River inflow [L/time]": river_inflow,
        "Lake volume [L]": lake_volume,
        "Evaporation volume [L/time]": evap_volume,
        "Time unit": time_unit,
        "Minerals": "Monohydrocalcite, AMC_TK, MSH075KF, Gypsum",
        "MHC log_k": MHC_log_k,
        "AMC log_k": AMC_log_k,
        "MSH log_k": MSH_log_k,
        "CO2(g) fugacity": row["si_CO2(g)"],
    }

    # Check whether the log exists
    exclude_cols = {"Timestamp", "File name", "Index"}
    compare_cols = [k for k in log_entry.keys() if k not in exclude_cols]
    if log_path.exists():
        existing = pd.read_csv(log_path, dtype=str)
        if set(compare_cols).issubset(existing.columns):
            is_duplicate = (
                (existing[compare_cols] == pd.Series(log_entry)[compare_cols]).all(
                    axis=1
                )
            ).any()
            if is_duplicate:
                print(
                    f"Simulation for {row['Sample name']} on same conditions already exists. Skipping."
                )
                continue

    # Define the initial result list
    result = []

    for i in range(0, sim_time):
        # Evaporation simulation
        evap_calc = f"""

        PHASES
        Monohydrocalcite
            CaCO3:H2O + H+ = Ca+2 + H2O + HCO3-
            log_k     {MHC_log_k}
        AMC_TK
            MgCO3:3H2O + H+ = 3H2O + HCO3- + Mg+2
            log_k     {AMC_log_k}
        MSH075KF
            Mg0.75SiO4H2.5 + 1.5H+ = 2H2O + SiO2 + 0.75Mg+2
            log_k     {MSH_log_k}
        Gypsum

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
            N(3)    {current_input['NO2-']}
            N(5)    {current_input['NO3-']}
            Cl      {current_input['Cl-']}
            Alkalinity {current_input['ALK']} as HCO3-

        SOLUTION 2 # River water
            pH      {row['pH']}
            temp    25 # degrees Celsius
            -water  {river_inflow / lake_volume} # kg
            density 1.0 # g/cm^3
            units   mmol/kgw
            Na      {row['Na+ concentration [ppm]'] / Na_molar_mass}
            Ca      {row['Ca++ concentration [ppm]'] / Ca_molar_mass}
            K       {row['K+ concentration [ppm]'] / K_molar_mass}
            Mg      {row['Mg++ concentration [ppm]'] / Mg_molar_mass}
            Si      {row['Si concentration [ppm]'] / Si_molar_mass}
            S(6)    {row['SO4-- concentration [ppm]'] / SO4_molar_mass}
            N(3)    {row['NO2- concentration [ppm]'] / NO2_molar_mass}
            N(5)    {row['NO3- concentration [ppm]'] / NO3_molar_mass}
            Cl      {row['Cl- concentration [ppm]'] / Cl_molar_mass}
            Alkalinity {row['Alkalinity [meq/L]']}

        MIX 3
            1   1
            2   1

        REACTION 3 # Evaporation of inflow water
            H2O        -1
            {evap_volume * 55.525397 / lake_volume} moles in 1 steps

        EQUILIBRIUM_PHASES 3
            CO2(g)    {row['si_CO2(g)']} 10
            Monohydrocalcite 0 {current_input['MHC']}
            AMC_TK    0 {current_input['AMC']}
            MSH075KF  0 {current_input['MSH']}
            Gypsum    0 {current_input['Gypsum']}

        SELECTED_OUTPUT
            -file                 false
            -high_precision       true
            -reset                true
            -step                 false
            -pH                   true
            -state                false
            -pe                   false
            -charge_balance       false
            -ionic_strength       true
            -percent_error        true
            -time                 false
            -distance             false
            -reaction             false
            -simulation           false
            -solution             false
            -alkalinity           true
            -water                true
            -totals               Na  Ca  S(6)  C(4) K Si Mg Cl N(3) N(5)
            -equilibrium_phases   AMC_TK  Monohydrocalcite  MSH075KF Gypsum
            -saturation_indices   AMC_TK  Monohydrocalcite  MSH075KF Gypsum
            -activities           Na+ Ca+2 K+ Mg+2 HCO3- Cl- SO4-2 Si CO3-2
            -molalities           Na+ Ca+2 K+ Mg+2 HCO3- Cl- SO4-2 Si CO3-2

        """

        # Run the PHREEQC
        print(f"Simulation ({i + 1}/{sim_time})", end="\r", flush=True)
        try:
            iphreeqc.run_string(evap_calc)
        except Exception as e:
            print("PHREEQC Error :", e)
        # Output
        evap_output = iphreeqc.get_selected_output_array()
        evap_header = ["time", *evap_output[0]]
        evap_origin = [0, *evap_output[2]]
        evap_result = [i + 1, *evap_output[-1]]
        result.append(evap_result)
        if i == 0:
            # Add original values to the first row
            result.insert(0, evap_origin)

        # Result feedback
        values = dict(zip(evap_header, evap_result))
        current_input["Na+"] = values.get("Na(mol/kgw)") * 1000
        current_input["Cl-"] = values.get("Cl(mol/kgw)") * 1000
        current_input["Ca+2"] = values.get("Ca(mol/kgw)") * 1000
        current_input["K+"] = values.get("K(mol/kgw)") * 1000
        current_input["Mg+2"] = values.get("Mg(mol/kgw)") * 1000
        current_input["Si"] = values.get("Si(mol/kgw)") * 1000
        current_input["SO4-2"] = values.get("S(6)(mol/kgw)") * 1000
        current_input["ALK"] = values.get("Alk(eq/kgw)") * 1000
        current_input["pH"] = values.get("pH")
        current_input["MHC"] = values.get("Monohydrocalcite")
        current_input["MSH"] = values.get("MSH075KF")
        current_input["AMC"] = values.get("AMC_TK")
        current_input["Gypsum"] = values.get("Gypsum")

    # Create data frame
    evap_df = pd.DataFrame(result, columns=evap_header)
    evap_df["Na+ [ppm]"] = evap_df["Na(mol/kgw)"] * 1000 * Na_molar_mass
    evap_df["Cl- [ppm]"] = evap_df["Cl(mol/kgw)"] * 1000 * Cl_molar_mass
    evap_df["SO4-- [ppm]"] = evap_df["S(6)(mol/kgw)"] * 1000 * SO4_molar_mass
    evap_df["HCO3- [ppm]"] = evap_df["C(4)(mol/kgw)"] * 1000 * HCO3_molar_mass
    evap_df["K+ [ppm]"] = evap_df["K(mol/kgw)"] * 1000 * K_molar_mass
    evap_df["Ca++ [ppm]"] = evap_df["Ca(mol/kgw)"] * 1000 * Ca_molar_mass
    evap_df["Mg++ [ppm]"] = evap_df["Mg(mol/kgw)"] * 1000 * Mg_molar_mass
    evap_df["Si [ppm]"] = evap_df["Si(mol/kgw)"] * 1000 * Si_molar_mass
    evap_df["Alkalinity [meq/L]"] = (
        evap_df["Alk(eq/kgw)"] * 1000
    )  # Convert to meq/L as HCO3-

    # Construct the log dataframe
    log_df = pd.DataFrame([log_entry])
    log_df.to_csv(log_path, mode="a", header=not log_path.exists(), index=False)
    print(f"{output_path.name} exported.\n{log_path.name} updated.\n\n")

    # Print the result as CSV
    evap_df.to_csv(output_path, index=False)

print("Evaporation simulation completed successfully.\n")

exit()
