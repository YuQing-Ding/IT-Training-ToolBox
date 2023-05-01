"""

COPYRIGHT NOVA SCOTIA COMMUNITY COLLEGE - STRAIT AREA CAMPUS [ITGE]. ALL RIGHTS RESERVED.
PRODUCT MANAGER : DAVIS BOUDREAU
WRITTEN BY YUQING DING (SCOTT).
SPECIAL THANKS : CHATGPT (OPENAI).

"""

from flask import Flask, render_template, request, send_file
import os
import tempfile
import shutil
from werkzeug.utils import secure_filename
from oo2excel_core import process_pdfs
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'input_files' not in request.files:
        return 'No file part', 400

    input_files = request.files.getlist('input_files')

    temp_dir = tempfile.mkdtemp()
    output_file_path = os.path.join(temp_dir, 'output.xlsx')

    output_filename = ""

    for file in input_files:
        file.save(os.path.join(temp_dir, secure_filename(file.filename)))
        output_filename = f"{os.path.splitext(secure_filename(file.filename))[0]}.xlsx"

    process_pdfs(temp_dir, output_file_path)

    with open(output_file_path, 'rb') as file:
        file_data = file.read()

    shutil.rmtree(temp_dir)

    output_file_object = BytesIO(file_data)
    response = send_file(output_file_object, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=output_filename)

    return response

if __name__ == '__main__':
    app.run(debug=False,port=8964)
