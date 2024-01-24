from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller, os, unicodedata, socket, time, pandas as pd
from urllib3.connection import HTTPConnection

HTTPConnection.default_socket_options = ( 
    HTTPConnection.default_socket_options + [
    (socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000), #1MB in byte
    (socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)
])

# 옵션
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-gpu')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option('excludeSwitches', ['enable-automation'])
# options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36')
des = os.getcwd()
if not os.path.isdir(f'{des}\\110'): chromedriver_autoinstaller.install(des)

# Renesas Technology Corp [RENESAS]^233
def Renesas(file_name):
    """
    Renesas 제조사의 파트넘버, pdf파일 링크, 컨텐츠 잠금여부를 크롤링합니다. \n
    크롤링된 요소들을 각 컬럼으로 구성하여 csv파일로 만듭니다.
    """
    driver = webdriver.Chrome(options=options)

    print('=============파트넘버 수집을 시작합니다=============')
    driver.get('https://www.renesas.com/us/en/support/document-search?keywords=datasheet&search_document_content=1')
    driver.find_element(By.XPATH, '//*[@id="edit-doc-file-types--wrapper"]/div/div[1]/div[1]/div[2]/div[1]/label/span').click()
    driver.find_element(By.XPATH, '//*[@id="edit-doc-file-types--wrapper"]/div/div[1]/div[1]/div[2]/div[2]/div[1]/label/span').click()
    driver.execute_script("window.scrollTo(0, 400)")

    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="edit-submit-documentation-tools"]').click()
    time.sleep(0.5)

    # make file that we save some files
    if not os.path.isdir(f'{des}\\{file_name}'):
        os.mkdir(f'{des}\\{file_name}')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전\\페이지별')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전\\병합본')
    
    start_page = 1
    temp_list = []
    # while loop will get part numbers when the pages go to until the end
    while True:
        # get pagination
        pager = driver.find_element(By.CLASS_NAME, 'pager') 
        cur_page = pager.find_element(By.CSS_SELECTOR, 'li.pager__item.pager__current-item.is-active')

        # get index for slicing
        spot = cur_page.text.find('\n')
        temp_df = pd.DataFrame(columns=['part_number', 'pdf_link', 'is_locked'])
        try:
            next_page = pager.find_element(By.CSS_SELECTOR, 'li.pager__item.pager__item--next>a')
        except:
            # if we can't find next page button, while loop will be breaked
            print('we have no more pages to crawling')
            break
        else:
            cur_page_num = int(cur_page.text[spot:])

            tbody = driver.find_element(By.TAG_NAME, 'tbody')
            tr_list = tbody.find_elements(By.TAG_NAME, 'tr')

            part_num_list = []
            pdf_link_list = []
            is_locked_list = []
            for tr in tr_list:
                is_locked = tr.find_element(By.TAG_NAME, 'span')
                lock_icon = is_locked.get_attribute('data-icon')

                a_tag = tr.find_element(By.TAG_NAME, 'a')
                part_num = unicodedata.normalize('NFKC', a_tag.text)
                part_num = part_num[:part_num.find(' ')].upper()

                # some exceptions about getting part number
                if ',' in part_num:
                    part_num = part_num[:part_num.find(',')]
                if part_num.startswith('DATASHEET'):
                    part_num = part_num[part_num.rfind(' ')+1:]
                if '-' in part_num and len(part_num[part_num.find('-')+1:])>7:
                    part_num = part_num[:part_num.find('-')]
                if 'DATASHEET' in part_num:
                    part_num = part_num.replace('DATASHEET', '')
                if '(' in part_num:
                    part_num = part_num[:part_num.find('(')]
                if '/' in part_num:
                    part_num = part_num[:part_num.find('/')]
                pdf_link = a_tag.get_attribute('href')

                # locked contents will be ruled out from the dataframe
                if lock_icon:
                    part_num_list.append(part_num)
                    pdf_link_list.append(pdf_link)
                    is_locked_list.append('yes')
                elif not lock_icon and '.' not in part_num and len(part_num)>4 and "_" not in part_num and '*' not in part_num:
                    part_num_list.append(part_num)
                    pdf_link_list.append(pdf_link)
                    is_locked_list.append('no')

            part_num_list = [keyword.replace('"', '').replace(',', '') for keyword in part_num_list]
            temp_df['part_number'] = part_num_list
            temp_df['pdf_link'] = pdf_link_list
            temp_df['is_locked'] = is_locked_list
            time.sleep(1)

            temp_df = temp_df.loc[temp_df['is_locked']=='no']
            temp_df.to_csv(f'{des}\\{file_name}\\중복검사_전\\페이지별\\{cur_page_num}페이지.csv', sep=',', encoding='utf8', index=False)
            temp_list.append(temp_df)

            if start_page <= cur_page_num: 
                print(f"{cur_page_num} page is done. move to next page..")
                next_page.send_keys(Keys.ENTER)
                start_page+=1

            if cur_page_num == 99:
                move_to_102 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[4]/main/div/div[2]/div/nav/ul/li[10]/a')
                move_to_102.send_keys(Keys.ENTER)

        finally:
            renesas_df = pd.concat(temp_list).reset_index(drop=True)
            renesas_df = renesas_df.drop_duplicates(keep='first').reset_index(drop=True)
            renesas_df.to_csv(f'{des}\\{file_name}\\중복검사_전\\병합본\\{file_name.lower()}.csv', encoding='utf8', index=False, sep=',')
    print('=============파트넘버 수집을 마쳤습니다=============')
    return

# NXP Semiconductors [NXP]^412
def Nxp(file_name):
    """
    Nxp 제조사의 파트넘버, pdf파일 링크를 크롤링합니다. \n
    이후 크롤링된 요소들을 각 컬럼으로 구성하여 csv파일로 만듭니다.
    """
    driver = webdriver.Chrome(options=options)
    
    driver.get(r'https://www.nxp.com/design/documentation:DOCUMENTATION#/collection=documents&start=0&max=12&language=en&query=type%3E%3EData%20Sheet')
    if not os.path.isdir(f'{des}\\{file_name}'):
        os.mkdir(f'{des}\\{file_name}')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전\\페이지별')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전\\병합본')
    print('===================================================================')
    print('파트넘버 수집을 시작합니다.')  

    temp_list = []
    while True:
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 4500)")
        time.sleep(1.5)
        pagenation = driver.find_element(By.XPATH, '//*[@id="retrieved-results"]/nav')
        pager = pagenation.find_element(By.XPATH, '//*[@id="retrieved-results"]/nav/ul')
        time.sleep(1.5)
        cur_page = pager.find_element(By.CSS_SELECTOR, '#retrieved-results > nav > ul > li.active > a')
        cur_page_num = int(cur_page.text)
        temp_df = pd.DataFrame(columns=['part_number', 'pdf_link'])
        time.sleep(1)
        try:
            # definition next page button for each situations
            if cur_page_num==408:
                next_page = pager.find_element(By.XPATH, '//*[@id="retrieved-results"]/nav/ul/li[7]/a')
            elif cur_page_num == 1 or cur_page_num == 2 or cur_page_num==407:
                next_page = pager.find_element(By.XPATH, '//*[@id="retrieved-results"]/nav/ul/li[8]/a')
            elif cur_page_num == 3 or cur_page_num == 406:
                next_page = pager.find_element(By.XPATH, '//*[@id="retrieved-results"]/nav/ul/li[9]/a')
            elif cur_page_num >= 4 and cur_page_num <= 405:
                next_page = pager.find_element(By.XPATH, '//*[@id="retrieved-results"]/nav/ul/li[10]/a')
            time.sleep(1)

            if cur_page_num==410:
                raise Exception('')
        except:
            print('we have no more pages to crawl')
            break
        else:
            ul = driver.find_element(By.CSS_SELECTOR, '#retrieved-results > ul')
            li_list = ul.find_elements(By.CLASS_NAME, 'retrieved-item ')
            part_num_list = []
            pdf_link_list = []
            for li in li_list:
                a_tag = li.find_element(By.TAG_NAME, 'a')
                pdf_link = a_tag.get_attribute('href')
                first = pdf_link.rfind('/')
                last = pdf_link.find('.pdf')
                part_num = pdf_link[first+1:last].upper()
                
                if part_num.startswith('R-'):
                    part_num = part_num[part_num.find('R-')+2:]
                if part_num.startswith('R_'):
                    part_num = part_num[part_num.find('R_')+2:]
                if part_num.startswith('DS-'):
                    part_num = part_num[part_num.find('DS-')+3:]
                if part_num.startswith('SDS-'):
                    part_num = part_num[part_num.find('SDS-')+4:]
                if part_num.startswith('SMX2_FAM_'):
                    part_num = part_num[part_num.find('FAM_')+4:part_num.rfind('_')-5]
                if part_num.endswith('_D'):
                    part_num = part_num.replace('_D', '')
                if part_num.endswith('_5'):
                    part_num = part_num.replace('_5', '-5R1')
                if part_num.endswith('_10'):
                    part_num = part_num.replace('_10', '-10R1')
                if 'Rev5' in part_num:
                    part_num = part_num.replace('Rev5', '')
                if 'ENGUM1' in part_num:
                    part_num = part_num[:part_num.find('ENGUM1')]
                if part_num.endswith('_60'):
                    part_num = part_num.replace('_60', '-60')
                if '_' in part_num:
                    part_num = part_num[:part_num.find('_')]
                if '-' in part_num:
                    part_num = part_num[:part_num.find('-')]
                if '(' in part_num:
                    part_num = part_num[:part_num.find('(')]
                
                if pdf_link.endswith('.pdf') and not part_num.startswith("950") and not part_num.startswith('X3G') and 'nxp' in pdf_link and len(part_num)>4:
                    part_num_list.append(part_num)
                    pdf_link_list.append(pdf_link)
                
            temp_df['part_number'] = part_num_list
            temp_df['pdf_link'] = pdf_link_list
            time.sleep(1)

            temp_df.to_csv(f'{des}\\{file_name}\\중복검사_전\\페이지별\\{cur_page_num}페이지.csv', sep=',', encoding='utf8', index=False)
            temp_list.append(temp_df)

            print(f"{cur_page_num} page is done. move to next page..")
            time.sleep(1)
            next_page.send_keys(Keys.ENTER)

        finally:
            renesas_df = pd.concat(temp_list).reset_index(drop=True)
            renesas_df = renesas_df.drop_duplicates(keep='first').reset_index(drop=True)
            renesas_df.to_csv(f'{des}\\{file_name}\\중복검사_전\\병합본\\{file_name.lower()}.csv', encoding='utf8', index=False, sep=',')

    print('파트넘버 수집을 완료했습니다. 자세한 내용은 csv파일을 확인하세요')  
    print('===================================================================')
    return

# Silicon Laboratories [SILABS]^316
def Silabs(file_name):
    """
    Silabs 제조사의 파트넘버, pdf파일 링크를 크롤링합니다. \n
    이후 크롤링된 요소들을 각 컬럼으로 구성하여 csv파일로 만듭니다.
    """
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.silabs.com/search#q=datasheets&t=All&sort=relevancy&f:@common_allowed_content_type=[Data%20Sheets]&f:@common_allowed_language=[English]')
    time.sleep(2)
    if not os.path.isdir(f'{des}\\{file_name}'):
        os.mkdir(f'{des}\\{file_name}')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전\\페이지별')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전\\병합본')
    print('===================================================================')
    print('파트넘버 수집을 시작합니다.')  

    driver.execute_script("window.scrollTo(0, 8000)")
    time.sleep(1)

    temp_list = []
    while True:
        time.sleep(1)
        cur_page_num = int(driver.find_element(By.CSS_SELECTOR, '#search > div.coveo-main-section > div.coveo-results-column > div.CoveoPager \
                                               > ul > li.coveo-pager-list-item.coveo-active.coveo-accessible-button').text)
        temp_df = pd.DataFrame(columns=['part_number', 'pdf_link'])
        time.sleep(1)
        try:
            if cur_page_num == 1 or cur_page_num==38:
                next_page = driver.find_element(By.XPATH, '//*[@id="search"]/div[7]/div[2]/div[8]/ul/li[6]')
            else:
                next_page = driver.find_element(By.XPATH, '//*[@id="search"]/div[7]/div[2]/div[8]/ul/li[7]')
        except:
            print('we have no more pages to crawl')
            break
        else:
            wrapper = driver.find_element(By.XPATH, '//*[@id="search"]/div[7]/div[2]/div[7]/div')
            div_list = wrapper.find_elements(By.CLASS_NAME, 'coveo-content-section')
            part_num_list = []
            pdf_link_list = []
            for div in div_list:
                a_tag = div.find_element(By.CSS_SELECTOR, '.CoveoSecureResultLink.CoveoResultLink')
                pdf_link = a_tag.get_attribute('href')
                if ' ' in a_tag.text: 
                    part_num = a_tag.text[:a_tag.text.find(' ')]
                else:
                    part_num = a_tag.text

                if '"' in part_num:
                    part_num = part_num.replace('"', '')
                elif ',' in part_num:
                    part_num = part_num.replace(',', '')
                elif '/' in part_num:
                    part_num = part_num[:part_num.find('/')]

                part_num_list.append(part_num)
                pdf_link_list.append(pdf_link)
                
            temp_df['part_number'] = part_num_list
            temp_df['pdf_link'] = pdf_link_list
            time.sleep(1)

            temp_df.to_csv(f'{des}\\{file_name}\\중복검사_전\\페이지별\\{cur_page_num}페이지.csv', sep=',', encoding='utf8', index=False)
            temp_list.append(temp_df)

            print(f"{cur_page_num} page is done. move to next page..")
            time.sleep(1)
            next_page.send_keys(Keys.ENTER)
            time.sleep(1)
        finally:
            renesas_df = pd.concat(temp_list).reset_index(drop=True)
            renesas_df = renesas_df.drop_duplicates(keep='first').reset_index(drop=True)
            renesas_df.to_csv(f'{des}\\{file_name}\\중복검사_전\\병합본\\{file_name.lower()}.csv', encoding='utf8', index=False, sep=',')

    print('파트넘버 수집을 완료했습니다. 자세한 내용은 csv파일을 확인하세요')  
    print('===================================================================')

    return

# Diodes Incorporated [DIODES]^41
def Diodes(file_name):
    """
    Diodes 제조사의 파트넘버, pdf파일 링크를 크롤링합니다. \n
    이후 크롤링된 요소들을 각 컬럼으로 구성하여 csv파일로 만듭니다.
    """
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.diodes.com/search?q=datasheet&t=keyword&f%5BFiles%5D=Files&start=0')
    time.sleep(2)
    if not os.path.isdir(f'{des}\\{file_name}'):
        os.mkdir(f'{des}\\{file_name}')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전\\페이지별')
        os.mkdir(f'{des}\\{file_name}\\중복검사_전\\병합본')
    print('===================================================================')
    print('파트넘버 수집을 시작합니다.')

    temp_list = []
    while True:
        pager = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div[1]/div[2]')
        cur_page = pager.find_element(By.TAG_NAME, 'strong').text
        cur_page_num = int(cur_page)

        driver.execute_script("window.scrollTo(0, 8000)")
        time.sleep(1)

        temp_df = pd.DataFrame(columns=['part_number', 'pdf_link'])
        time.sleep(1)
        try:
            next_page = driver.find_element(By.CSS_SELECTOR, 'body > div.Page__wrapper > div.Layout > div > div.SearchResults__results.typography > div:nth-child(1) > div.Pagination > a.Pagination__arrow.-next')
        except:
            print('we have no more pages to crawl')
            break
        else:
            tbody = driver.find_element(By.TAG_NAME, 'tbody')
            tr_list = tbody.find_elements(By.TAG_NAME, 'tr')
            part_num_list = []
            pdf_link_list = []
            for tr in tr_list:
                part_num = tr.find_element(By.CLASS_NAME, 'SearchResults__title').text
                a_tag = tr.find_element(By.CLASS_NAME, 'SearchResults__file')
                pdf_link = a_tag.get_attribute('href')

                if part_num.startswith('ds'):
                    continue
                if str() not in part_num:
                    continue
                if '.' in part_num:
                    part_num = part_num[:part_num.find('.')].upper()
                if ' ' in part_num:
                    part_num = part_num[:part_num.find(' ')].upper()
                if '_' in part_num:
                    part_num = part_num[:part_num.find('_')].upper()
                if '-' in part_num:
                    part_num = part_num[:part_num.find('-')].upper()
                if '(' in part_num:
                    part_num = part_num[:part_num.find('(')].upper()
                if '/' in part_num:
                    part_num = part_num[:part_num.find('/')].upper()
                if '"' in part_num:
                    part_num = part_num.replace('"', '').upper()
                if ',' in part_num:
                    part_num = part_num[:part_num.find(',')].replace(',', '').upper()

                if len(part_num)>4 and pdf_link.endswith('pdf') and not part_num.startswith('DS3') and 'products_inactive_data' not in pdf_link and 'userguide' not in pdf_link:
                    part_num_list.append(part_num)
                    pdf_link_list.append(pdf_link)
                
            temp_df['part_number'] = part_num_list
            temp_df['pdf_link'] = pdf_link_list
            time.sleep(1)

            temp_df.to_csv(f'{des}\\{file_name}\\중복검사_전\\페이지별\\{cur_page_num}페이지.csv', sep=',', encoding='utf8', index=False)
            temp_list.append(temp_df)

            print(f"{cur_page_num} page is done. move to next page..")
            time.sleep(1)
            next_page.send_keys(Keys.ENTER)
            time.sleep(1)
        finally:
            renesas_df = pd.concat(temp_list).reset_index(drop=True)
            renesas_df = renesas_df.drop_duplicates(keep='first').reset_index(drop=True)
            renesas_df.to_csv(f'{des}\\{file_name}\\중복검사_전\\병합본\\{file_name.lower()}.csv', encoding='utf8', index=False, sep=',')

    print('파트넘버 수집을 완료했습니다. 자세한 내용은 csv파일을 확인하세요')  
    print('===================================================================')
    return