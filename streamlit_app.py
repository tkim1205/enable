import streamlit as st
import fitz
import util_v2
import re

st.set_page_config(page_title="enable rewordify", page_icon="🦄", layout="wide")

# Variables
enable_start = '[-enable start-]'
enable_end = '[-enable end-]'
icbc_start = '[-icbc start-]'
icbc_end = '[-icbc end-]'

def main():
    # [Image: Logo]
    st.image('rewordify-logo.png')
    st.markdown('#')

    # [Select Box: Model]
    model = st.selectbox(
        "**ChatGPT Model**",
        ("gpt-3.5-turbo", "gpt-4o")
        )
    st.markdown('#')   

    # [PDF File Uploader]
    pdf_file = st.file_uploader("**Upload a PDF file**", type='pdf', accept_multiple_files=False, disabled=False, label_visibility="visible")
    st.markdown('#')

    # [Load Default ChatGPT Prompts]
    default_questionaire_prompt = util_v2.load_default_text("questionaire_prompt")
    default_icbc_prompt = util_v2.load_default_text("icbc_prompt")
    default_summary_prompt = util_v2.load_default_text("summary_prompt")
    default_past_medical_prompt = util_v2.load_default_text("past_medical_prompt")
    default_surgical_history_prompt = util_v2.load_default_text("surgical_history_prompt")
    default_current_medication_prompt = util_v2.load_default_text("current_medication_prompt")
    default_allergies_prompt = util_v2.load_default_text("allergies_prompt")
    default_family_history_prompt = util_v2.load_default_text("family_history_prompt")
    default_social_history_prompt = util_v2.load_default_text("social_history_prompt")
    default_functional_history_prompt = util_v2.load_default_text("functional_history_prompt")
    
    # [Expander for optional raw notes]
    with st.expander("display optional raw notes"):
        raw_questionaire_txt = st.text_area(
            '**Questionaire: History of Presenting Illness (optional)**',
            'N/A',
            height=120,
            disabled=False,
            label_visibility="visible"
        )

        raw_icbc_txt = st.text_area(
            '**ICBC/WBC (optional)**',
            'N/A',
            height=120,
            disabled=False,
            label_visibility="visible"
        )

    # [Expander to modify default ChatGPT Prompts]
    with st.expander("display prompts"):
        questionaire_prompt = st.text_area(
            '**Questionaire Prompt**',
            default_questionaire_prompt,
            height=120,
            disabled=False,
            label_visibility="visible"
        )

        icbc_prompt = st.text_area(
            '**ICBC/WBC Prompt**',
            default_icbc_prompt,
            height=120,
            disabled=False,
            label_visibility="visible"
        )

        summary_prompt = st.text_area(
            '**Summary Prompt**',
            default_summary_prompt,
            height=120,
            disabled=False,
            label_visibility="visible"
        )

        past_medical_prompt = st.text_area(
            '**Past Medical Prompt**',
            default_past_medical_prompt,
            height=20,
            disabled=False,
            label_visibility="visible"
        )

        surgical_history_prompt = st.text_area(
            '**Surgical History Prompt**',
            default_surgical_history_prompt,
            height=20,
            disabled=False,
            label_visibility="visible"
        )

        current_medication_prompt = st.text_area(
            '**Current Medication Prompt**',
            default_current_medication_prompt,
            height=20,
            disabled=False,
            label_visibility="visible"
        )

        allergies_prompt = st.text_area(
            '**Allergies Prompt**',
            default_allergies_prompt,
            height=20,
            disabled=False,
            label_visibility="visible"
        )

        family_history_prompt = st.text_area(
            '**Family History Prompt**',
            default_family_history_prompt,
            height=20,
            disabled=False,
            label_visibility="visible"
        )

        social_history_prompt = st.text_area(
            '**Social History Prompt**',
            default_social_history_prompt,
            height=20,
            disabled=False,
            label_visibility="visible"
        )

        functional_history_prompt = st.text_area(
            '**Functional History Prompt**',
            default_functional_history_prompt,
            height=20,
            disabled=False,
            label_visibility="visible"
        )
    st.markdown('#')

    # [Rewordify Action Button]
    if st.button("Rewordify"):
        try:
            if pdf_file is not None:
                with st.spinner('Running...'):
                    
                    # [Extract PDF]
                    pdf_txt = util_v2.pdf_file_extract_text(pdf_file)
                    
                    # [Get patient info]
                    name_txt, age_txt, gender_txt, pronouns_txt = util_v2.extract_patient_info(pdf_txt)
                    
                    # [Get Occupation/Employer]
                    occupation_txt = util_v2.extract_occupation(pdf_txt)
                    employer_txt = util_v2.extract_employer(pdf_txt)
                    
                    # [Get Live with People text]
                    live_with_people_txt = util_v2.extract_live_with_people(pdf_txt)
                    
                    # [Get text between Markers]
                    txt_between_markers = util_v2.extract_text_between_markers(pdf_txt, '[-enable start-]', '[-enable end-]')
                    
                    # [Raise exception if no text extracted]


                    # [Get Section Text]
                    summary_txt = util_v2.extract_summary_text(txt_between_markers)
                    past_medical_txt = util_v2.extract_section_text(txt_between_markers, "past medical")
                    surgical_history_txt = util_v2.extract_section_text(txt_between_markers, "surgical history")
                    current_meds_txt = util_v2.extract_section_text(txt_between_markers, "current medications")
                    allergies_txt = util_v2.extract_section_text(txt_between_markers, "allergies")
                    fam_history_txt = util_v2.extract_section_text(txt_between_markers, "family history")
                    soc_history_txt = util_v2.extract_section_text(txt_between_markers, "social history")
                    func_history_txt = util_v2.extract_section_text(txt_between_markers, "functional history")

                    # [Reword Sections]
                    original_txt = ''

                    # [Questionaire]
                    if util_v2.is_na_string(raw_questionaire_txt) == True:
                        new_questionaire_txt = ''
                    else:
                        new_questionaire_txt = util_v2.reword_section_text(st.secrets["api_key"], model, questionaire_prompt, '**Questionaire Summary**', raw_questionaire_txt)+'\n\n'
                        original_txt += '**Questionaire Summary**:\n' + raw_questionaire_txt +'\n\n'

                    # [ICBC]
                    if util_v2.is_na_string(raw_icbc_txt) == True:
                        new_icbc_txt = ''
                    else:
                        new_icbc_txt = util_v2.reword_section_text(st.secrets["api_key"], model, icbc_prompt, '**ICBC/WBC**', raw_icbc_txt)+'\n\n'
                        original_txt += '**ICBC/WBC**:\n' + raw_icbc_txt +'\n\n'
                    
                    # [Summary]
                    new_summary_txt = util_v2.reword_section_text(st.secrets["api_key"], model, summary_prompt, '**Summary**', summary_txt)
                    original_txt += '**Summary**:\n' + summary_txt
                    
                    # [Past Medical]
                    clean_past_medical_txt = util_v2.clean_section_text(st.secrets["api_key"], model, past_medical_txt)
                    new_past_medical_txt = util_v2.reword_section_text(st.secrets["api_key"], model, past_medical_prompt, '**Past Medical**', clean_past_medical_txt)
                    original_txt += '\n\n**Past Medical**:\n' + past_medical_txt
                    
                    # [Surgical History]
                    clean_surgical_history_txt = util_v2.clean_section_text(st.secrets["api_key"], model, surgical_history_txt)
                    new_surgical_history_txt = util_v2.reword_section_text(st.secrets["api_key"], model, surgical_history_prompt, '**Surgical History**', clean_surgical_history_txt)
                    original_txt += '\n\n**Surgical History**:\n' + surgical_history_txt
                    
                    # [Current Medication]
                    clean_current_meds_txt = util_v2.clean_section_text(st.secrets["api_key"], model, current_meds_txt)
                    new_current_meds_txt = util_v2.reword_section_text(st.secrets["api_key"], model, current_medication_prompt, '**Current Medication**', clean_current_meds_txt)
                    original_txt += '\n\n**Current Medication**:\n' + current_meds_txt

                    # [Allergies]
                    clean_allergies_txt = util_v2.clean_section_text(st.secrets["api_key"], model, allergies_txt)
                    new_allergies_txt = util_v2.reword_section_text(st.secrets["api_key"], model, allergies_prompt, '**Allergies**', clean_allergies_txt)
                    original_txt += '\n\n**Allergies**:\n' + allergies_txt

                    # [Family History]
                    clean_fam_history_txt = util_v2.clean_section_text(st.secrets["api_key"], model, fam_history_txt)
                    new_fam_history_txt = util_v2.reword_section_text(st.secrets["api_key"], model, family_history_prompt, '**Family History**', clean_fam_history_txt)
                    original_txt += '\n\n**Family History**:\n' + fam_history_txt
                    

                    # [Social History]
                    original_txt += '\n\n**Social History**:\n' + soc_history_txt

                    # Remove PII
                    if len(occupation_txt) > 0 and util_v2.contains_pii(occupation_txt) == False:
                        soc_history_txt = soc_history_txt.replace(occupation_txt, "<occupation>")
                    if len(employer_txt) > 0 and util_v2.contains_pii(employer_txt) == False:
                        soc_history_txt = soc_history_txt.replace(employer_txt, "<employer>")
                    if len(live_with_people_txt) > 0 and util_v2.contains_pii(live_with_people_txt) == False:
                        soc_history_txt = soc_history_txt.replace(live_with_people_txt, "<live_with_people>")
                    if len(name_txt) > 0:
                        soc_history_txt = soc_history_txt.replace(name_txt, "<name>")

                    # Reword
                    new_soc_history_txt = util_v2.reword_section_text(st.secrets["api_key"], model, social_history_prompt, '**Social History**', soc_history_txt)
                    
                    # Readd PII
                    if len(occupation_txt) > 0 and util_v2.contains_pii(occupation_txt) == False:
                        new_soc_history_txt = new_soc_history_txt.replace("<occupation>", occupation_txt)
                    if len(employer_txt) > 0 and util_v2.contains_pii(employer_txt) == False:
                        new_soc_history_txt = new_soc_history_txt.replace("<employer>", employer_txt)
                    if len(live_with_people_txt) > 0 and util_v2.contains_pii(live_with_people_txt) == False:
                        new_soc_history_txt = new_soc_history_txt.replace("<live_with_people>", live_with_people_txt)
                    if len(name_txt) > 0:
                        new_soc_history_txt = new_soc_history_txt.replace("<name>", name_txt)
                    
                    # [Functional History]
                    if util_v2.is_na_string(func_history_txt) == True:
                        new_func_history_txt = '**Functional History**:\nN/A'
                        original_txt += '\n\n**Functional History**:\nN/A'
                    else:
                        new_func_history_txt = util_v2.reword_section_text(st.secrets["api_key"], model, functional_history_prompt, '**Functional History**', func_history_txt)
                        original_txt += '\n\n**Functional History**:\n' + func_history_txt
                    
                    # [Combine Sections]
                    combine_sections = new_questionaire_txt + new_icbc_txt + new_summary_txt +'\n\n'+ new_past_medical_txt +'\n\n'+ new_surgical_history_txt +'\n\n'+ new_current_meds_txt +'\n\n'+ new_allergies_txt +'\n\n'+ new_fam_history_txt +'\n\n'+ new_soc_history_txt +'\n\n'+ new_func_history_txt

                # [Done]
                st.success('Done!')
                st.markdown('#')
                
                # [Format Text Strings for Display]
                original_txt_format = original_txt.replace('•\n', '+ ').replace('\n', '  \n')
                combine_sections_format = combine_sections.replace('•', '+').replace('\n', '  \n')

                original_txt_raw = original_txt.replace('**', '')
                combine_sections_raw = combine_sections.replace('**', '')

                # [Display Tabs to show Formatted or Raw text]
                tab1, tab2, tab3, tab4 = st.tabs(["Formatted", "Raw", "Processed Prompts", "Debug"])
                
                # Formatted Text
                with tab1:                
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Original Text**")
                        with st.container(border=True):
                            st.markdown(original_txt_format)

                    with col2:
                        st.write("**Rewordified Text**")
                        with st.container(border=True):
                            st.markdown(combine_sections_format)

                # Raw Text
                with tab2:  
                    col1, col2 = st.columns(2)             

                    with col1:
                        st.write("**Original Text (Raw)**")
                        with st.container(border=True):
                            st.code(original_txt_raw, language=None)

                    with col2:
                        st.write("**Rewordified Text (Raw)**")
                        with st.container(border=True):
                            st.code(combine_sections_raw, language=None)
                        
                # Prompts text sent
                with tab3:
                    if util_v2.is_na_string(raw_questionaire_txt) == False:
                        st.write("**Questionaire**")
                        with st.container(border=True):
                            st.markdown("INSTRUCTIONS:\n\n" + questionaire_prompt + "\n\nGIVEN INFORMATION:\n\n" + raw_questionaire_txt)

                    if util_v2.is_na_string(raw_icbc_txt) == False:
                        st.write("**ICBC**")
                        with st.container(border=True):
                            st.markdown("INSTRUCTIONS:\n\n" + icbc_prompt + "\n\nGIVEN INFORMATION:\n\n" + raw_icbc_txt)

                    st.write("**Summary**")
                    with st.container(border=True):
                        st.markdown("INSTRUCTIONS:\n\n" + summary_prompt + "\n\nGIVEN INFORMATION:\n\n" + summary_txt)

                    st.write("**Past Medical**")
                    with st.container(border=True):
                        st.markdown("INSTRUCTIONS:\n\n" + past_medical_prompt + "\n\nGIVEN INFORMATION:\n\n" + clean_past_medical_txt)

                    st.write("**Surgical History**")
                    with st.container(border=True):
                        st.markdown("INSTRUCTIONS:\n\n" + surgical_history_prompt + "\n\nGIVEN INFORMATION:\n\n" + clean_surgical_history_txt)

                    st.write("**Current Medication**")
                    with st.container(border=True):
                        st.markdown("INSTRUCTIONS:\n\n" + current_medication_prompt + "\n\nGIVEN INFORMATION:\n\n" + clean_current_meds_txt)

                    st.write("**Allergies**")
                    with st.container(border=True):
                        st.markdown("INSTRUCTIONS:\n\n" + allergies_prompt + "\n\nGIVEN INFORMATION:\n\n" + clean_allergies_txt)

                    st.write("**Family History**")
                    with st.container(border=True):
                        st.markdown("INSTRUCTIONS:\n\n" + family_history_prompt + "\n\nGIVEN INFORMATION:\n\n" + clean_fam_history_txt)

                    st.write("**Social History**")
                    with st.container(border=True):
                        st.markdown("INSTRUCTIONS:\n\n" + social_history_prompt + "\n\nGIVEN INFORMATION:\n\n" + soc_history_txt)

                    st.write("**Functional History**")
                    with st.container(border=True):
                        st.markdown("INSTRUCTIONS:\n\n" + functional_history_prompt + "\n\nGIVEN INFORMATION:\n\n" + func_history_txt)

                # Debug
                with tab4:
                    st.write("**Text between markers**")
                    with st.container(border=True):
                        st.markdown(txt_between_markers)

            elif pdf_file is None:
                st.write("Please choose a valid PDF file")
                
        except Exception as e:
            st.write("Error occurred 😓")
            st.exception(e)
    
if __name__ == '__main__': 
    main()