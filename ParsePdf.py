import os, shutil, pandas as pd
from tqdm import tqdm
from read_pdf import read_pdfs
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-gpu')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')
des = os.getcwd()

# pdf파일 분할
def parse_pdf(filename):
    """
    바로 업로드가 가능한 pdf파일과 아닌 파일로 분할하는 작업을 진행합니다.
    """
    print("========================= 작업 가능 파일과 아닌 파일로 분할중입니다. =========================")
    if not os.path.isdir(f'{des}\\{filename}\\Workable-Files'): os.mkdir(f'{des}\\{filename}\\Workable-Files')
    non_equal_df = pd.DataFrame(columns=['crawled_part_num', 'pdf_part_num'])
    part_num_list = []
    pdf_part_num_list = []
    tq = tqdm(os.listdir(f'{des}\\{filename}\\PDF\\'))
    for file in tq:
        path = f'{des}\\{filename}\\PDF\\{file}'
        part_num = file.replace('.pdf', '')
        try:
            pdf_part_num = read_pdfs(path, part_num, filename)
        except Exception as e:
            print(f'{e} has occured. part number is {part_num}')

        if pdf_part_num == part_num:
            shutil.move(f'{des}\\{filename}\\PDF\\{file}', f'{des}\\{filename}\\Workable-Files\\{file}')
        else:
            part_num_list.append(part_num)
            pdf_part_num_list.append(pdf_part_num)
    tq.close()

    non_equal_df['crawled_part_num'] = part_num_list
    non_equal_df['pdf_part_num'] = pdf_part_num_list
    non_equal_df = non_equal_df.dropna(axis=0)
    non_equal_df.to_csv(f'{des}\\{filename}\\재중복검사대상.csv', sep=',', index=False, encoding='utf8')
    print('=============== 파일 분할을 완료했습니다. 작업가능한 파일 수 : {} ==============='.format(len(os.listdir(f"{des}\\{filename}\\Workable-Files\\"))))
    if os.path.isfile(f'{des}\\{filename}\\Workable-Files\\Single-Chip.pdf'): os.remove(f'{des}\\{filename}\\Workable-Files\\Single-Chip.pdf')

# 2차 중복검사
# def re_check(filename, fac_name):
#     print('======================== master page에서 중복검사를 재실시합니다. =================================')
#     driver = webdriver.Chrome(options=options)

#     driver.get("master page link")
#     time.sleep(0.5)

#     driver.switch_to.window(driver.window_handles[-1])
#     time.sleep(0.5)
#     id = driver.find_element(By.NAME, 'id')
#     pw = driver.find_element(By.NAME, 'pwd')
#     id.send_keys('master id')
#     time.sleep(0.5)
#     pw.send_keys('master password')
#     time.sleep(0.5)

#     loggin_button = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[3]/td/input[1]')
#     loggin_button.click()

#     print('================================= 로그인 완료 =================================')
#     driver.find_element(By.XPATH, '/html/body/div[1]/center/table/tbody/tr[3]/td[1]/a').click()
#     time.sleep(0.5)

#     df = pd.read_csv(f'{des}\\{filename}\\재중복검사대상.csv')
#     part_list = list(df['pdf_part_num'])
#     seppered_list = [part_list[i:i+50] for i in range(0, len(part_list), 50)]
#     text_list = []
#     for a in seppered_list:
#         result_text = ''
#         for j in a:
#             result_text += f'{j}\n'

#         fact_name = driver.find_element(By.NAME, 'sFactory')
#         fact_name.send_keys(fac_name)
#         time.sleep(0.5)

#         text_box = driver.find_element(By.NAME, 'S1')
#         text_box.clear()
#         time.sleep(0.5)
#         text_box.send_keys(result_text)
#         time.sleep(0.5)

#         execute = driver.find_element(By.NAME, 'B1')
#         execute.click()
#         time.sleep(0.5)

#         result_text_clip = driver.find_element(By.XPATH, '/html/body/center').text
#         text_list.append(result_text_clip)

#     return text_list

# 2차 중복검사 결과 문자열 전처리
# def pret(filename, fact_name):
#     result_text_list = re_check(filename, fact_name)
#     dup_lists = []
#     for result_text in result_text_list: 
#         first_spot = result_text.find(']') 
#         last_spot = result_text.find('Yes(') 
#         treated = result_text[first_spot+1:last_spot]
#         results = treated.split('\n') 
#         results = [keyword for keyword in results if keyword != '']

#         for keyword in results:
#             if keyword.endswith('no'): 
#                 dup_lists.append('no')
#             elif keyword.endswith('yes'):
#                 dup_lists.append('yes')

#     print('======================= csv파일에 중복검사 결과를 입력하는 중입니다 ================================')

#     df = pd.read_csv(f'{des}\\{filename}\\재중복검사대상.csv')
#     df['is_dup'] = dup_lists
#     df = df.dropna(axis=0)
#     df.to_csv(f'{des}\\{filename}\\2차중복검사후.csv', encoding='utf8', sep=',', index=False)

#     print('====================== 중복검사 결과 입력 완료. 2차 중복검사 결과를 보려면 2차중복검사 후 csv파일을 확인해주세요. ====================')

# 중복되는 파일들 삭제
# def delete_files(filename):
#     print('================= 중복검사 결과가 yes인 파일을 삭제합니다. =================')
#     df = pd.read_csv(f'{des}\\{filename}\\2차중복검사후.csv')
#     dup = df.loc[df['is_dup']=='yes']
#     dup_parts = list(dup['crawled_part_num'])

#     for part in dup_parts:
#         dup_file = f'{des}\\{filename}\\PDF\\{part}.pdf'
#         if os.path.isfile(dup_file): os.remove(dup_file)
#     print('=============================== 삭제 완료! ===============================')

# pdf안의 파트넘버로 파일이름 변경
# def rename_files(filename):
#     delete_files(filename)
#     print('==================== pdf안의 파트넘버로 파일 이름을 변경합니다. ====================')
#     df = pd.read_csv(f'{des}\\{filename}\\2차중복검사후.csv')
#     df = df.loc[df['is_dup']=='no']

#     part_num = list(df['crawled_part_num'])
#     pdf_part_num = list(df['pdf_part_num'])

#     for i in range(0, df.shape[0]):
#         origin_path = f'{des}\\{filename}\\PDF\\' + part_num[i] + '.pdf'
#         new_path = f'{des}\\{filename}\\PDF\\' + pdf_part_num[i] + '.pdf' 
#         if os.path.isfile(origin_path) and not os.path.isfile(new_path): os.rename(origin_path, new_path)
#     print('=================================== 변경 완료! ===================================')

# 파일 이동
# def move_files(filename):
#     rename_files(filename)
#     print('==================== 작업폴더로 이름을 변경한 파일들을 옮깁니다. ====================')
#     df = pd.read_csv(f'{des}\\{filename}\\2차중복검사후.csv')
#     df = df.loc[df['is_dup']=='no']

#     pdf_part_num = list(df['pdf_part_num'])
#     for i in range(0, len(pdf_part_num)):
#         new_file = f'{des}\\{filename}\\PDF\\' + pdf_part_num[i] + '.pdf' 
#         target_dir = f'{des}\\{filename}\\Workable-Files\\' + pdf_part_num[i] + '.pdf' 
#         if not os.path.isfile(target_dir) and os.path.isfile(new_file):
#             shutil.move(new_file, target_dir)
#     print('=================================== 이동 완료! ===================================')