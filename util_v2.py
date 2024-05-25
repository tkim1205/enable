#!/usr/bin/env python
# coding: utf-8
import fitz # imports the pymupdf library
import re
import warnings


def pdf_file_extract_text(pdf_file):
    """
    Extract text from a PDF file, excluding the headers and footers
    
    Args:
        pdf_file (string): PDF file path
    
    Returns:
        string: Extracted text from PDF file, excluding the headers and footers
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")  # Open the PDF
    extracted_text = ""

    for page in doc:  # Iterate through each page
        # Get the page dimensions
        page_rect = page.rect
        top_margin = page_rect.height * 0.1  # Assuming header is within top 10%
        bottom_margin = page_rect.height * 0.95  # Assuming footer starts after bottom 90%

        # Extract text blocks along with their rectangles
        text_blocks = page.get_text("blocks")

        # Filter out text blocks that are in the header or footer regions
        main_content_blocks = [block for block in text_blocks if block[1] > top_margin and block[3] < bottom_margin]

        # Concatenate the text of these blocks
        page_text = "\n".join([block[4] for block in main_content_blocks])
        extracted_text += page_text + "\n"

    # Remove the specific string " SUMMARY" from the extracted text
    extracted_text = extracted_text.replace(" SUMMARY", "")

    # Define the regular expression pattern for " n a "
    pattern = r"\b(n\s+a)\b"

    # Perform case-insensitive replacement using re.sub()
    extracted_text = re.sub(pattern, "N/A", extracted_text, flags=re.IGNORECASE)

    doc.close()
    return extracted_text


def extract_patient_info(pdf_text):
    """
    Extract Name, Age, Gender, and Pronoun from text. They are values that exist after header fields, as shown below.
    
    Example.
    [-name-] First Last.
    [-age-] 100.
    [-gender-] male.
    [-pronouns-] he his himself him
    
    Args:
        pdf_text (string): PDF string text
    
    Returns:
        tuple: A tuple containing values for name, age, gender, and pronouns fields. If a field is not found, a blank space is returned for that field.
    """
    patterns = {
        'name': r'\[-name-\]\s*(.*)',
        'age': r'\[-age-\]\s*(.*)',
        'gender': r'\[-gender-\]\s*(.*)',
        'pronouns': r'\[-pronouns-\]\s*(.*)'
    }    
    
    # Initialize variables for each field
    name = age = gender = pronouns = ""

    # Iterate through each field pattern
    for field, pattern in patterns.items():
        match = re.search(pattern, pdf_text)
        if match:
            # Assign value to corresponding variable based on the field
            if field == "name":
                name = match.group(1)
            elif field == "age":
                age = match.group(1)
            elif field == "gender":
                gender = match.group(1)
            elif field == "pronouns":
                pronouns = match.group(1)
    
    # Return values for each field
    return name, age, gender, pronouns


def extract_occupation(pdf_text):
    """
    Extract occuption from 35.1

    Parameters:
    - pdf_text (str): PDF Text.

    Returns:
    - string: Occupation
    """
    index_text = "My occupation is"
    start_index = pdf_text.find(index_text)
    end_index = pdf_text.find("35.2")
    
    if start_index != -1:
        extract_text = pdf_text[start_index + len(index_text):end_index].strip()
        return extract_text
    else:
        return ''


def extract_employer(pdf_text):
    """
    Extract employer from 35.2

    Parameters:
    - pdf_text (str): PDF Text.

    Returns:
    - string: Employer
    """
    index_text = "I work at an organization called"
    start_index = pdf_text.find(index_text)
    end_index = pdf_text.find("35.3")
    
    if start_index != -1:
        extract_text = pdf_text[start_index + len(index_text):end_index].strip()
        return extract_text
    else:
        return ''


def extract_live_with_people(pdf_text):
    """
    Extract employer from 31.1

    Parameters:
    - pdf_text (str): PDF Text.

    Returns:
    - string: People i live with
    """
    index_text = "I live with the following people"
    start_index = pdf_text.find(index_text)
    end_index = pdf_text.find("32")
    
    if start_index != -1:
        extract_text = pdf_text[start_index + len(index_text):end_index].strip()
        return extract_text
    else:
        return ''


def extract_text_between_markers(pdf_text, start_marker, end_marker):
    """
    Extracts text between two specified markers in a given text.

    Parameters:
    - pdf_text (str): PDF text to search within.
    - start_marker (str): The starting marker.
    - end_marker (str): The ending marker.

    Returns:
    - string: The extracted text between the markers, or an empty string if markers are not found or no text between them.
    """
    # Escape markers for use in regular expression
    start_marker_escaped = re.escape(start_marker)
    end_marker_escaped = re.escape(end_marker)

    # If start marker does not exist, default to after Pronouns
    start_match = re.search(start_marker_escaped, pdf_text, re.DOTALL)
    if start_match is None:
        start_marker_escaped = r'\[-pronouns-\].*?(?=\n|$)'

    # If end marker does not exist, default to 1. Name
    end_match = re.search(end_marker_escaped, pdf_text, re.DOTALL)
    if end_match is None:
        end_marker_escaped = re.escape('1.\nName')
    
    # Regular expression to find text between markers
    pattern = rf'{start_marker_escaped}(.*?){end_marker_escaped}'

    # Using re.DOTALL to make '.' match newlines as well
    match = re.search(pattern, pdf_text, re.DOTALL)

    if match:
        # Extracted text between the markers
        return match.group(1).strip()
    else:
        return ""  # Return an empty string if no text is found between the markers


def check_required_headers_exist(text):
    """
    Checks if at least 5 out of 7 specified headers are present in the given text string.

    Parameters:
    text (str): The text string to be checked.

    Returns:
    bool: True if at least 5 headers are found, False otherwise.
    """
    headers = [
        "Past medical",
        "Surgical history",
        "Current medications",
        "Allergies",
        "Family History",
        "Social History",
        "Functional History"
    ]

    # Count the number of headers present in the text
    headers_found = sum(1 for header in headers if header.lower() in text.lower())

    # Return True if at least 5 headers are found, otherwise return False
    return headers_found >= 5


def extract_summary_text(text_between_markers):
    """
    Extract summary text, which is all text before the "Past Medical" section.

    Parameters:
    - text_between_markers (str): Text between markers

    Returns:
    - string: The extracted text before the "Past Medical" section.
    """
    result = re.search(r'^(.*?)Past medical', text_between_markers, re.DOTALL | re.MULTILINE)
    
    summary_text = result.group(1)
    
    return summary_text


def extract_section_text(text_between_markers, section_header):
    """
    The extracted PDF text may have the Section Headers below. For the section header passed, return the string under that specific section header only.
    - Past medical
    - Surgical history
    - Current medications
    - Allergies
    - Family History
    - Social History
    - Functional History

    Parameters:
    - text_between_markers (str): Text between markers.
    - section_header (str): The section header to search for.

    Returns:
    - string: The extracted text under the specified section header.
    """
    sections = [
        "Past medical", "Surgical history", "Current medications", 
        "Allergies", "Family History", "Social History", "Functional History"
    ]
    
    section_header_lower = section_header.lower()
    
    start_index = -1
    for i, section in enumerate(sections):
        if section_header_lower == section.lower():
            start_index = text_between_markers.find(section)
            break
    
    if start_index == -1:
        return None
    
    end_index = len(text_between_markers)
    for section in sections[i+1:]:
        section_index = text_between_markers.find(section, start_index + len(section_header))
        if section_index != -1 and section_index < end_index:
            end_index = section_index
    
    return text_between_markers[start_index + len(section_header):end_index].strip()


def load_default_text(section_header):
    """
    Load the default text from the corresponding file.

    Parameters:
    - section_header (str): The input string used to construct the filename.

    Returns:
    - str: The default text loaded from the file.
    """
    filename = f"prompts/default_{section_header}.txt"
    with open(filename, "r") as file:
        default_text = file.read()
    return default_text


def contains_pii(input_string):
    """
    Checks if the input string contains any of the specified keywords.

    Args:
    input_string (str): The input string to be checked.

    Returns:
    bool: True if the input string contains any of the specified keywords, False otherwise.
    """
    # Define the list of keywords
    keywords = ["common law", "self employ", "wife", "husband", "partner",
                "son", "daughter", "child", "baby", "girl", "boy"]
    
    # Convert input string to lowercase for case-insensitive comparison
    input_lower = input_string.lower()

    # Check if any of the keywords are present in the input string
    for keyword in keywords:
        if keyword in input_lower:
            return True
    
    return False


def is_na_string(text):
    """
    Check if a string variable represents 'none', 'no', 'na', 'n'
    after removing non-alphabetic characters.

    Parameters:
    text (str): The string variable to check.

    Returns:
    bool: True if the processed text matches 'no', 'na', 'n' (case-insensitive), False otherwise.
    """
    if text is None:
        return True
    else:
        # Remove non-alphabetic characters using regular expression
        text_alpha = re.sub(r'[^a-zA-Z]', '', text)
        na_patterns = ["none", "no", "na", "n", ""]
        return text_alpha.lower() in na_patterns


def call_chatgpt(prompt, api_key, model):
    """
    Call ChatGPT
    
    Args:
        prompt (string): prompt to pass to ChatGPT API
    
    Returns:
        string: Response from ChatGPT
    """
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    messages = [
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


def clean_section_text(api_key, model, section_text):
    """
    Clean section text using ChatGPT

    Parameters:
    - api_key
    - model
    - section_text (str): Section Text to be reworded

    Returns:
    - string: The section text cleansed
    """
    chatgpt_prompt = "My purpose is to look at the string of text below, and if it only references an external document like an attached page, then return N/A. Otherwise return the text without any modification:\n\n" + section_text
    chatgpt_response = call_chatgpt(chatgpt_prompt, api_key, model)
    return chatgpt_response


def reword_section_text(api_key, model, prompt, section_header, section_text):
    """
    Reword section text using ChatGPT

    Parameters:
    - api_key
    - model
    - prompt (str): The ChatGPT prompt.
    - section_header (str): Section Header Text
    - section_text (str): Section Text to be reworded

    Returns:
    - string: The reworded output from ChatPGT
    """
    if is_na_string(section_text) == True:
        return f"{section_header}:\nN/A"
    else:
        chatgpt_prompt = "INSTRUCTIONS:\n\n" + prompt + "\n\nGIVEN INFORMATION:\n\n" + section_text
        chatgpt_response = call_chatgpt(chatgpt_prompt, api_key, model)
        return f"{section_header}:\n" + chatgpt_response
