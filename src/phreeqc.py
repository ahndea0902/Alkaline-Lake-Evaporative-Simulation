from phreeqpy.iphreeqc.phreeqc_dll import IPhreeqc

# 인스턴스 생성
iphreeqc = IPhreeqc()

# 데이터베이스 로드
database_path = "/usr/local/share/doc/IPhreeqc/database/phreeqc.dat"
print(f"📂 데이터베이스 로드 시도 중: {database_path}")
try:
    iphreeqc.load_database(database_path)
    print("✅ 데이터베이스 로드 성공")
except Exception as e:
    print("❌ 데이터베이스 로드 실패:", e)
    exit(1)

# 입력 정의
phreeqc_input = """
SOLUTION 1
    pH      7
    temp    25
    units   mol/kgw
    Na      1
    Cl      1
SELECTED_OUTPUT
    -file false
    -high_precision true
    -pH true
    -temperature true
    -ionic_strength true
    -totals Na Cl
END
"""

# 시뮬레이션 실행
try:
    iphreeqc.run_string(phreeqc_input)
    print("✅ PHREEQC 입력 실행 성공")
except Exception as e:
    print("❌ PHREEQC 입력 실행 중 오류 발생:", e)
    exit(1)

# 결과 출력
output = iphreeqc.get_selected_output_array()
print("📊 Selected Output Array:")
for row in output:
    print(row)
