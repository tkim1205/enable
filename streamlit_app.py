#import requests
import streamlit as st
import util

st.set_page_config(page_title="enable rewordify", page_icon="🦄")

# Variables
enable_start = '[-enable start-]'
enable_end = '[-enable end-]'
icbc_start = '[-icbc start-]'
icbc_end = '[-icbc end-]'

def main():

    st.image('rewordify-logo.jpg')
    st.markdown('#')

    # Prompt
    prompt_template = st.text_area(
        'ChatGPT Prompt',
        "Every time I enter text, act as a consultant neurologist."
        "Use the text to summarize the patient's presenting complaint in a professional manner that would be suitable to communicate to other physicians."
        "Write in paragraphs. ONLY SUMMARIZE THE GIVEN INFORMATION. Do not indicate or suggest that further evaluation or investigation is needed."
    )

    # PDF File Uploader
    pdf_file = st.file_uploader("**Upload a PDF file**", type='pdf', accept_multiple_files=False, disabled=False, label_visibility="visible")

    # Debug
    with st.expander("display options"):
        col1, col2 = st.columns(2)

        with col1:
            show_pdf_text = st.toggle("Raw extracted PDF text", value=False, disabled=False, label_visibility="visible")
            show_text_between_markers = st.toggle("Text between markers", value=False, disabled=False, label_visibility="visible")
            show_personal_info = st.toggle("Personal data", value=False, disabled=False, label_visibility="visible")
            show_summary_text = st.toggle("Summary text", value=False, disabled=False, label_visibility="visible")

        with col2:
            show_past_medical_text = st.toggle("Past medical text", value=False, disabled=False, label_visibility="visible")
            show_chatgpt_prompt = st.toggle("ChatGPT prompt", value=False, disabled=False, label_visibility="visible")
            show_chatgpt_response = st.toggle("ChatGPT response", value=True, disabled=False, label_visibility="visible")

    if st.button("Rewordify"):
        try:
            if pdf_file is not None:
                with st.spinner('Running...'):
                    pdf_text = util.extract_text_from_pdf(pdf_file) 
                    text_between_markers = util.extract_text_between_markers(pdf_text, enable_start, enable_end, icbc_start, icbc_end)
                    name, age, gender = util.extract_information(pdf_text)
                    summary_text = util.get_summary_text(text_between_markers)
                    past_medical_text = util.get_past_medical_text(text_between_markers)
                    chatgpt_prompt = prompt_template + "\n\nText:\n\n" + summary_text

                    if show_chatgpt_response:
                        response = util.call_chatgpt(chatgpt_prompt, st.secrets["api_key"])

                # Done
                st.success('Done!')

                # Debug
                if show_pdf_text:
                    st.write(pdf_text)
                if show_text_between_markers:
                    st.write(text_between_markers)
                if show_personal_info:
                    st.write("Name:", name)
                    st.write("Age:", age)
                    st.write("Gender:", gender)
                if show_summary_text:
                    st.write(summary_text)
                if show_past_medical_text:
                    st.write(past_medical_text)
                if show_chatgpt_prompt:
                    st.write(chatgpt_prompt)

                # Print Reponse
                if show_chatgpt_response:
                    st.code(response + '\n\n' + past_medical_text, language="python")
            
            elif pdf_file is None:
                st.write("Please choose a valid PDF file")
                
        except Exception as e:
            st.write("Error occurred 😓")
            st.exception(e)
    
if __name__ == '__main__': 
    main()
