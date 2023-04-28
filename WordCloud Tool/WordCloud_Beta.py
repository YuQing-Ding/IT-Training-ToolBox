"""

COPYRIGHT NOVA SCOTIA COMMUNITY COLLEGE - STRAIT AREA CAMPUS [ITGE]. ALL RIGHTS RESERVED.
PRODUCT MANAGER : DAVIS BOUDREAU
WRITTEN BY YUQING DING (SCOTT) & DAVIS BOUDREAU.
SPECIAL THANKS : CHATGPT (OPENAI).

"""
import subprocess
#Install Libs First :)
subprocess.check_call(["pip3", "install", "PyPDF2"])
subprocess.check_call(["pip3", "install", "nltk"])
subprocess.check_call(["pip3", "install", "wordcloud"])
subprocess.check_call(["pip3", "install", "pandas"])
import os
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.chunk import ne_chunk
from wordcloud import WordCloud
import pdfrw
import pandas as pd


nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('maxent_ne_chunker')
nltk.download('words')

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

def filter_named_entities(tagged_words):
    chunked = ne_chunk(tagged_words)
    filtered_words = []
    for item in chunked:
        if not hasattr(item, 'label'):
            word, tag = item
            filtered_words.append((word, tag))
    return filtered_words

def extract_verbs(text):
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words("english"))
    banned_words = pd.read_csv("banned_words.csv")["banned_words"].str.lower().tolist()  # Read "banned_words.csv"
    words = [word for word in words if word.lower() not in stop_words and word.lower() not in banned_words]
    tagged_words = nltk.pos_tag(words)
    filtered_words = filter_named_entities(tagged_words)
    # verbs = [word for word, tag in filtered_words if tag.startswith('VB')]
    verbs = [word for word, tag in filtered_words]
    return verbs

def create_wordcloud(verbs, output_path):
    wordcloud = WordCloud(width=3840, height=2160, background_color='white', min_font_size=15).generate(" ".join(verbs))
    wordcloud.to_file(output_path)

def merge_pdfs(folder_path, output_path):
    input_pdfs = []
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                input_pdfs.append(pdf_path) 
    output_pdf = pdfrw.PdfWriter()
    for pdf_path in input_pdfs:
        try:
            input_pdf = pdfrw.PdfReader(pdf_path)
            if len(input_pdf.pages) == 0:
                print(f"Skipping empty PDF file: {pdf_path}")
                continue
            output_pdf.addpages(input_pdf.pages)
        except pdfrw.errors.PdfParseError:
            print(f"Skipping invalid or empty PDF file: {pdf_path}")
    with open(output_path, 'wb') as file:
        output_pdf.write(file)

def process_pdfs_in_folder(folder_path, merge=False):
    if merge:
        merged_pdf_path = os.path.join(folder_path, "merged_pdfs.pdf")
        merge_pdfs(folder_path, merged_pdf_path)
        print(f"Merged PDFs saved as {merged_pdf_path}")
        text = extract_text_from_pdf(merged_pdf_path)
        verbs = extract_verbs(text)
        print(verbs)
        output_path = os.path.join(folder_path, "merged_pdfs_wordcloud.png")
        create_wordcloud(verbs, output_path)
        print(f"Word cloud for merged PDFs saved as {output_path}")
    else:
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.endswith(".pdf"):
                    pdf_path = os.path.join(root, filename)
                    print(f"Processing {pdf_path}...")
                    text = extract_text_from_pdf(pdf_path)
                    verbs = extract_verbs(text)
                    print(verbs)
                    output_path = os.path.join(root, f"{os.path.splitext(filename)[0]}_wordcloud.png")
                    create_wordcloud(verbs, output_path)
                    print(f"Word cloud saved as {output_path}")

if __name__ == "__main__":
    folder_path = os.path.join(os.path.dirname(__file__))
    user_choice = input("Do you want to merge all PDFs before generating the word cloud? Press 1 for yes, any other key for no: ")
    should_merge_pdfs = True if user_choice == '1' else False
    process_pdfs_in_folder(folder_path, should_merge_pdfs)
