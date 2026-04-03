from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.shared import Pt, Inches
from docx.oxml import OxmlElement, ns
from datetime import datetime
import os

def create_element(name):
    return OxmlElement(name)

def create_attribute(element, name, value):
    element.set(ns.qn(name), value)

def add_page_number(run):
    fldChar1 = create_element('w:fldChar')
    create_attribute(fldChar1, 'w:fldCharType', 'begin')
    
    instrText = create_element('w:instrText')
    create_attribute(instrText, 'xml:space', 'preserve')
    instrText.text = "PAGE"
    
    fldChar2 = create_element('w:fldChar')
    create_attribute(fldChar2, 'w:fldCharType', 'end')
    
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)

def add_pto_conditional(run):
    # BEGIN IF
    fldChar_if_begin = create_element('w:fldChar')
    create_attribute(fldChar_if_begin, 'w:fldCharType', 'begin')
    run._r.append(fldChar_if_begin)
    
    instrText_if1 = create_element('w:instrText')
    create_attribute(instrText_if1, 'xml:space', 'preserve')
    instrText_if1.text = "IF "
    run._r.append(instrText_if1)
    
    # BEGIN PAGE
    fldChar_page_begin = create_element('w:fldChar')
    create_attribute(fldChar_page_begin, 'w:fldCharType', 'begin')
    run._r.append(fldChar_page_begin)
    
    instrText_page = create_element('w:instrText')
    create_attribute(instrText_page, 'xml:space', 'preserve')
    instrText_page.text = "PAGE"
    run._r.append(instrText_page)
    
    # END PAGE
    fldChar_page_end = create_element('w:fldChar')
    create_attribute(fldChar_page_end, 'w:fldCharType', 'end')
    run._r.append(fldChar_page_end)
    
    # " < "
    instrText_cmp = create_element('w:instrText')
    create_attribute(instrText_cmp, 'xml:space', 'preserve')
    instrText_cmp.text = " < "
    run._r.append(instrText_cmp)
    
    # BEGIN NUMPAGES
    fldChar_nump_begin = create_element('w:fldChar')
    create_attribute(fldChar_nump_begin, 'w:fldCharType', 'begin')
    run._r.append(fldChar_nump_begin)
    
    instrText_nump = create_element('w:instrText')
    create_attribute(instrText_nump, 'xml:space', 'preserve')
    instrText_nump.text = "NUMPAGES"
    run._r.append(instrText_nump)
    
    # END NUMPAGES
    fldChar_nump_end = create_element('w:fldChar')
    create_attribute(fldChar_nump_end, 'w:fldCharType', 'end')
    run._r.append(fldChar_nump_end)
    
    # " "P.T.O." "" "
    instrText_cond = create_element('w:instrText')
    create_attribute(instrText_cond, 'xml:space', 'preserve')
    instrText_cond.text = " \"P.T.O.\" \"\" "
    run._r.append(instrText_cond)
    
    # END IF
    fldChar_if_end = create_element('w:fldChar')
    create_attribute(fldChar_if_end, 'w:fldCharType', 'end')
    run._r.append(fldChar_if_end)

def export_paper_docx(sections_data: dict, subject_info: dict, is_answer_key: bool = False) -> str:
    """
    Exports a structured question paper or answer key adhering strictly to professional university limits.
    """
    doc = Document()
    
    # 1. Header Array
    mm_par = doc.add_paragraph()
    mm_run=mm_par.add_run("M.M.: ")
    mm_run.bold=True
    mm_run=mm_par.add_run(f"{subject_info.get('total_marks', 100)}")
    mm_run.bold=True
    mm_par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    title_text = subject_info.get('exam_title', 'Exam')
    if is_answer_key:
        title_text = f"Answer Key: {title_text}"
        
    title_par = doc.add_paragraph()
    title_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_par.add_run(title_text)
    title_run.bold = True
    title_run.font.size = Pt(20)

    line_par = doc.add_paragraph("-" * 100)
    line_par.alignment = WD_ALIGN_PARAGRAPH.CENTER

    
    details_par = doc.add_paragraph()
    details_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    details_par.add_run(f"Branch Name: {subject_info.get('branch_name', '')} ({subject_info.get('branch_code', '')})\n")
    details_par.add_run(f"Semester: {subject_info.get('sem_year', '')} | Subject: {subject_info.get('subject_name', '')} ({subject_info.get('subject_code', '')})\n")
    details_par.add_run("Time: 3 Hours")
    
    div_par = doc.add_paragraph("_" * 40)
    div_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 2. Body / Section Processing
    q_counter = 1
    section_mapping = [
        ("section_a", "SECTION-A / भाग - क"),
        ("section_b", "SECTION-B / भाग - ख"),
        ("section_c", "SECTION-C / भाग - ग")
    ]
    
    for sec_key, sec_title in section_mapping:
        sec_qs = sections_data.get(sec_key, [])
        if not sec_qs:
            continue
            
        doc.add_paragraph()
        
        sec_par = doc.add_paragraph()
        sec_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sr = sec_par.add_run(sec_title)
        sr.bold = True
        
        if not is_answer_key:
            note_par = doc.add_paragraph(f"Note: Attempt any {len(sec_qs)} questions. (Total Marks: {len(sec_qs)*2})")
            note_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            note_par.runs[0].italic = True
            
        doc.add_paragraph()
        
        for q_item in sec_qs:
            if not is_answer_key:
                doc.add_paragraph(f"Q{q_counter}. {q_item['q']}")
                options = q_item.get("options")
                if options:
                    for k, v in options.items():
                        p = doc.add_paragraph(f"{k}) {v}")
                        p.paragraph_format.left_indent = Pt(20)
            else:
                doc.add_paragraph(f"Q{q_counter}: {q_item['q']}")
                doc.add_paragraph(f"Ans: {q_item['a']}")
                
            doc.add_paragraph()
            q_counter += 1
            
    # 3. Footer Formatting (Page Numbers & Alignments)
    section = doc.sections[0]
    footer = section.footer
    footer_par = footer.paragraphs[0]
    
    # Set explicit tab stops (Center at 3.25", Right at 6.5" for 8.5x11 page)
    tab_stops = footer_par.paragraph_format.tab_stops
    tab_stops.add_tab_stop(Inches(3.25), WD_TAB_ALIGNMENT.CENTER)
    tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)

    footer_par.text = f"{subject_info.get('subject_code', 'SUB')}\tPage "
    add_page_number(footer_par.add_run())
    footer_par.add_run("\t")
    add_pto_conditional(footer_par.add_run())
    
    # 4. File Management
    os.makedirs("exports", exist_ok=True)
    filename = f"exports/{subject_info.get('subject_code', 'SUB')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    if is_answer_key:
        filename += "_ANS"
    filename += ".docx"
    doc.save(filename)
    
    return filename
