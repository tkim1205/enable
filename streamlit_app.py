#import requests
import streamlit as st
import util

st.set_page_config(page_title="Rewordify", page_icon="🦄")

# Variables
prompt_template = """Every time I enter text, act as a consultant neurologist. Use the text to summarize the patient's presenting complaint in a professional manner that would be suitable to communicate to other physicians. Write in paragraphs. ONLY SUMMARIZE THE GIVEN INFORMATION. Do not indicate or suggest that further evaluation or investigation is needed.\n"""

enable_start = '[-enable start-]'
enable_end = '[-enable end-]'
icbc_start = '[-icbc start-]'
icbc_end = '[-icbc end-]'

def main():
    st.title("Rewordify")

    # PDF File Uploader
    pdf_file = st.file_uploader("Choose a PDF file", type='pdf', accept_multiple_files=False, disabled=False, label_visibility="visible")

    # Debug
    with st.expander("Debug mode"):
        debug_pdf_text = st.toggle("Show extracted PDF Text", value=False)
        debug_text_between_markers = st.toggle("Show text between markers", value=False)
        debug_personal_info = st.toggle("Show personal data extracted", value=False)
        debug_summary_text = st.toggle("Show summary text extracted", value=False)
        debug_past_medical_text = st.toggle("Show past medical text extracted", value=False)
        debug_chatgpt_prompt = st.toggle("Show ChatGPT prompt", value=False)

    if st.button("Rewordify"):
        try:
            if pdf_file is not None:
                with st.spinner('Running...'):
                    pdf_text = util.extract_text_from_pdf(pdf_file) 
                    text_between_markers = util.extract_text_between_markers(pdf_text, enable_start, enable_end, icbc_start, icbc_end)
                    name, age, gender = util.extract_information(pdf_text)
                    summary_text = util.get_summary_text(text_between_markers)
                    past_medical_text = util.get_past_medical_text(text_between_markers)
                    chatgpt_prompt = prompt_template + summary_text
                    
                    response = util.call_chatgpt(chatgpt_prompt, st.secrets["api_key"])

                # Done
                st.success('Done!')

                # Debug
                if debug_pdf_text:
                    st.write(pdf_text)
                if debug_text_between_markers:
                    st.write(text_between_markers)
                if debug_personal_info:
                    st.write("Name:", name, "\nAge:", age, "\nGender:", gender)
                if debug_summary_text:
                    st.write(summary_text)
                if debug_past_medical_text:
                    st.write(past_medical_text)
                if debug_chatgpt_prompt:
                    st.write(chatgpt_prompt)

                # Print Reponse
                st.code(response + '\n\n' + past_medical_text, language="python")
            
            elif pdf_file is None:
                st.write("Please choose a valid PDF file")
                
        except Exception as e:
            st.write("Error occurred 😓")
            st.exception(e)
    
if __name__ == '__main__': 
    main()
