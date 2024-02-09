from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_JUSTIFY
from urllib.request import urlopen
import datetime;

PAGE_WIDTH, PAGE_HEIGHT = A4
FULL_COLUMN_WIDTH = (PAGE_WIDTH - 1 * inch)
GARAMOND_REGULAR_FONT_PATH = './res/fonts/EBGaramond-Regular.ttf'
GARAMOND_REGULAR = 'Garamond_Regular'

GARAMOND_BOLD_FONT_PATH = './res/fonts/EBGaramond-Bold.ttf'
GARAMOND_BOLD = 'Garamond_Bold'

GARAMOND_SEMIBOLD_FONT_PATH = './res/fonts/EBGaramond-SemiBold.ttf'
GARAMOND_SEMIBOLD = 'Garamond_Semibold'

pdfmetrics.registerFont(ttfonts.TTFont(GARAMOND_REGULAR, GARAMOND_REGULAR_FONT_PATH))
pdfmetrics.registerFont(ttfonts.TTFont(GARAMOND_BOLD, GARAMOND_BOLD_FONT_PATH))
pdfmetrics.registerFont(ttfonts.TTFont(GARAMOND_SEMIBOLD, GARAMOND_SEMIBOLD_FONT_PATH))

JOB_DETAILS_PARAGRAPH_STYLE = ParagraphStyle('job_details_paragraph', leftIndent=12, fontName = GARAMOND_REGULAR, fontSize = 12, leading = 14, alignment = TA_JUSTIFY)
NAME_PARAGRAPH_STYLE = ParagraphStyle('name_paragraph', fontName = GARAMOND_SEMIBOLD, fontSize=16)
CONTACT_PARAGRAPH_STYLE = ParagraphStyle('contact_paragraph', fontName = GARAMOND_REGULAR, fontSize=12)
SECTION_PARAGRAPH_STYLE = ParagraphStyle('section_paragraph', fontName = GARAMOND_SEMIBOLD, fontSize=13, textTransform = 'uppercase')
COMPANY_HEADING_PARAGRAPH_STYLE = ParagraphStyle('company_heading_paragraph', fontName = GARAMOND_SEMIBOLD, fontSize=13)
COMPANY_TITLE_PARAGRAPH_STYLE = ParagraphStyle('company_title_paragraph', fontName = GARAMOND_REGULAR, fontSize=12)
COMPANY_DURATION_PARAGRAPH_STYLE = ParagraphStyle('company_duration_paragraph', fontName = GARAMOND_SEMIBOLD, fontSize=13, alignment = TA_RIGHT)
COMPANY_LOCATION_PARAGRAPH_STYLE = ParagraphStyle('company_location_paragraph', fontName = GARAMOND_REGULAR, fontSize=12, alignment = TA_RIGHT)

#pip install Pillow==10.0.0
#pip install reportlab==4.0.4

def appendSectionTableStyle(table_styles, running_row_index):
    table_styles.append(('TOPPADDING', (0, running_row_index), (1, running_row_index), 5))
    table_styles.append(('BOTTOMPADDING', (0, running_row_index), (1, running_row_index), 5))
    table_styles.append(('LINEBELOW', (0, running_row_index), (-1, running_row_index), 1, colors.black))

def generate_resume(file_path, json_data, author):
    doc = SimpleDocTemplate(file_path, pagesize=A4, showBoundary=0, leftMargin = 0.5 * inch, rightMargin= 0.5 * inch, topMargin = 0.2 * inch, bottomMargin = 0.1 * inch, title = f"Resume of {author}", author = author)
    # data for the table
    table_data = []
    table_styles = []
    running_row_index = 0

    # Append some basic styles to the table styles array only in debug mode
    # if (debug == 'true'):
    #     table_styles.append(('GRID', (0, 0), (-1, -1), 0, colors.black))
    
    table_styles.append(('ALIGN', (0, 0), (0, -1), 'LEFT'))
    table_styles.append(('ALIGN', (1, 0), (1, -1), 'RIGHT'))
    table_styles.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
    table_styles.append(('RIGHTPADDING', (0, 0), (-1, -1), 0))
    # Add name and basic contact
    
    table_styles.append(('BOTTOMPADDING', (0, running_row_index), (1, running_row_index), 6))
    table_data.append([
        Paragraph(json_data["name"], NAME_PARAGRAPH_STYLE)
    ])
    running_row_index += 1

    table_data.append([
        Paragraph(f"{"<a href='mailto:" + json_data["email"] + "'>" + json_data["email"] + "</a>"} | {json_data["mobileno"]} | {json_data["address"]}", CONTACT_PARAGRAPH_STYLE),
    ])
    table_styles.append(('BOTTOMPADDING', (0, running_row_index), (1, running_row_index), 1))
    running_row_index += 1

    # Add experience heading
    table_data.append(
        [Paragraph("Experience", SECTION_PARAGRAPH_STYLE)]
    )
    appendSectionTableStyle(table_styles, running_row_index)
    running_row_index += 1


    # Append experience
    for job_experience in json_data['experience']:
        table_data.append([
            Paragraph(job_experience['company'], COMPANY_HEADING_PARAGRAPH_STYLE),
            Paragraph(job_experience['duration'], COMPANY_DURATION_PARAGRAPH_STYLE),
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index), (1, running_row_index), 5))
        running_row_index += 1

        table_data.append([
            Paragraph(job_experience['title'], COMPANY_TITLE_PARAGRAPH_STYLE),
            Paragraph(job_experience['location'], COMPANY_LOCATION_PARAGRAPH_STYLE),
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index), (1, running_row_index), 1))
        running_row_index += 1

        for line in job_experience['description']:
            table_data.append([
                Paragraph(line, bulletText='•', style=JOB_DETAILS_PARAGRAPH_STYLE)
            ])
            table_styles.append(('TOPPADDING', (0, running_row_index), (1, running_row_index), 1))
            table_styles.append(('BOTTOMPADDING', (0, running_row_index), (1, running_row_index), 0))
            table_styles.append(('SPAN', (0, running_row_index), (1, running_row_index)))
            running_row_index += 1
    
    # Append education heading
    table_data.append(
        [Paragraph("Education", SECTION_PARAGRAPH_STYLE)]
    )
    appendSectionTableStyle(table_styles, running_row_index)
    running_row_index += 1
    
    # Append education
    for education in json_data['education']:
        table_data.append([
            Paragraph(education['university'], COMPANY_HEADING_PARAGRAPH_STYLE),
            Paragraph(education['year'], COMPANY_DURATION_PARAGRAPH_STYLE),
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index), (1, running_row_index), 5))
        running_row_index += 1

        table_data.append([
            Paragraph(education['degree'], COMPANY_TITLE_PARAGRAPH_STYLE),
            Paragraph(education['location'], COMPANY_LOCATION_PARAGRAPH_STYLE),
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index), (1, running_row_index), 1))
        running_row_index += 1

    # Append projects heading
    table_data.append(
        [Paragraph("Projects", SECTION_PARAGRAPH_STYLE)]
    )
    appendSectionTableStyle(table_styles, running_row_index)
    running_row_index += 1

    for project in json_data['projects']:
        table_data.append([
            Paragraph(f"<font face='Garamond_Semibold'>{project['title']}: </font>{project['description']} {project['link']}", bulletText='•', style=JOB_DETAILS_PARAGRAPH_STYLE),
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index), (1, running_row_index), 1))
        table_styles.append(('BOTTOMPADDING', (0, running_row_index), (1, running_row_index), 0))
        table_styles.append(('SPAN', (0, running_row_index), (1, running_row_index)))
        running_row_index += 1

    # Append skills heading
    table_data.append(
        [Paragraph("Skills", SECTION_PARAGRAPH_STYLE)]
    )
    appendSectionTableStyle(table_styles, running_row_index)
    running_row_index += 1

    # Append skills
    for skill in json_data['skills']:
        table_data.append([
            Paragraph(skill, bulletText='•', style=JOB_DETAILS_PARAGRAPH_STYLE)
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index), (1, running_row_index), 1))
        table_styles.append(('BOTTOMPADDING', (0, running_row_index), (1, running_row_index), 0))
        table_styles.append(('SPAN', (0, running_row_index), (1, running_row_index)))
        running_row_index += 1
    
    table_style = TableStyle(table_styles)

    # Create the table and apply the style
    table = Table(table_data, colWidths=[FULL_COLUMN_WIDTH * 0.7, FULL_COLUMN_WIDTH * 0.3], spaceBefore=0, spaceAfter=0)
    table.setStyle(table_style)

    # Add the table to the elements list
    elements = [table]

    # Build the PDF document
    doc.build(elements)

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<center><h1>Welcome to resume builder</h1></center>"

@app.route('/prepare_resume', methods=['POST'])
def prepare_resume():
    data = json.loads(request.data)
    json_url = data["json_url"]
    candidate_name = data["candidate_name"]
    
    response = urlopen(json_url)
    data_json = json.loads(response.read())

    ts = datetime.datetime.now().timestamp()
    OUTPUT_PDF_PATH = f"static/{candidate_name.lower().replace(' ', '_')}_resume_" + str(ts).replace('.', '_') + ".pdf"
    generate_resume("./" + OUTPUT_PDF_PATH, data_json, candidate_name)
    return jsonify({"resume_link":OUTPUT_PDF_PATH})

@app.route('/prepare_my_resume')
def prepare_my_resume():
    json_url = "http://localhost/igap-lms/resume_json/" + request.args.get("json_url") +  ".json"
    
    
    response = urlopen(json_url)
    data_json = json.loads(response.read())

    candidate_name = data_json["name"]

    ts = datetime.datetime.now().timestamp()
    OUTPUT_PDF_PATH = f"static/{candidate_name.lower().replace(' ', '_')}_resume_" + str(ts).replace('.', '_') + ".pdf"
    generate_resume("./" + OUTPUT_PDF_PATH, data_json, candidate_name)
    return OUTPUT_PDF_PATH