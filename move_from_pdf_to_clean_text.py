import fitz
import time
import re
from datetime import datetime

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def remove_text_before_team(text):
    pattern = re.compile(r'[^.]*Team:[^.]*\.')
    modified_text = pattern.sub('', text)
    return modified_text.strip()

def title_after(text, title):
    pattern = re.compile(rf'.*?{re.escape(title)}', re.DOTALL)
    match = pattern.search(text)
    if match:
        return text[match.end():]
    else:
        return text
    
    
    
def remove_after_date(text, selected_date_str):
    """Remove all text after the last date older than the selected date."""
    # Convert the selected date string to a datetime object
    selected_date = datetime.strptime(selected_date_str, '%m/%d/%y')

    date_pattern = re.compile(r'\((\d{2}/\d{2}/\d{2})\)')
    last_valid_index = None
    for match in date_pattern.finditer(text):
        current_date = datetime.strptime(match.group(1), '%m/%d/%y')
        print(f"Found date: {current_date} (comparing with {selected_date})")
        if current_date <= selected_date:
            print(f"Found an earlier date: {current_date}. Truncating text at index: {match.start()}")
            return text[:match.start()]
    return text



def clean_pdf_text(text, title, date, remove_old=True):
    # Remove any extra new lines and extra spaces
    cleaned_text = re.sub(r'\n+', ' ', text)
    cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)
    # Remove repeated spaces or tabs at the beginning of lines
    cleaned_text = re.sub(r'^\s+', '', cleaned_text, flags=re.MULTILINE)
    # Remove all newlines
    cleaned_text = cleaned_text.replace('\n', ' ')
    # Collapse multiple spaces into one
    cleaned_text = re.sub(r' +', ' ', cleaned_text)
    # #remove the Team:
    cleaned_text = title_after(cleaned_text, title)
    # Fix specific formatting issues
    cleaned_text = re.sub(r'This document is being provided for the exclusive use.*?Bloomberg® \d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'Bloomberg® \d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'Bloomberg.*?affiliates\.', '', cleaned_text, flags=re.DOTALL)
    # Remove sentences that contain @ symbol or the word Bloomberg
    cleaned_text = re.sub(r'[^.]*@[^.]*\.', '', cleaned_text)  
    #Remove older additions
    if remove_old == True:
        cleaned_text = remove_after_date(cleaned_text, date)
    # Remove sentences with fewer than five words
    sentences = re.split(r'(?<=[.!?]) +', cleaned_text)
    cleaned_text = ' '.join([sentence for sentence in sentences if len(sentence.split()) >= 5])
    cleaned_text = re.sub(r'T eam', 'Team', cleaned_text)
    cleaned_text = re.sub(r' T ', ' T', cleaned_text)
    cleaned_text = re.sub(r'\(Bloomberg Intelligence\) --', '', cleaned_text)
    return cleaned_text.strip()