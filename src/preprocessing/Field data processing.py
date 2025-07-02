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

# load field data
df = pd.read_csv("./data/field_data.csv", header=[0])

# date
df[("Date")] = pd.to_datetime(df[("Date")], format="%Y-%m-%d", errors="raise")

# 각 데이터의 site 이온 ph등을 변수로 지정해서, for로 반복해서 계산하고, 그 결과를 또 CSV로 저장 ( site 명 및 날짜 포함 )
# 그렇게 나온 데이터를 evaporation 으로 증발시키는 시뮬레이션 돌림
# 그리고, 마지막으로 plot으로 plot함
# 이 모든걸 main으로 실행하고 싶음.

# Water 분류 안에서, 수계를 정하고, 그 중에서 뭘 시뮬레이션 할 지 나타냄
# 결과 폴더를 보고, 
# CSV를 또 그룹으로 묶는 방법이 있나?
# 결과폴더에 이미 존재하는 결과들을 자동적으로 python에 입력?
# 그걸 플롯에서 바로 불러올 수 있도록

# phreeqc calculation
phreeqc_preprocessing = f"""

Phase
Monohydrocalcite
    CaCO3:H2O + H+ = Ca+2 + H2O + HCO3-
    log_k     3.1488
AMC_TK
    MgCO3:3H2O + H+ = 3H2O + HCO3- + Mg+2
    log_k     4.7388
MSH075KF
    Mg0.75SiO4H2.5 + 1.5H+ = 2H2O + SiO2 + 0.75Mg+2
    log_k     6.841
Gypsum

Selected_output
    -file               false
    -high_precision     true
    -reset              true
    -totals             C(4) Na Mg Si S(6) Cl K Ca
    -saturation_indices AMC_TK
                        Monohydrocalcite
                        MSH075KF
                        Gypsum
    -equilibrium_phases AMC_TK
                        Monohydrocalcite
                        MSH075KF
                        Gypsum
    -activities         HCO3-
                        Ca+2
                        Na+
                        Mg+2
                        Cl-
                        SO4-2
                        K+
                        CO3-2
                        CaCO3
                        CO2
                        CaSO4
                        MgSO4
                        CaHCO3+
                        MgHCO3+
                        OH-
                        NaHCO3
                        MgCl+
                        KSO4-
                        NaCO3-
                        CaCl+

Solution 1
    pH  
                        
"""

exit()
