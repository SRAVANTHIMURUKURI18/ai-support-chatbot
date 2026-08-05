import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_comprehensive_handbook():
    os.makedirs("backend", exist_ok=True)
    pdf_path = "backend/college_handbook.pdf"
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor='#ff4d4d', spaceAfter=12)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=13, textColor='#333333', spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=10, textColor='#444444', spaceAfter=6, leading=14)

    story.append(Paragraph("VISHNU INSTITUTE OF TECHNOLOGY (VITB) - OFFICIAL STUDENT HANDBOOK & GUIDELINES", title_style))
    story.append(Paragraph("Campus Location: Vishnupur, Kovvada Rd, Bhimavaram, Andhra Pradesh - 534202. Affiliated to JNTUK and Approved by AICTE.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Bus Timings & Transportation Facilities", heading_style))
    story.append(Paragraph("• Route 1 (Bhimavaram Town to Campus): Departs at 8:15 AM and 8:45 AM from local junctions. Evening return buses leave campus at 4:30 PM.", body_style))
    story.append(Paragraph("• Route 2 (Palakollu & Tanuku Express Routes): Morning pickups start at 7:45 AM. Return trip departs at 4:30 PM sharp from the central parking bay.", body_style))
    story.append(Paragraph("• Transport In-charge: Mr. Ramesh (Contact Ext: 402). Mandatory registration and bus pass issuance must be completed at the administrative transport cell.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. Hostels & Accommodation Details", heading_style))
    story.append(Paragraph("• Girls Hostel (Vedavathi Block): Accommodates over 1,200 students. Offers 24/7 Wi-Fi, round-the-clock security, medical care, reading rooms, and 4-time meal mess service.", body_style))
    story.append(Paragraph("• Boys Hostel (Vasishta Block): Located within campus premises. Includes indoor games, gym facilities, study areas, and daily room cleaning.", body_style))
    story.append(Paragraph("• Hostel Fee Structure: Non-AC rooms range from INR 79,500 to INR 82,500 per year. AC rooms are priced up to INR 1,25,000 per year depending on attached bathroom options.", body_style))
    story.append(Paragraph("• Curfew & Timings: Hostel main gates strictly close at 8:30 PM for all undergraduate students.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3. Fee Structure & Payment Guidelines", heading_style))
    story.append(Paragraph("• B.Tech Tuition Fees: Conformed as per AP-EAPCET convener quota norms (approx. INR 90,000 to INR 1,03,000 per annum depending on branch specialization).", body_style))
    story.append(Paragraph("• One-time Admission & Other Dues: INR 2,000 admission fee applicable in the 1st year only, with auxiliary university fees around INR 4,850 - 5,850 annually.", body_style))
    story.append(Paragraph("• Payment Deadlines: Fees are payable in annual or semester installments via the student portal. A late fine of INR 500 is levied after due dates.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("4. Academic Regulations & Code of Conduct", heading_style))
    story.append(Paragraph("• Attendance Policy: Minimum 75% attendance is mandatory in all theory and practical lab sessions to sit for semester-end exams.", body_style))
    story.append(Paragraph("• ID Card Mandate: Physical college ID cards must be worn visibly around the neck at all times inside campus buildings and labs.", body_style))
    story.append(Paragraph("• Campus Outing & Leave: Students must apply through the Smart Campus Outing system on the portal or app to leave premises during operational hours.", body_style))
    story.append(Paragraph("• Anti-Ragging Policy: Zero tolerance policy enforced strictly. Any complaints must be reported immediately to the Anti-Ragging Committee cell.", body_style))

    doc.build(story)
    print("Comprehensive handbook PDF created successfully at backend/college_handbook.pdf!")

if __name__ == "__main__":
    create_comprehensive_handbook()