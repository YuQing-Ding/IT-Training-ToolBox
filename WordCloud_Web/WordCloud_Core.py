"""

COPYRIGHT NOVA SCOTIA COMMUNITY COLLEGE - STRAIT AREA CAMPUS [ITGE]. ALL RIGHTS RESERVED.
PRODUCT MANAGER : DAVIS BOUDREAU
WRITTEN BY YUQING DING (SCOTT).
SPECIAL THANKS : CHATGPT (OPENAI).

"""

import os
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.chunk import ne_chunk, RegexpParser
from nltk.corpus import words
from wordcloud import WordCloud
import pdfrw
import pandas as pd
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

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

def extract_words(text, mode):
    stop_words = set(stopwords.words("english"))
    banned_words = pd.read_csv("Banned_Words/banned_words.csv")["banned_words"].str.lower().tolist()
    valid_words = set(words.words())  # 获取英语词库
    grammar = r"""
        NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and noun
        VB: {<VB.*>}                # chunk verbs of any tense
    """
    chunk_parser = RegexpParser(grammar)

    sentences = sent_tokenize(text.lower())
    extracted_words = []

    for sent in sentences:
        tokens = word_tokenize(sent)
        tagged_words = nltk.pos_tag(tokens)
        chunked = chunk_parser.parse(tagged_words)
        for subtree in chunked.subtrees():
            if subtree.label() == 'NP' and mode == 2:
                for item in subtree.leaves():
                    word, tag = item
                    if word.lower() not in stop_words and word.lower() not in banned_words and word.lower() in valid_words:
                        extracted_words.append(word)
            elif subtree.label() == 'VB' and (mode == 1 or mode == 2):
                for item in subtree.leaves():
                    word, tag = item
                    if word.lower() not in stop_words and word.lower() not in banned_words and word.lower() in valid_words:
                        extracted_words.append(word)

    return list(set(extracted_words))

def create_wordcloud(words, output_path):
    wordcloud = WordCloud(width=3840, height=2160, background_color='white', min_font_size=15).generate(" ".join(words))
    wordcloud.to_file(output_path)

def process_pdfs_in_folder(folder_path, mode):
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                print(f"Processing {pdf_path}...")
                text = extract_text_from_pdf(pdf_path)
                words = extract_words(text, mode)
                print(words)

                # 提取课程编号
                course_code = filename.split("_")[0]
                # 根据用户选择生成输出文件名
                output_filename = f"{course_code} - {'Verbs' if mode == 1 else 'Noun & Verbs'}_WordCloud.png"
                output_path = os.path.join(root, output_filename)
                create_wordcloud(words, output_path)
                print(f"Word cloud saved as {output_path}")

