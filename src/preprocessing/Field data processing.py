# import library
import math
import os
from phreeqpy.iphreeqc.phreeqc_dll import IPhreeqc  # type: ignore
import pandas as pd

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

# phreeqc selected output
selected_output = """
Selected_output

"""

# load field data
df = pd.read_csv("./data/field_data.csv", header=[0])

# date
df[("Date")] = pd.to_datetime(df[("Date")], format="%Y-%m-%d", errors="raise")

print(df)

exit()
