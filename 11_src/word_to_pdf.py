import os
import win32com.client

base = r'D:\Brain\07_Research\AI-INVENTORY-OPTIMIZATION\09_reports\final'
src = os.path.join(base, 'research_report.docx')
pdf = os.path.join(base, 'docx_visual_qa.pdf')
for f in (pdf,):
    if os.path.exists(f):
        os.remove(f)
word = win32com.client.DispatchEx('Word.Application')
word.Visible = False
word.DisplayAlerts = False
doc = word.Documents.Open(src)
doc.SaveAs(pdf, FileFormat=17)
pages = doc.ComputeStatistics(2)  # wdStatisticPages
doc.Close(False)
word.Quit()
print('pages:', pages)
print('pdf bytes:', os.path.getsize(pdf))
