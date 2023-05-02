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
import os
from WordCloud_Core import extract_text_from_pdf, merge_pdfs, extract_words, create_wordcloud, process_pdfs_in_folder
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():

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
            output_path = os.path.join(folder_path, "merged_wordcloud.png")
            create_wordcloud(words, output_path)
            return send_file(output_path, mimetype='image/png', as_attachment=True)
        else:
            pdf_file = request.files['pdf_file']
            filename = secure_filename(pdf_file.filename)
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf_file.save(pdf_path)
            text = extract_text_from_pdf(pdf_path)
            words = extract_words(text, mode)
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], "wordcloud.png")
            create_wordcloud(words, output_path)
            return send_file(output_path, mimetype='image/png', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
