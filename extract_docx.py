from docx import Document

doc = Document("autonomous-it-issue-resolution.docx")
with open("autonomous-it-issue-resolution.txt", "w") as f:
    for para in doc.paragraphs:
        f.write(para.text + "\n")
