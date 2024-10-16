import streamlit as st
from PyPDF2 import PdfReader
from fpdf import FPDF
import os

# Define a list of font styles (100 options)
font_styles = [
    "Arial", "Arial Black", "Arial Narrow", "Arial Rounded MT Bold",
    "Comic Sans MS", "Courier", "Georgia", "Helvetica", "Impact",
    "Lucida Console", "Palatino", "Times", "Trebuchet MS",
    "Verdana", "Muli", "Open Sans", "Roboto", "Montserrat",  # Add other fonts as needed
]

# Function to register custom fonts
def register_fonts(pdf):
    # Register TTF font files
    font_dir = 'fonts'  # Directory where font files are located
    for font in font_styles:
        try:
            pdf.add_font(font, '', os.path.join(font_dir, f'{font}.ttf'), uni=True)
        except Exception as e:
            st.warning(f"Could not load font: {font}. Error: {e}")

def format_text(text):
    return text  # Return plain text without Markdown formatting

def find_line(text, query):
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if query.lower() in line.lower():
            return index + 1  # Return line number (1-indexed)
    return None

def text_to_pdf(text, background_color, font_style):
    pdf = FPDF()
    pdf.add_page()
    
    # Set background color
    try:
        r, g, b = int(background_color[1:3], 16), int(background_color[3:5], 16), int(background_color[5:7], 16)
    except ValueError:
        st.error("Invalid color format. Please use a hex code (e.g., #FF5733).")
        return None
    
    pdf.set_fill_color(r, g, b)  
    pdf.rect(0, 0, 210, 297, 'F')  # Fill the background
    
    # Register fonts before using them
    register_fonts(pdf)
    
    # Set font style based on user input
    try:
        pdf.set_font(font_style, size=12)
    except Exception as e:
        st.error(f"Error setting font style: {e}")
        return None

    # Split the text into lines and add them to the PDF
    for line in text.splitlines():
        pdf.cell(0, 10, line, ln=True)
    
    # Save the PDF to a BytesIO object
    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output

def main():
    st.title("PDF Summarizer and Text to PDF Converter")

    # Section for uploading PDF file
    st.subheader("Upload PDF for Summarization")
    uploaded_file = st.file_uploader("Drag and drop a PDF file here", type="pdf", label_visibility="collapsed")
    
    if uploaded_file is not None:
        # Read the PDF file
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""  # Handle None case for empty pages

        # Display the extracted text
        st.subheader("Extracted Text")
        st.text_area("Extracted Text", text, height=300, disabled=True)  # Read-only text area for extracted text

        # User input for Q&A
        user_input = st.text_input("Ask a question about the document:")
        
        if st.button("Submit Question"):
            if user_input:
                line_number = find_line(text, user_input)
                if line_number:
                    response = f"The answer is written on line **{line_number}**."
                else:
                    response = "Sorry, the document does not contain information regarding that."
                
                st.write(response)
            else:
                st.error("Please enter a question.")
    
    # Section for writing text to create PDF
    st.subheader("Create a PDF from Text")
    input_text = st.text_area("Enter text to create a PDF:", height=150)
    
    # Input for PDF customization
    background_color = st.color_picker("Choose Background Color:", "#FFFFFF")
    
    # Add spacing to ensure the dropdown opens downwards
    st.write("")  # Add a blank line to create some vertical space

    font_style = st.selectbox("Choose Font Style:", options=font_styles)  # 100 font styles available
    
    if st.button("Generate PDF"):
        if input_text:
            pdf_output = text_to_pdf(input_text, background_color, font_style)
            if pdf_output:
                st.success("PDF has been generated! Click the button below to download.")
                st.download_button(
                    label="Download Generated PDF",
                    data=pdf_output,
                    file_name="generated_text.pdf",
                    mime="application/pdf"
                )
        else:
            st.error("Please enter some text to create a PDF.")

# Set a custom background for Streamlit app
st.markdown(
    """
    <style>
    .stApp {
        color: white;  /* White text */
    }
    </style>
    """,
    unsafe_allow_html=True
)

if __name__ == "__main__":
    main()
