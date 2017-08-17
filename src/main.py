import os
import csv as CSV
import numpy as np
import warnings
import xlwt
import time


# 경고 무시
warnings.simplefilter("ignore")
# 메모리 데이터 초기화
RESULTS = {}
ABS_PATH = os.path.dirname(os.path.abspath(__file__))
RES_PATH = '../res'
OUTPUT_PATH = '../output'
txt_files = [f for f in os.listdir(os.path.join(ABS_PATH,RES_PATH)) if f.endswith('.txt')]
csv_files = [f for f in os.listdir(os.path.join(ABS_PATH,RES_PATH)) if f.endswith('.csv')]
workbook = xlwt.Workbook(encoding='utf-8')
workbook.default_style.font.height = 20*11
current_milli_time = lambda: int(round(time.time() * 1000))
output_file_name = str(current_milli_time())
# 삼각함수
cos = np.cos
sin = np.sin
arcsin = np.arcsin
pow = np.power

# FILE LOAD
for txt in txt_files:
    file_path = os.path.join(ABS_PATH,RES_PATH,txt)
    basename = os.path.splitext(os.path.basename(file_path))[0]
    RESULTS[basename] = {}
    RESULTS[basename]['const'] = {}
    f = open(file_path).read().splitlines()
    for line in f:
        RESULTS[basename]['const'][line.split(':')[0]] = float(line.split(':')[1])

for csv in csv_files:
    file_path = os.path.join(ABS_PATH,RES_PATH,csv)
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
    # 시트 생성
    worksheet = workbook.add_sheet(subject)

    # LOAD DATASET
    p_data = data['dataset']["p'"]
    U_ro_data = data['dataset']["U_ro"]
    # LOAD CONST
    G = data['const']['G']
    p_fe = data['const']['p_fe']
    p_o = data['const']['p_o']
    r_o = data['const']['r_o']
    phi_r = data['const']['phi_r']
    nu = data['const']['nu']

    # INIT RESULT PARAMS
    min_i = None
    min_j = None
    min_c = None
    min_phi = None
    min_V = None
    min_p_data_filtered = None
    min_U_ro_data_filtered = None
    min_U_ro_cal = None
    for i in range(50):
        i = i + 1
        p_f = ((0.4 * p_fe / 50) * i) + (0.8 * p_fe)
        p_data_filtered = p_data[p_data > p_f]
        U_ro_data_filtered = U_ro_data[p_data > p_f]
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
            rf_ro_cal = pow((p_data_filtered * (m-1) + sigma) / (p_f * (m-1) + sigma),(m / (m-1)))
            U_ro_cal = (r_o / (2 * G)) * ((b1 * pow(rf_ro_cal,(m-1)/m)) + (b2 * pow(rf_ro_cal,(n+1)/n)) + b3)
            V = sum(pow(U_ro_cal - U_ro_data_filtered,2)) / len(U_ro_cal)

            if min_V == None:
                min_i = i
                min_j = j
                min_V = V
                min_c = c
                min_phi = phi
                min_p_data_filtered = p_data_filtered
                min_U_ro_data_filtered = U_ro_data_filtered
                min_U_ro_cal = U_ro_cal
            else:
                if min_V >= V:
                    min_i = i
                    min_j = j
                    min_V = V
                    min_c = c
                    min_phi = phi
                    min_p_data_filtered = p_data_filtered
                    min_U_ro_data_filtered = U_ro_data_filtered
                    min_U_ro_cal = U_ro_cal

    worksheet.write(0,0,'min_k')
    worksheet.write(1, 0, 50*(min_i-1) + min_j)
    worksheet.write(0,1, 'min_c')
    worksheet.write(1, 1, min_c)
    worksheet.write(0,2, 'min_phi')
    worksheet.write(1, 2, min_phi)
    worksheet.write(0,3, 'min_V')
    worksheet.write(1, 3, min_V)

    worksheet.write(0,4, 'min_p_data')
    worksheet.write(0,5, 'min_U_ro_data')
    worksheet.write(0,6, 'min_U_ro_cal')

    for i,val in enumerate(min_p_data_filtered):
        worksheet.write(i+1,4,val)
    for i,val in enumerate(min_U_ro_data_filtered):
        worksheet.write(i+1,5, val)
    for i,val in enumerate(min_U_ro_cal):
        worksheet.write(i+1,6, val)

    print(f'최소 V = {min_V}')
    print(f'k = {50*(min_i-1) + min_j}')
    print(f'c = {min_c}')
    print(f'phi = {min_phi}')

    print("##########################################")

workbook.save(os.path.join(ABS_PATH,OUTPUT_PATH,f'{output_file_name}.xls'))