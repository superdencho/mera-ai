import os
from PyPDF2 import PdfReader


# Чтение PDF-файла и извлечение текста
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text


# Чтение всех PDF-файлов в папке ~/Documents
def extract_texts_from_folder(folder_path="~/Documents"):
    folder_path = os.path.expanduser(folder_path)
    all_texts = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            all_texts += extract_text_from_pdf(pdf_path) + "\n"
            print(f"Извлечен текст из файла: {filename}")
    return all_texts
