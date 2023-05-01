import os
import re
import glob
import pdfplumber
import pandas as pd

def extract_course_info(file_name):
    course_info = os.path.basename(file_name).split('.')[0]
    course_info = course_info.replace('_', ':')
    return course_info

def process_pdf(file_name):
    text = ""
    with pdfplumber.open(file_name) as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    course_info = extract_course_info(file_name)
    page_header_regex = re.compile(rf"{re.escape(course_info)} - \d+")
    page_footer_regex = re.compile(rf"\d+\s+{re.escape(course_info)}")
    text = page_header_regex.sub('', text)
    text = page_footer_regex.sub('', text)
    text = text.replace("Copyright statement", "")

    outcomes_and_objectives = re.search(
        r'Course Outcomes and Objectives([\s\S]*?)(Other Course Notes:|$)',
        text, re.IGNORECASE
    )

    if not outcomes_and_objectives:
        return None

    outcomes_and_objectives = outcomes_and_objectives.group(1)
    outcomes = re.findall(r'Outcome\s*?\n(\d+\. .*?)\nObjectives', outcomes_and_objectives, re.IGNORECASE)

    objectives = re.findall(r'Objectives([\s\S]*?)(?=\nIn keeping with|$)', outcomes_and_objectives, re.IGNORECASE)

    cleaned_objectives = []
    for obj_list in objectives:
        obj_list = re.sub(r'\n(\d+\. )', r'\n***\1', obj_list)  # Replace line breaks before objectives with a delimiter
        obj_list = obj_list.replace('\n', ' ').strip()  # Remove line breaks within objectives
        cleaned_obj_list = re.findall(r'\d+\. .*?(?=\*\*\*\d+\. |\Z)', obj_list)  # Split objectives using the delimiter
        formatted_obj_list = ["{}:{}".format(i + 1, obj[obj.index('.')+2:]) for i, obj in enumerate(cleaned_obj_list)]
        cleaned_objectives.append(formatted_obj_list)

    data = {
        'Course#': [],
        'Outcome': [],
        'Objectives': [],
    }
    for i, (outcome, objective_list) in enumerate(zip(outcomes, cleaned_objectives)):
        for j, objective in enumerate(objective_list):
            data['Course#'].append(course_info)
            data['Outcome'].append(outcome)
            data['Objectives'].append(objective)

    return pd.DataFrame(data)


# Search all PDF files in a subdirectory
pdf_files = []
for root, dirs, files in os.walk('.'):
    pdf_files += glob.glob(os.path.join(root, '*.pdf'))

# Process each PDF file and merge the results into a DataFrame
result_df = pd.DataFrame(columns=['Course#', 'Outcome', 'Objectives'])
for pdf_file in pdf_files:
    df = process_pdf(pdf_file)
    if df is not None:
        result_df = pd.concat([result_df, df], ignore_index=True)

# Output Xlsx (AKA Excel)
result_df.to_excel('output.xlsx', index=False)
