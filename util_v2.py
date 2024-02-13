#!/usr/bin/env python
# coding: utf-8

# ## Import

# In[34]:


import fitz # imports the pymupdf library
import re
import warnings


# ## Function: is_na_string(text)

# In[5]:


def is_na_string(text):
    """
    Check if a string variable represents 'no', 'na', 'n'
    after removing non-alphabetic characters.

    Parameters:
    text (str): The string variable to check.

    Returns:
    bool: True if the processed text matches 'no', 'na', 'n' (case-insensitive), False otherwise.
    """
    # Remove non-alphabetic characters using regular expression
    text_alpha = re.sub(r'[^a-zA-Z]', '', text)
    
    na_patterns = ["no", "na", "n", ""]
    return text_alpha.lower() in na_patterns


# ## Function: call_chatgpt(prompt)

# In[33]:


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


# ## Function: pdf_file_extract_text(pdf_file)

# In[7]:


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

    doc.close()
    return extracted_text


# ## Function: extract_patient_info(pdf_text)

# In[8]:


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
        dictionary: return key-value pairs for the extracted Name, Age, Gender, and Pronoun attributes
    """
    fields = {}
    patterns = {
        'name': r'\[-name-\]\s*(.*)',
        'age': r'\[-age-\]\s*(.*)',
        'gender': r'\[-gender-\]\s*(.*)',
        'pronouns': r'\[-pronouns-\]\s*(.*)'
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, pdf_text)
        if match:
            cleaned_value = re.sub(r'[^a-zA-Z0-9\s]', '', match.group(1).strip())
            fields[field] = cleaned_value

    return fields


# ## Function: extract_occupation(pdf_text)

# In[9]:


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


# ## Function: extract_employer(pdf_text)

# In[10]:


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


# ## Function: extract_live_with_people(pdf_text)

# In[11]:


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


# ## Function: extract_text_between_markers(pdf_text, start_marker, end_marker):

# In[12]:


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
    start_index = pdf_text.find(start_marker_escaped)
    if start_index == -1:
        match = re.search(r'\[-pronouns-\]', pdf_text)
        if match:
            next_line_start_index = match.end()  # End index of the match
            start_marker_escaped = pdf_text.find('\n', next_line_start_index) + 1

    # If end marker does not exist, default to 1. Name
    end_index = pdf_text.find(end_marker_escaped)
    if end_index == -1:
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


# ## Function: extract_summary_text(text_between_markers)

# In[13]:


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


# ## Function: extract_section_text(text_between_markers, section_header)

# In[14]:


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


# ## Function: reword_section_text(prompt, section_header, section_text)

# In[15]:


def reword_section_text(api_key, model, prompt, section_header, section_text):
    """
    Reword section text using ChatGPT

    Parameters:
    - prompt (str): The ChatGPT prompt.
    - section_header (str): Section Header Text
    - section_text (str): Section Text to be reworded

    Returns:
    - string: The reworded output from ChatPGT
    """
    if is_na_string(section_text) == True:
        return f"{section_header}:\nN/A"
    else:
        chatgpt_prompt = prompt + ": " + section_text
        chatgpt_response = call_chatgpt(chatgpt_prompt, api_key, model)
        return f"{section_header}:\n" + chatgpt_response

