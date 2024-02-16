#import requests
import streamlit as st
import fitz
import util_v2
import re

st.set_page_config(page_title="enable rewordify", page_icon="🦄")

# Variables
enable_start = '[-enable start-]'
enable_end = '[-enable end-]'
icbc_start = '[-icbc start-]'
icbc_end = '[-icbc end-]'

def main():
    ##################################################
    # Logo
    ##################################################
    st.image('rewordify-logo.png')

    ##################################################
    # Model
    ##################################################
    st.markdown('#')
    model = st.selectbox(
        "**ChatGPT Model**",
        ("gpt-3.5-turbo", "gpt-4 (disabled)")
        )

    ##################################################
    # PDF File Uploader
    ##################################################
    st.markdown('#')   
    pdf_file = st.file_uploader("**Upload a PDF file**", type='pdf', accept_multiple_files=False, disabled=False, label_visibility="visible")

    ##################################################
    # Display Prompts
    ##################################################
    st.markdown('#')
    with st.expander("display prompts"):
        summary_prompt = st.text_area(
            '**Summary Prompt**',
            "Every time I enter text, act as a consultant neurologist. Use the text to summarize the patient's presenting complaint in a professional manner that would be suitable to communicate to other physicians. Write in paragraphs. ONLY SUMMARIZE THE GIVEN INFORMATION. Do not indicate or suggest that further evaluation or investigation is needed",
            height=120,
            disabled=False,
            label_visibility="visible"
        )
        past_medical_prompt = st.text_area(
            '**Past Medical/Family History Prompt**',
            "Reword the following in point form to use medical terminology",
            height=20,
            disabled=False,
            label_visibility="visible"
        )
        surgical_history_prompt = st.text_area(
            '**Surgical History Prompt**',
            "Reword this to read more fluidly. keep it medically professional",
            height=20,
            disabled=False,
            label_visibility="visible"
        )
        current_medication_prompt = st.text_area(
            '**Current Medication Prompt**',
            "Correct the spelling of the following medications and arrange them in point form. Do not state what the original spelling was. If an acronym was used, spell out the whole word",
            height=20,
            disabled=False,
            label_visibility="visible"
        )
        allergies_prompt = st.text_area(
            '**Allergies Prompt**',
            "Reword this to read more fluidly. keep it medically professional",
            height=20,
            disabled=False,
            label_visibility="visible"
        )
        social_history_prompt = st.text_area(
            '**Social History Prompt**',
            "Reword this to read more fluidly. keep it medically professional",
            height=20,
            disabled=False,
            label_visibility="visible"
        )
        functional_history_prompt = st.text_area(
            '**Functional History Prompt**',
            "Reword this to read more fluidly. keep it medically professional",
            height=20,
            disabled=False,
            label_visibility="visible"
        )

    ##################################################
    # Rewordify Action Button
    ##################################################
    st.markdown('#')
    if st.button("Rewordify"):
        try:
            if pdf_file is not None:
                with st.spinner('Running...'):
                    
                    ##################################################
                    # Extract PDF
                    ##################################################
                    pdf_text = util_v2.pdf_file_extract_text(pdf_file)
                    
                    ##################################################
                    # Get patient info
                    ##################################################
                    name_text, age_text, gender_text, pronouns_text = util_v2.extract_patient_info(pdf_text)
                    
                    # Get Occupation/Employer
                    occupation_text = util_v2.extract_occupation(pdf_text)
                    employer_text = util_v2.extract_employer(pdf_text)
                    
                    # Get Live with People text
                    live_with_people_text = util_v2.extract_live_with_people(pdf_text)
                    
                    ##################################################
                    # Get text between Markers
                    ##################################################
                    text_between_markers = util_v2.extract_text_between_markers(pdf_text, '[-enable start-]', '[-enable end-]')
                    
                    ##################################################
                    # Get Section Text
                    ##################################################
                    summary_section = util_v2.extract_summary_text(text_between_markers)
                    past_medical_section = util_v2.extract_section_text(text_between_markers, "past medical")
                    surgical_history_section = util_v2.extract_section_text(text_between_markers, "surgical history")
                    current_medications_section = util_v2.extract_section_text(text_between_markers, "current medications")
                    allergies_section = util_v2.extract_section_text(text_between_markers, "allergies")
                    familiy_history_section = util_v2.extract_section_text(text_between_markers, "family history")
                    social_history_section = util_v2.extract_section_text(text_between_markers, "social history")
                    functional_history_section = util_v2.extract_section_text(text_between_markers, "functional history")
                    
                    ##################################################
                    # Reword Sections
                    ##################################################
                    original_text = ''

                    # Summary
                    reworded_summary_section = util_v2.reword_section_text(st.secrets["api_key"], model, summary_prompt, 'Summary', summary_section)
                    original_text += 'Summary:\n' + summary_section
                    
                    # Past Medical/Family History
                    if util_v2.is_na_string(past_medical_section) == True and util_v2.is_na_string(familiy_history_section) == True:
                        reworded_past_medical_family_history_section = 'Past Medical/Family History:\nN/A'
                        original_text += '\n\nPast Medical/Family History:\nN/A'
                    else:
                        past_medical_family_history_combined = ''
                        if util_v2.is_na_string(past_medical_section) == False:
                            past_medical_family_history_combined = past_medical_section
                        if util_v2.is_na_string(familiy_history_section) == False:
                            past_medical_family_history_combined = past_medical_family_history_combined + '\n' + familiy_history_section
                        reworded_past_medical_family_history_section = util_v2.reword_section_text(st.secrets["api_key"], model, past_medical_prompt, 'Past Medical/Family History', past_medical_family_history_combined)
                        original_text += '\n\nPast Medical/Family History:\n' + past_medical_family_history_combined
                    
                    # Surgical History
                    reworded_surgical_history_section = util_v2.reword_section_text(st.secrets["api_key"], model, surgical_history_prompt, 'Surgical History', surgical_history_section)
                    original_text += '\n\nSurgical History:\n' + surgical_history_section
                    
                    # Current Medication
                    reworded_current_medication_section = util_v2.reword_section_text(st.secrets["api_key"], model, current_medication_prompt, 'Current Medication', current_medications_section)
                    original_text += '\n\nCurrent Medication:\n' + current_medications_section

                    # Allergies
                    reworded_allergies_section = util_v2.reword_section_text(st.secrets["api_key"], model, allergies_prompt, 'Allergies', allergies_section)
                    original_text += '\n\nAllergies:\n' + allergies_section

                    # Social History
                    original_text += '\n\nSocial History:\n' + social_history_section
                    # Remove PII
                    if len(occupation_text) > 0 and util_v2.contains_pii(occupation_text) == False:
                        social_history_section = social_history_section.replace(occupation_text, "<occupation>")
                    if len(employer_text) > 0 and util_v2.contains_pii(employer_text) == False:
                        social_history_section = social_history_section.replace(employer_text, "<employer>")
                    if len(live_with_people_text) > 0 and util_v2.contains_pii(live_with_people_text) == False:
                        social_history_section = social_history_section.replace(live_with_people_text, "<live_with_people>")
                    if len(name_text) > 0:
                        social_history_section = social_history_section.replace(name_text, "<name>")
                    # Reword
                    reworded_social_history_section = util_v2.reword_section_text(st.secrets["api_key"], model, social_history_prompt, 'Social History', social_history_section)
                    # Readd PII
                    if len(occupation_text) > 0 and util_v2.contains_pii(occupation_text) == False:
                        reworded_social_history_section = reworded_social_history_section.replace("<occupation>", occupation_text)
                    if len(employer_text) > 0 and util_v2.contains_pii(employer_text) == False:
                        reworded_social_history_section = reworded_social_history_section.replace("<employer>", employer_text)
                    if len(live_with_people_text) > 0 and util_v2.contains_pii(live_with_people_text) == False:
                        reworded_social_history_section = reworded_social_history_section.replace("<live_with_people>", live_with_people_text)
                    if len(name_text) > 0:
                        reworded_social_history_section = reworded_social_history_section.replace("<name>", name_text)
                    
                    # Functional History
                    reworded_functional_history_section = util_v2.reword_section_text(st.secrets["api_key"], model, functional_history_prompt, 'Functional History', functional_history_section)
                    original_text += '\n\nFunctional History:\n' + functional_history_section
                    
                    ##################################################
                    # Combine Sections
                    ##################################################
                    combine_sections = reworded_summary_section +'\n\n'+ reworded_past_medical_family_history_section +'\n\n'+ reworded_surgical_history_section +'\n\n'+ reworded_current_medication_section +'\n\n'+ reworded_allergies_section +'\n\n'+ reworded_social_history_section +'\n\n'+ reworded_functional_history_section

                # Done
                st.success('Done!')
                
                st.markdown('#')
                col1, col2 = st.columns(2)

                original_text_new = original_text.replace('\n', '  \n').replace('•\n', '+ ')
                combine_sections_new = combine_sections.replace('\n', '  \n').replace('•', '+')

                with col1:
                    st.write("**Extracted Text**")
                    with st.container(border=True):
                        st.markdown(original_text)
                        st.markdown(original_text_new)

                with col2:
                    st.write("**ChatGPT Response**")
                    with st.container(border=True):
                        st.markdown(combine_sections_new)
            
            elif pdf_file is None:
                st.write("Please choose a valid PDF file")
                
        except Exception as e:
            st.write("Error occurred 😓")
            st.exception(e)
    
if __name__ == '__main__': 
    main()
