from selenium import webdriver
from selenium.webdriver.common.by import By
import time, pandas as pd, requests
import os
from tqdm import tqdm

options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-gpu')
options.add_experimental_option('excludeSwitches', ['enable-logging'])

options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')

# 중복검사
def validation(file_name, fac_name):
    """
    수집한 파트 넘버들을 일련의 전처리 과정을 거쳐 회사 내부 중복검사 기능을 통해 \n
    회사에서 보유하고 있는 pdf인지 아닌지 중복검사를 실시합니다. 
    """
    print('===================================================================')
    print('master페이지에 로그인합니다.')
    des = os.getcwd()
    driver = webdriver.Chrome(options=options)

    driver.get("master page link")
    time.sleep(0.5)

    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(0.5)
    id = driver.find_element(By.NAME, 'id')
    pw = driver.find_element(By.NAME, 'pwd')
    id.send_keys('master id')
    time.sleep(0.5)
    pw.send_keys('master password')
    time.sleep(0.5)

    loggin_button = driver.find_element(By.XPATH, '/html/body/form/table/tbody/tr[3]/td/input[1]')
    loggin_button.click()

    print('===================================================================')
    print('로그인 완료')
    print('===================================================================')
    if not os.path.isdir(f'{des}\\{file_name}\\중복검사_후'):
        os.mkdir(f'{des}\\{file_name}\\중복검사_후')
    driver.find_element(By.XPATH, '/html/body/div[1]/center/table/tbody/tr[3]/td[1]/a').click()
    time.sleep(0.5)

    path = f'{des}\\{file_name}\\중복검사_전\\페이지별\\'
    result_text_list = []
    print('수집한 전체 page 중복체크 시작')

    pbar = tqdm(os.listdir(path))
    for file in pbar:
        df = pd.read_csv(f'{path}{file}', encoding='utf-8-sig')
        df = df.dropna(axis=0).reset_index(drop=True)
        text_list = list(df['part_number'])
        [text_list.remove(key) for key in text_list if key=='']
        val_string = ''
        for text in text_list:
            text = str(text)
            if '/' in text:
                text = text[:text.find('/')]
            text = ''.join(c for c in text if 0 < ord(c) < 127)
            if "'" in text:
                text = text.replace("'", '')
            val_string += f'{text}\n'
        
        val_string = val_string.replace(' ','')

        fact_name = driver.find_element(By.NAME, 'sFactory')
        fact_name.send_keys(fac_name)
        time.sleep(0.5)

        text_box = driver.find_element(By.NAME, 'S1')
        text_box.clear()
        time.sleep(0.5)
        text_box.send_keys(val_string)
        time.sleep(0.5)

        execute = driver.find_element(By.NAME, 'B1')
        execute.click()
        time.sleep(0.5)

        result_text = driver.find_element(By.XPATH, '/html/body/center').text
        result_text_list.append(result_text)
    pbar.close()
    print('중복체크 완료')
    print('===================================================================')
    return result_text_list

# 중복검사 결과 입력
def pretreat(file_name, result_text_list):
    """
    중복 검사 결과와 파트넘버, pdf링크를 컬럼으로 구성하여 csv파일로 재구성합니다. \n
    일부 제조사의 경우 컨텐츠 잠금여부까지 컬럼으로 구성합니다.
    """
    des = os.getcwd()

    print('문자열 데이터 전처리를 시작합니다.')
    print('===================================================================')
    path = f'{des}\\{file_name}\\중복검사_전\\페이지별\\'
    dup_lists = []

    print('불필요한 텍스트를 제거하고 공백을 지우는 중입니다.')
    for result_text in result_text_list: 
        first_spot = result_text.find(']') 
        last_spot = result_text.find('Yes(') 
        treated = result_text[first_spot+1:last_spot]
        results = treated.split('\n') 
        results = [keyword for keyword in results if keyword != '']

        is_dup_list = []
        for keyword in results:
            if keyword.endswith('no'): 
                is_dup_list.append('no')
            elif keyword.endswith('yes'):
                is_dup_list.append('yes')

        dup_lists.append(is_dup_list)
    print('문자열 전처리 완료')
    print('===================================================================')
    print('csv파일에 중복검사 결과를 입력하는 중입니다...')
    print('===================================================================')

    result_df_list = []
    for i, file in enumerate(os.listdir(path)): 
        if file.endswith('.csv'):
            df = pd.read_csv(f'{path}{file}')
            df['is_duplicated'] = dup_lists[i]
            result_df_list.append(df)
    
    df1 = pd.concat(result_df_list).reset_index(drop=True)
    df1 = df1.drop_duplicates(keep='first').dropna(axis=0).reset_index(drop=True)
    dup_df = df1.loc[df1['is_duplicated']=='yes']
    none_dup_df = df1.loc[df1['is_duplicated']=='no']
    dup_df.to_csv(f'{des}\\{file_name}\\중복검사_후\\{file_name.lower()}_dup.csv', encoding='utf8', index=False, sep=',')
    none_dup_df.to_csv(f'{des}\\{file_name}\\중복검사_후\\{file_name.lower()}_none_dup.csv', encoding='utf8', index=False, sep=',')
    print('중복검사 결과 입력 완료. 자세한 내용은 csv파일을 확인해주세요.')
    print('파일명이 dup으로 끝나는 파일은 DB에 등록된 파트넘버들, none_dup으로 끝나는 파일이 등록되지 않은 파트넘버들 입니다.')
    print('===================================================================')

# pdf 다운로드
def down_pdf(file_name):
    """
    중복 검사결과가 no인 제품들의 pdf파일을 다운로드 합니다.
    """
    des = os.getcwd()

    print(f'{file_name}제조사의 PDF 다운로드를 시작합니다.')
    print('===================================================================')
    path = f'{des}\\{file_name}\\중복검사_후\\{file_name.lower()}_none_dup.csv'
    if not os.path.isdir(f'{des}\\{file_name}\\PDF'):
        os.mkdir(f'{des}\\{file_name}\\PDF')
    pdf_path = f'{des}\\{file_name}\\PDF\\'

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    headers = {'User-Agent':user_agent}
    
    df = pd.read_csv(path)
    temp_df = pd.DataFrame(columns=['failed_part_num'])
    failed_part_list = []

    pbar = tqdm(range(0, df.shape[0]))
    for i in pbar:
        url = df.iloc[i, 1]
        part_num = str(df.iloc[i, 0])
        try:
            res = requests.get(url, headers = headers)
        except Exception as e:
            print('error has been occured. {}'.format(e))
            failed_part_list.append(part_num)
        else:
            if res.status_code == 200 or not os.path.isfile(f'{pdf_path}{part_num}.pdf'):
                with open(f'{pdf_path}{part_num}.pdf', 'wb') as f:
                        f.write(res.content)
            else:
                print(f"{res.status_code} error is occured. part number is {part_num}")
                failed_part_list.append(part_num)
    pbar.close()

    if len(failed_part_list) != 0:
        if not os.path.isdir(f'{des}\\{file_name}\\download_failed'): os.mkdir(f'{des}\\{file_name}\\download_failed')
        temp_df['failed_part_num'] = failed_part_list
        temp_df.to_csv(f'{des}\\{file_name}\\download_failed\\failed_to_download.csv', encoding='utf8', sep=',')

    for file in os.listdir(pdf_path):
        if not file.endswith('.pdf'):
            os.remove(f'{pdf_path}{file}')

    print(f'{file_name}제조사의 PDF 다운로드를 완료했습니다 !')
    print('총 개수:{0} 다운받은 개수:{1} 다운로드에 실패한 개수:{2}'.format(df.shape[0], len(os.listdir(f"{des}\\{file_name}\\PDF\\")), len(failed_part_list)))
    print('===================================================================')