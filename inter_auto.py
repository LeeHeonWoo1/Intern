from tkinter import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from myFunctions import validation, pretreat, down_pdf
from CrawlByFac import Renesas, Nxp, Silabs, Diodes
from ParsePdf import parse_pdf

root = ttk.Window(themename='minty')
root.title('경쟁사 관리 자동화 프로그램')
root.geometry('530x650+480+240')
root.resizable(False, False)

# 파트넘버 크롤링
def get_part_num():
    """
    gui프로그램 내부의 파트넘버 수집 버튼을 담당하는 함수입니다. \n
    이 함수 내부에는 각 제조사 이름에 따라 실행되는 4개의 함수가 있습니다.
    """
    fac_name = fac_entry1.get()
    if not fac_name:
        messagebox.showinfo(title='제조사 명 미입력', message='제조사 명을 입력하지 않으셨습니다. 입력란을 확인해주세요.')
    
    file_name = fac_name[fac_name.find('[')+1:fac_name.find(']')]
    
    # we will excute functions for each manufactures
    if file_name == 'RENESAS':
        Renesas(file_name)
    if file_name == 'NXP':
        Nxp(file_name)
    if file_name == 'SILABS':
        Silabs(file_name)
    if file_name == 'DIODES':
        Diodes(file_name)

# 중복검사 후 csv파일 생성
def start_pretreat():
    """
    gui프로그램 내부의 중복검사 버튼을 담당하는 함수입니다. \n
    이 함수의 내부에는 중복검사 함수, 중복검사 결과 재구성 함수가 존재합니다.
    """
    fac_name = fac_entry1.get()
    if not fac_name:
        messagebox.showinfo(title='제조사 명 미입력', message='제조사 명을 입력하지 않으셨습니다. 입력란을 확인해주세요.')
    file_name = fac_name[fac_name.find('[')+1:fac_name.find(']')]
    if fac_name:
        result_text_list = validation(file_name, fac_name)
        pretreat(file_name, result_text_list)

# pdf다운로드
def start_down_pdf():
    """
    gui프로그램 내부의 pdf다운 버튼을 담당하는 함수입니다. \n
    이 함수 안에는 pdf다운로드 함수 하나가 존재합니다.
    """
    fac_name = fac_entry1.get()
    file_name = fac_name[fac_name.find('[')+1:fac_name.find(']')]
    if not fac_name:
        messagebox.showinfo(title='제조사 명 미입력', message='제조사 명을 입력하지 않으셨습니다. 입력란을 확인해주세요.')
    file_name = fac_name[fac_name.find('[')+1:fac_name.find(']')]
    if fac_name:
        down_pdf(file_name)

# pdf파일 분리
def start_sep_files():
    """
    gui프로그램 내부의 pdf파일 분리 버튼을 담당하는 함수입니다. \n
    이 함수 내부에는 pdf분할 함수 하나가 존재합니다.
    """
    fac_name = fac_entry2.get()
    if not fac_name:
        messagebox.showinfo(title='제조사 명 미입력', message='제조사 명을 입력하지 않으셨습니다. 입력란을 확인해주세요.')
    file_name = fac_name[fac_name.find('[')+1:fac_name.find(']')]
    if fac_name:
        parse_pdf(file_name)

# 타이틀
title_lbl = ttk.Label(root, text='경쟁사 관리 자동화 프로그램', font=('굴림체', 18))
title_lbl.grid(row=1, column=0, columnspan=2, pady=20)

# 1차 작업
# 입력 프레임
fac_lbl_frame = LabelFrame(root, text='1차작업', bg='white')
fac_lbl_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# 제조사 입력
fac_lbl1 = ttk.Label(fac_lbl_frame, text='제조사 입력', width=10, font=('맑은고딕', 10))
fac_lbl1.grid(row=2, column=0, padx=10, pady=5)

fac_entry1 = ttk.Entry(fac_lbl_frame, width=55)
fac_entry1.grid(row=2, column=1, sticky='w', padx=7, ipady=3)

# 각 기능별 버튼들(크롤링, 중복검사, pdf다운로드)
btn_frame1 = ttk.Frame(fac_lbl_frame)
btn_frame1.grid(row=3, column=0, columnspan=2, padx=10)

btn_crawl = ttk.Button(btn_frame1, text='파트넘버 수집', width=12, command = get_part_num)
btn_crawl.grid(row=3, column=0, pady=5, padx=6)

btn_valid = ttk.Button(btn_frame1, text='중복검사', width=10, command = start_pretreat)
btn_valid.grid(row=3, column=1, pady=5, padx=6)

btn_down = ttk.Button(btn_frame1, text='pdf다운로드', width=10, command = start_down_pdf)
btn_down.grid(row=3, column=2, pady=5, padx=6)

# # 2차작업
# 입력 프레임
fac_lbl_frame2 = LabelFrame(root, text='2차작업', bg='white')
fac_lbl_frame2.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# 제조사 입력
fac_lbl1 = ttk.Label(fac_lbl_frame2, text='제조사 입력', width=10, font=('맑은고딕', 10))
fac_lbl1.grid(row=4, column=0, padx=10, pady=5)

fac_entry2 = ttk.Entry(fac_lbl_frame2, width=55)
fac_entry2.grid(row=4, column=1, sticky='w', padx=7, ipady=3)

# 파일 분리 버튼
btn_frame2 = ttk.Frame(fac_lbl_frame2)
btn_frame2.grid(row=5, column=0, columnspan=2, padx=10)

btn_sep = ttk.Button(btn_frame2, text='pdf파일 분리', width=10, command = start_sep_files)
btn_sep.grid(row=5, column=0, pady=5, padx=10)

title_lbl3 = ttk.Label(root, text='자동으로 켜지는 크롬창은 종료하지 말아주세요.\n\n(현재 자동화된 제조사 : Renesas, Diodes, Nxp, Silabs)\n\n\
1. 제조사 입력란에 제조사 풀네임을 입력한다\n\n2. 파트넘버 수집 버튼을 누른다.\n\n\
3. 완료되면 중복검사 버튼을 누른다\n\n4. 완료되면 pdf를 다운받는다\
\n\n5. 2차 검사란에도 제조사 풀네임을 입력한다.\n\n6. pdf파일 분리 버튼을 누른다. \n\n7. pdf별 작업을 시작한다.', font=('맑은고딕', 12))
title_lbl3.grid(row=6, column=1, pady=20, sticky=W)

title_lbl2 = ttk.Label(root, text='주의사항 및 간단 설명', font=('맑은고딕', 18))
title_lbl2.grid(row=1, column=7, pady=10, sticky=W)

root.mainloop()