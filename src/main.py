import os
import csv as CSV
import numpy as np
import warnings

# 경고 무시
warnings.simplefilter("ignore")
# 메모리 데이터 초기화
RESULTS = {}
RES_PATH = '../res'
txt_files = [f for f in os.listdir(RES_PATH) if f.endswith('.txt')]
csv_files = [f for f in os.listdir(RES_PATH) if f.endswith('.csv')]

# 삼각함수
cos = np.cos
sin = np.sin
arcsin = np.arcsin
pow = np.power

# FILE LOAD
for txt in txt_files:
    file_path = os.path.join(RES_PATH,txt)
    basename = os.path.splitext(os.path.basename(file_path))[0]
    RESULTS[basename] = {}
    RESULTS[basename]['const'] = {}
    f = open(file_path).read().splitlines()
    for line in f:
        RESULTS[basename]['const'][line.split(':')[0]] = float(line.split(':')[1])

for csv in csv_files:
    file_path = os.path.join(RES_PATH,csv)
    basename = os.path.splitext(os.path.basename(file_path))[0]
    RESULTS[basename]['dataset'] = {}
    f = open(file_path,newline='')
    reader = CSV.reader(f, delimiter=',')
    next(reader)
    RESULTS[basename]['dataset']["p'"] = np.array([float(row[0].strip()) for row in reader],dtype=np.float64)
    f.seek(0)
    next(reader)
    RESULTS[basename]['dataset']["U_ro"] = np.array([float(row[1].strip()) for row in reader],dtype=np.float64)


# MAIN LOGIC
print("##########################################")
for subject,data in RESULTS.items():
    print(f'{subject}에 대한 분석을 실시합니다.')
    # LOAD CONST
    G = data['const']['G']
    p_fe = data['const']['p_fe']
    p_o = data['const']['p_o']
    r_o = data['const']['r_o']
    phi_r = data['const']['phi_r']
    nu = data['const']['nu']
    min_i = 0
    min_j = 0
    min_c = None
    min_phi = None
    min_V = None
    p_data = data['dataset']["p'"]
    U_ro_data = data['dataset']["U_ro"]
    for i in range(50):
        i = i + 1
        p_f = ((0.4 * p_fe / 50) * i) + (0.8 * p_fe)
        for j in range(50):
            j = j+1
            #식값 계산
            phi = (((90 - phi_r)/50) * j) + phi_r
            psi = arcsin((sin(phi) - sin(phi_r)) / (1-(sin(phi) * sin(phi_r))))
            c = (p_f - (p_o * (sin(phi)+1))) / cos(phi)
            m = (1 + sin(phi)) / (1-sin(phi))
            n = (1 + sin(psi)) / (1-sin(psi))
            sigma = 2*c*cos(phi) / (1-sin(phi))
            b1 = (-2 * m / (m-1)) * ((1-nu) * ((1+(m*n))/(m+n)) - nu)*(p_f - p_o)
            b2 = (2*n*(1-nu)*((m+1)) / ((m+n))*(p_f - p_o))
            b3 = ((1-(2*nu))*((m+1)) / ((m-1))*(p_f - p_o))

            rf_ro_cal = pow((p_data * (m-1) + sigma) / (p_f * (m-1) + sigma),(m / (m-1)))
            U_ro_cal = (r_o / (2 * G)) * ((b1 * pow(rf_ro_cal,(m-1)/m)) + (b2 * pow(rf_ro_cal,(n+1)/n)) + b3)
            V = sum((U_ro_cal - U_ro_data) ** 2) / len(U_ro_cal)

            if min_V == None:
                min_i = i
                min_j = j
                min_V = V
                min_c = c
                min_phi = phi
            else:
                if min_V >= V:
                    min_i = i
                    min_j = j
                    min_V = V
                    min_c = c
                    min_phi = phi

    print(f'최소 V = {min_V}')
    print(f'k = {50*(min_i-1) + min_j}')
    print(f'c = {min_c}')
    print(f'phi = {min_phi}')

    print("##########################################")