"""

COPYRIGHT NOVA SCOTIA COMMUNITY COLLEGE - STRAIT AREA CAMPUS [ITGE]. ALL RIGHTS RESERVED.
PRODUCT MANAGER : DAVIS BOUDREAU
WRITTEN BY YUQING DING (SCOTT).
SPECIAL THANKS : CHATGPT (OPENAI).

"""

import subprocess
import nltk
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from pathlib import Path
import os
from WordCloud_Core import extract_text_from_pdf, merge_pdfs, extract_words, create_wordcloud, process_pdfs_in_folder
import datetime

subprocess.check_call(["pip3", "install", "PyPDF2"])
subprocess.check_call(["pip3", "install", "nltk"])
subprocess.check_call(["pip3", "install", "wordcloud"])
subprocess.check_call(["pip3", "install", "pandas"])

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('maxent_ne_chunker')
nltk.download('words')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():

    def secure_output_filename(filename, mode):
        if mode == 1:
            mode_str = "Verbs Only"
        elif mode == 2:
            mode_str = "Nouns and Verbs"
        return secure_filename(f"{filename.stem}_{mode_str}{filename.suffix}")

    uploads_folder = 'uploads'
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder)

    if request.method == 'POST':
        merge_choice = request.form.get('merge_pdfs')
        mode = int(request.form.get('mode'))
        if merge_choice:
            pdf_files = request.files.getlist('pdf_files')
            folder_path = app.config['UPLOAD_FOLDER']
            for file in pdf_files:
                filename = secure_filename(file.filename)
                file.save(os.path.join(folder_path, filename))
            output_merged_pdf = os.path.join(folder_path, "merged_pdfs.pdf")
            merge_pdfs(folder_path, output_merged_pdf)
            text = extract_text_from_pdf(output_merged_pdf)
            words = extract_words(text, mode)
            output_path = os.path.join(folder_path, f"Merged_WordCloud_{get_timestamp()}.png")
            create_wordcloud(words, output_path)

            # Remove the source PDF files after processing
            for file in pdf_files:
                file_path = os.path.join(folder_path, secure_filename(file.filename))
                if os.path.exists(file_path):
                    os.remove(file_path)
            if os.path.exists(output_merged_pdf):
                os.remove(output_merged_pdf)

            return send_file(output_path, mimetype='image/png', as_attachment=True, download_name=secure_output_filename(Path(output_path), mode))
        else:
            pdf_file = request.files['pdf_file']
            filename = secure_filename(pdf_file.filename)
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf_file.save(pdf_path)
            text = extract_text_from_pdf(pdf_path)
            words = extract_words(text, mode)
            original_filename = Path(filename).stem
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename}_WordCloud_{get_timestamp()}.png")
            create_wordcloud(words, output_path)

            # Remove the source PDF file after processing
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

            return send_file(output_path, mimetype='image/png', as_attachment=True, download_name=secure_output_filename(Path(output_path), mode))

if __name__ == '__main__':
    app.run(debug=False,port=5001)

