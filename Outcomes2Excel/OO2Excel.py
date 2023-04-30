import os
import re
import glob
import pdfplumber
import pandas as pd

def process_pdf(file_name):
    text = ""
    with pdfplumber.open(file_name) as pdf:
        for page in pdf.pages:
            text += page.extract_text()

    file_basename = os.path.basename(file_name)
    first_four_letters = file_basename[:4]
    text = re.sub(r'(\d+\. .*?\.)\n\d+ ' + re.escape(first_four_letters) + r' .*?- \d+', r'\1', text)
    text = re.sub(r'^(\d+\. .*?)\n\d+ ', r'\1\n', text, flags=re.MULTILINE)

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
        cleaned_obj_list = re.findall(r'\d+\. .*?(?=\n\d+\. |\n\Z|$)', obj_list)
        formatted_obj_list = [f"{i + 1}:{obj[obj.index('.')+2:]}" for i, obj in enumerate(cleaned_obj_list)]
        cleaned_objectives.append(formatted_obj_list)

    data = {
        'Course#': [],
        'Outcome': [],
        'Objectives': [],
    }
    for i, (outcome, objective_list) in enumerate(zip(outcomes, cleaned_objectives)):
        for j, objective in enumerate(objective_list):
            data['Course#'].append(file_basename.split('.')[0])
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