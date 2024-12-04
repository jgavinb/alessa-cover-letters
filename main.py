import streamlit as st
import groq
from datetime import datetime
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# read in resume
with open("resume.pdf", "rb") as file:
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)

    resume_text = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        resume_text += page.extract_text()


# Initialize Groq client
client = groq.Client(api_key="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")

def generate_cover_letter(job_description):
    """Generate cover letter using Groq API"""
    prompt = f"""
    ###########################################
    RULES: 
    The cover letter should be formal, highlight relevant skills, and show enthusiasm for the role.
    The cover letter should be tailored to increase the likelihood of getting an interview.
    Only include the body text of the cover letter in your response, no "Here is a cover letter for the job description...", "Here is a cover letter tailored to the job description:" or any other intro or prompt related text like this.
    Include a closing statement (ex. 'Sincerely,' 'Best,', etc.).
    Do not lie about experience, only include experience listed in the personal statement or resume.
    Please ensure the cover letter will fit on one page.
    ###########################################
    
    Write a professional cover letter based on the following job description and resume:
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    """
    
    response = client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": prompt
        }],
        model="llama3-70b-8192",
    )
    
    return response.choices[0].message.content

def save_cover_letter(cover_letter_text, company_name):
    """Save cover letter directly to PDF"""
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Current date
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Create output filename
    pdf_filename = f"output/cover_letter_{company_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Create styles
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        spaceBefore=12,
        spaceAfter=12,
        fontSize=12
    )
    
    # Build document content
    content = []
    
    # Add date
    content.append(Paragraph(current_date, normal_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Add cover letter text
    paragraphs = cover_letter_text.split('\n\n')
    for para in paragraphs:
        if para.strip():
            content.append(Paragraph(para, normal_style))
    
    # Build PDF
    doc.build(content)
    
    return pdf_filename

def main():
    st.title("Cover Letter Generator")
    # Form inputs
    company_name = st.text_input("Company Name")
    job_description = st.text_area("Job Description")
    
    if st.button("Generate Cover Letter"):
        if not all([company_name, job_description]):
            st.error("Please fill in all fields")
        else:
            with st.spinner("Generating cover letter..."):
                # Generate cover letter
                cover_letter_text = generate_cover_letter(job_description)
                
                # Save to template and convert to PDF
                pdf_filename = save_cover_letter(cover_letter_text, company_name)
                
                if pdf_filename:
                    st.success("Your cover letter is ready for download!")
                    
                    # Add download button for PDF
                    with open(f"output/{pdf_filename}", "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                        st.download_button(
                            label="📥 Download Cover Letter (PDF)",
                            data=pdf_bytes,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )

if __name__ == "__main__":
    main()