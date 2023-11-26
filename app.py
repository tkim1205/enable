#import requests
import streamlit as st
import util

st.set_page_config(page_title="Rewordify", page_icon="🦄")

def main():
    st.title("Rewordify")

    api_key = st.text_input('OpenAI API Key')
    pdf_file = st.file_uploader("Choose a PDF file", type='pdf', accept_multiple_files=False, disabled=False, label_visibility="visible")

    if st.button("Rewordify"):
        try:
            if pdf_file is not None and api_key != '':
                with st.spinner('Running...'):
                    pdf_text = util.extract_text_from_pdf(pdf_file) 
                    text_between_markers = util.extract_text_between_markers(pdf_text, "/enable", "\\enable", "/ICBC", "\\ICBC")
                    summary_text = util.get_summary_text(text_between_markers)
                    past_medical_text = util.get_past_medical_text(text_between_markers)
                    chatgpt_prompt = 'Rephrase and format the following text into paragraphs so it sounds like as a consultant neurologist. Use the entered notes to summarize the patients problem:\n' + summary_text
                    
                    response = util.call_chatgpt(chatgpt_prompt, api_key)
                    
                st.success('Done!')
                st.code(response + '\n\n' + past_medical_text, language="python")

            elif api_key == '':
                st.write("Please enter an API Key")
            
            elif pdf_file is None:
                st.write("Please choose a valid PDF file")
                
        except Exception as e:
            st.write("Error occurred 😓")
            st.exception(e)
    
if __name__ == '__main__': 
    main()