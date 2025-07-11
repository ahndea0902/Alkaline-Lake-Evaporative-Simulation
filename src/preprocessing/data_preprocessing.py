# import library
import math
import os
import sys
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
csv_path = parent_dir / "data" / "field_data.csv"
field_data = pd.read_csv(csv_path)

# Load water data from field data
water_rowdata = (
    (field_data["Sample type"] == "Water")
    & (field_data["pH"].notna())
    & (field_data["Temperature [C]"].notna())
    & (field_data["Na+ concentration [ppm]"].notna())
    & (field_data["Ca++ concentration [ppm]"].notna())
    & (field_data["Cl- concentration [ppm]"].notna())
    & (field_data["Ca++ concentration [ppm]"].notna())
    & (field_data["K+ concentration [ppm]"].notna())
    & (field_data["Mg++ concentration [ppm]"].notna())
    & (field_data["SO4-- concentration [ppm]"].notna())
    & (field_data["Alkalinity [meq/L]"].notna())
)
water_data = field_data[water_rowdata]

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

# Calculate Phreeqc for each water sample
for idx, row in water_data.iterrows():
    # Prepare the input for Phreeqc
    input_data = f"""
    PHASES
        Monohydrocalcite
        CaCO3:H2O + H+ = Ca+2 + H2O + HCO3-
        log_k     3.1488
        AMC_TK
        MgCO3:3H2O + H+ = 3H2O + HCO3- + Mg+2
        log_k     4.7388
        MSH075KF
        Mg0.75SiO4H2.5 + 1.5H+ = 2H2O + SiO2 + 0.75Mg+2
        log_k     6.841
    Solution 1
        pH {row['pH']}
        temp {row['Temperature [C]']}
        -units mg/L
        Na {row['Na+ concentration [ppm]']}
        Cl {row['Cl- concentration [ppm]']}
        Ca {row['Ca++ concentration [ppm]']}
        K {row['K+ concentration [ppm]']}
        Mg {row['Mg++ concentration [ppm]']}
        Si {row['Si concentration [ppm]']}
        S(6) {row['SO4-- concentration [ppm]']}
        N(3) {row['NO2- concentration [ppm]']}
        N(5) {row['NO3- concentration [ppm]']}
        Alkalinity {row['Alkalinity [meq/L]']} meq/L
    Selected_output
        -reset true
        -step false
        -time false
        -simulation false
        -state false
        -solution false
        -pe false
        -reaction false
        -water false
        -total Cl C(4) Na Ca K Mg Si S(6) N(3) N(5)
        -charge_balance true
        -percent_error true
        -distance false
        -ionic_strength true
        -saturation_indices CO2(g) Monohydrocalcite AMC_TK MSH075KF Gypsum
        -ph false
        -temperature false
        -alkalinity true
        -activities Ca+2 Mg+2 CO3-2

    """

    # Run Phreeqc with the input data
    try:
        iphreeqc.run_string(input_data)
    except Exception as e:
        print(f"Error running Phreeqc for sample {idx + 1}: {e}")
        continue

    # Get the output from Phreeqc
    output = iphreeqc.get_selected_output_array()
    sys.stdout.write(
        f"\r\033[2KPreprocessing sample {row["Sample name"]} ({idx +1}/{len(field_data)})"
    )
    sys.stdout.flush()
    output_lastrow = output[-1]  # Get the last row of the output
    headers = output[0]  # Get the headers from the output
    try:
        result
    except NameError:
        result = pd.DataFrame(columns=headers)
    result.loc[idx] = list(output_lastrow)  # Append the output to the result DataFrame

# convert the result unit from mol/kgw to ppm


# Print "Precprocessing complete" message
print("\n\nPreprocessing complete.")

# Join the result with the original water data
calculated_data = field_data.join(result)

# output the result to a CSV file
calculated_data.to_csv(parent_dir / "data" / "calculated_data.csv", index=False)

exit()
