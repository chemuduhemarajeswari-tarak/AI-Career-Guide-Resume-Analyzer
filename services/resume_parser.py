import os
from typing import Optional

from docx import Document
from PyPDF2 import PdfReader


def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = []
    for page in reader.pages:
        page_text = page.extract_text() or ''
        text.append(page_text)
    return '\n'.join(text)


def extract_text_from_docx(file_path):
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs]
    return '\n'.join(paragraphs)


def extract_resume_text(file_storage):
    filename = file_storage.filename.lower()
    if filename.endswith('.txt'):
        temp_path = file_storage.save('/tmp/tmp_resume.txt')
        return extract_text_from_txt(file_storage.stream.name)
    if filename.endswith('.pdf'):
        temp_path = file_storage.save('/tmp/tmp_resume.pdf')
        return extract_text_from_pdf(file_storage.stream.name)
    if filename.endswith('.docx'):
        temp_path = file_storage.save('/tmp/tmp_resume.docx')
        return extract_text_from_docx(file_storage.stream.name)
    raise ValueError('Unsupported resume format. Only PDF, DOCX, and TXT are allowed.')


def extract_resume_text_from_upload(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        return extract_text_from_txt(file_path)
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    if ext == '.docx':
        return extract_text_from_docx(file_path)
    raise ValueError('Unsupported resume format. Only PDF, DOCX, and TXT are allowed.')
