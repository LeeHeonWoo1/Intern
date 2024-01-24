from io import StringIO
from PretreatParts import PretreatParts
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import re

def read_pdfs(pdf_file_path, part_num, filename):
    """
    pdf파일 안의 파트넘버를 찾아 리턴합니다.
    """
    pdf_part_num = ''
    output_string = StringIO()
    with open(pdf_file_path, 'rb') as f:
        parser = PDFParser(f)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        
        cnt = 1
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
            cnt += 1
            if cnt == 4:
                break
        
        text = str(output_string.getvalue())
        x = re.split('[ \n]', text)
        aList = [a for a in x if part_num == a]
        if len(aList) != 0:
            pdf_part_num = aList[0]
            pdf_part_num = ''.join(c for c in pdf_part_num if 0 < ord(c) < 127)

            pdf_part_num = PretreatParts(pdf_part_num)
    f.close()

    return pdf_part_num