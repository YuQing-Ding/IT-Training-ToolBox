"""

COPYRIGHT NOVA SCOTIA COMMUNITY COLLEGE - STRAIT AREA CAMPUS [ITGE]. ALL RIGHTS RESERVED.
PRODUCT MANAGER : DAVIS BOUDREAU
WRITTEN BY YUQING DING (SCOTT).
SPECIAL THANKS : CHATGPT (OPENAI).

"""

from flask import Flask, render_template, request, send_file
import os
from datetime import datetime
import pdfrw

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads/')

def create_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

create_folder(app.config['UPLOAD_FOLDER'])
create_folder(os.path.join(BASE_DIR, 'output/'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pdf_files = []
        for f in request.files.getlist('pdf_files'):
            if f.filename.endswith('.pdf'):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
                f.save(file_path)
                pdf_files.append(file_path)

        if pdf_files:
            merged_pdf = pdfrw.PdfWriter()
            for pdf_file in pdf_files:
                merged_pdf.addpages(pdfrw.PdfReader(pdf_file).pages)

            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            output_file = os.path.join(BASE_DIR, f'output/merged_output_{timestamp}.pdf')
            with open(output_file, 'wb') as f:
                merged_pdf.write(f)

            for pdf_file in pdf_files:
                os.remove(pdf_file)

            return send_file(output_file, as_attachment=True)

    return render_template('index.html') # Html file

if __name__ == '__main__':
    app.run(debug=False, port = 5003) # You can change port, at default it's 5003


#Hmmmmmm~
