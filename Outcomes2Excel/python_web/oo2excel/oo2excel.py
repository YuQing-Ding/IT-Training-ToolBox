# app.py
from flask import Flask, render_template, request, send_file
import os
import tempfile
import shutil
from oo2excel_core import process_pdfs

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

    for file in input_files:
        file.save(os.path.join(temp_dir, secure_filename(file.filename)))

    your_script.process_pdfs(temp_dir, output_file_path)

    # 使用with语句确保文件被正确关闭
    with open(output_file_path, 'rb') as file:
        file_data = file.read()

    # 删除临时目录
    shutil.rmtree(temp_dir)

    # 使用BytesIO创建一个文件对象，以便在响应中发送
    output_file_object = BytesIO(file_data)

    response = send_file(output_file_object, attachment_filename='output.xlsx', as_attachment=True)
    return response


if __name__ == '__main__':
    app.run(debug=True)
