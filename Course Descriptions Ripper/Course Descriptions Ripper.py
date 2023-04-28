"""

COPYRIGHT NOVA SCOTIA COMMUNITY COLLEGE - STRAIT AREA CAMPUS [ITGE]. ALL RIGHTS RESERVED.
PRODUCT MANAGER : DAVIS BOUDREAU
WRITTEN BY YUQING DING (SCOTT).
SPECIAL THANKS : CHATGPT (OPENAI).

"""

import os
import pdfplumber
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def extract_course_description(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()

        if "Course Description" not in text or "Credits" not in text:
            return None

        start_idx = text.index("Course Description")
        end_idx = text.index("Credits", start_idx)
        course_description = text[start_idx:end_idx].strip()

        return course_description

def process_pdfs(folder_path, output_file):
    course_descriptions = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                course_description = extract_course_description(pdf_path)
                
                if course_description is not None:
                    course_descriptions.append((file[:-4], course_description))

    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    styles['Heading1'].fontSize = 24
    styles['Heading1'].spaceAfter = 12
    # Change the body font size
    styles['BodyText'].fontSize = 14
    flowables = []

    custom_title = "Description of the courses to be taken this semester"
    title_style = styles['Heading1']
    title_style.spaceAfter = 12
    title_paragraph = Paragraph(custom_title, title_style)
    flowables.append(title_paragraph)

    for course_id_and_name, course_description in course_descriptions:
        # Remove the underscore from the file name and replace it with "-"
        course_id_and_name = course_id_and_name.replace("_", " -")
        
        course_id_and_name_paragraph = Paragraph("<b>{}</b>".format(course_id_and_name), styles["BodyText"])
        flowables.append(course_id_and_name_paragraph)

        lines = course_description.splitlines()
        modified_description = ""

        for line_number, line in enumerate(lines):
            if line_number == 0 and "Course Description" in line:
                line = line.replace("Course Description", "").strip()

            if line_number < len(lines) - 1:
                next_line = lines[line_number + 1]
                if not re.match(r'^\s*[A-Z]', next_line):  # If the next line does not start with an uppercase letter
                    line += " "

            modified_description += line

        description_paragraph = Paragraph(modified_description, styles["BodyText"])
        flowables.append(description_paragraph)
        flowables.append(Spacer(1, 12))

    doc.build(flowables)

folder_path = "CHANGE TO YOUR PATH"
output_file = "Combined_Course_Descriptions.pdf"
process_pdfs(folder_path, output_file)
