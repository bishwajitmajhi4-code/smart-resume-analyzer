import PyPDF2

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in range(len(reader.pages)):
                # PDF ke har page ka text nikal kar add kar rahe hain
                text += reader.pages[page].extract_text() + " "
    except Exception as e:
        print(f"Error reading PDF: {e}")
        
    # Saare text ko lowercase (chote aksharon) mein convert kar rahe hain taaki match karna aasan ho
    return text.lower()