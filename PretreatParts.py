import re

def PretreatParts(text):
    """
    각 제조사의 pdf파일 안의 파트넘버를 식별할 때 해당 파트넘버에 \n
    불필요한 문자열은 제거하고 잘라야 하는 기준에 따라 파트넘버를 전처리합니다.
    """
    back = text[text.find('-')+1:]
    front = text[:text.find('-')]
    if '-' in text and len(back) >= len(front): text = front
    if ',' in text: text = text[:text.find(',')]
    if '/' in text: text = text[:text.find('/')]
    if 'www.' in text: text = text[:text.find('www.')]
    if 'utomotive' in text: text = text.replace('utomotive', '')
    if text.startswith('Inc.'): text = text.replace('Inc.', '')
    if text.endswith('Rev'): text = text.replace('Rev', '')
    new_text = re.sub(r"[^a-zA-Z0-9-]", "", text)

    return new_text