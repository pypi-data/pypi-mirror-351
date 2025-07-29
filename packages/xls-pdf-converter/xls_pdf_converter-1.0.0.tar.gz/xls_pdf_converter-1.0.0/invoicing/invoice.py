import os.path

import pandas as pd
import glob
from fpdf import FPDF
from pathlib import Path

def generate(invoices_path,pdfs_path):
    """This function converts xls files to pdf"""
    filepaths = glob.glob(f"{invoices_path}/*.xlsx")

    for filepath in filepaths:
        df = pd.read_excel(filepath)
        pdf = FPDF(orientation="p",unit="mm",format="A4")
        pdf.add_page()
        pdf.set_font(family="Times",style="B",size=16)

        # Clean filename
        filename = Path(filepath).stem
        invoice_no,date_str = filename.split("-")

        # Invoice details
        pdf.cell(w=50, h=8, txt=f"Invoice nr.{invoice_no}", border=0, align="L",ln=1)
        pdf.cell(w=50, h=8, txt=f"Date {date_str}",border=0,align="L",ln=1)
        pdf.ln()

        # Table headers
        pdf.set_font(family="Times", style="B", size=14)
        col_widths = []
        padding = 4  # extra padding for aesthetics

        for col in df.columns:
            max_width = pdf.get_string_width(str(col))
            for val in df[col]:
                val_width = pdf.get_string_width(str(val))
                if val_width > max_width:
                    max_width = val_width
            col_widths.append(max_width + padding)

        pdf.set_font(family="Times", style="B", size=12)
        for index_col,col in enumerate(df.columns):
            pdf.cell(w=col_widths[index_col], h=8, txt=f"{col.replace('_',' ').title()}", border=1, align="L")
        pdf.ln()

        # Table rows
        pdf.set_font(family="Times",size=12)
        for index_row,row in df.iterrows():
            for i,col in enumerate(df.columns):
                pdf.cell(w=col_widths[i], h=8, txt=str(df[col][index_row]), border=1)
            pdf.ln()

        # Total row
        for index_sum,col in enumerate(df.columns):
            if col == "total_price":
                pdf.cell(w=col_widths[index_sum], h=8, txt=str(sum(df["total_price"])), border=1,ln=1)
            else:
                pdf.cell(w=col_widths[index_sum], h=8, txt="", border=1)

        pdf.ln()
        pdf.set_font(family="Times", style="B", size=14)
        pdf.cell(w=50, h=8, txt=f"The total due amount is {sum(df["total_price"])} Euros", border=0,align="L")

        # Save PDF
        if not os.path.exists(pdfs_path):
            os.mkdir(pdfs_path)

        pdf.output(f"{pdfs_path}/{filename}.pdf")


