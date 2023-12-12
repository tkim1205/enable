import re
import warnings
import PyPDF2
from PyPDF2 import PdfReader 

def extract_text_from_pdf(pdf): 
    pdf_reader = PdfReader(pdf) 
    return ''.join(page.extract_text() for page in pdf_reader.pages) 

def extract_text_between_markers(pdf_text, start_marker, end_marker, start_icbc_marker, end_icbc_marker):
    extracted_text = ""
    final_extracted_text = ""
    
    # Find start & end location index
    start_index = pdf_text.find(start_marker)
    end_index = pdf_text.find(end_marker)
    
    # Find ignore markers
    start_ignore_index = pdf_text.find(start_icbc_marker)
    end_ignore_index = pdf_text.find(end_icbc_marker)
        
    # Check if both start and end markers are present on the page
    if start_index != -1 and end_index != -1 and start_ignore_index != -1 and end_ignore_index != -1:
        # Extract the text between the markers, ignoring the text between the ignore markers
        extracted_text += pdf_text[start_index + len(start_marker):start_ignore_index].strip() + "\n"
        extracted_text += pdf_text[end_ignore_index + len(end_icbc_marker):end_index].strip() + "\n"
    elif start_index != -1 and end_index != -1:
        # There is no ignore text, so get all text between start & end markers
        extracted_text += pdf_text[start_index + len(start_marker):end_index].strip() + "\n"
    else:
        print('start and end markers are not present')
    
    # Remove Header & Footer
    header_index = extracted_text.find('PATIENT INFORMATION')
    footer_index = extracted_text.find('www.inputhealth.com')
    
    final_extracted_text += extracted_text[:header_index].strip() + "\n"
    final_extracted_text += extracted_text[footer_index + len('www.inputhealth.com'):].strip() + "\n"
    
    print(final_extracted_text)
            
    return final_extracted_text

def extract_information(text):
    # Define patterns for name, age, and gender
    name_pattern = re.compile(r'\[-name-\](.*?)\.')
    age_pattern = re.compile(r'\[-age-\](.*?)\.')
    gender_pattern = re.compile(r'\[-gender-\](.*?)\.')

    # Use findall to get all matches for each pattern
    names = re.findall(name_pattern, text)
    ages = re.findall(age_pattern, text)
    genders = re.findall(gender_pattern, text)

    # Return the extracted information
    return (
        names[0].strip() if names else None,
        ages[0].strip() if ages else None,
        genders[0].strip() if genders else None
    )

def get_summary_text(text):
    result = re.search(r'^(.*?)Past medical', text, re.DOTALL | re.MULTILINE)
    
    extracted_text = result.group(1)
    
    return extracted_text

def get_past_medical_text(text):
    result = re.search(r'(Past medical.*)', text, re.DOTALL)

    extracted_text = result.group(1)

    # Add line breaks before each header
    headers = ["Past medical", "Surgical history", "Current medications", "Allergies", "Family History", "Social History", "Functional History"]
    for header in headers:
        extracted_text = extracted_text.replace(header, '\n' + header)
    
    return extracted_text

def call_chatgpt(prompt, api_key, model):
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )

    response_message = response.choices[0].message.content
    return response_message