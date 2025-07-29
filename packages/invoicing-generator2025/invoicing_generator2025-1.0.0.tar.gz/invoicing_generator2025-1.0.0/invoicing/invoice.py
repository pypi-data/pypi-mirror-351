import pandas as pd
import glob
from fpdf import FPDF
from pathlib import Path
import os

def generate(invoices_path, pdfs_path, image_path, product_id, product_name, amount_purchased, price_per_unit, total_price):
    filepaths = glob.glob(f"{invoices_path}/*.xlsx")
    """
    This function converts invoice Excel files into pdf invoices.
    :param invoices_path: The path where your excel files are located.
    :param pdfs_path: The path where you want get the output pdf files.
    :param image_path: Your company or your organization logo path.
    :param product_id: Enter your excel files first column name,ex-product_id,id.
    :param product_name: Enter your excel files second column name,ex-product_name,name.
    :param amount_purchased: Enter your excel files third column name,ex-amount_purchased,quantity
    :param price_per_unit: Enter your excel files forth column name,ex-price_per_unit,price_per_piece
    :param total_price: Enter your excel files fifth column name,ex-total_price,sum_of_total
    :return: Returns all the output of the generated pdf files from excel files.
    """

    #Getting the data from the Excel files 

    for filepath in filepaths:
        
        pdf = FPDF(orientation="p", unit="mm", format="A4")
        pdf.add_page()

        filename = Path(filepath).stem
        invoice_nr, date = filename.split("-")

        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=50, h=8, txt=f"Invoice num. {invoice_nr}", ln=1)

        pdf.set_font(family="Times", size=16, style="B")
        pdf.cell(w=50, h=8, txt=f"Date {date}", ln=1)


        df = pd.read_excel(filepath)


    #Add Header
    
        column = [item.replace("_"," ").title() for item in list(df.columns)]
        pdf.set_font(family="Times", size=10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=30, h=8, txt=column[0], border=1)
        pdf.cell(w=70, h=8, txt=column[1], border=1)
        pdf.cell(w=30, h=8, txt=column[2], border=1)
        pdf.cell(w=30, h=8, txt=column[3], border=1)
        pdf.cell(w=30, h=8, txt=column[4], border=1, ln=1)

    # Add rows to the tables
        for index, row in df.iterrows():
            pdf.set_font(family="Times", size=10)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(w=30, h=8, txt=str(row[product_id]), border=1)
            pdf.cell(w=70, h=8, txt=str(row[product_name]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[amount_purchased]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[price_per_unit]), border=1)
            pdf.cell(w=30, h=8, txt=str(row[total_price]), border=1, ln=1)

        #Total value adding on the end of the row 
        
        total = df[total_price].sum()
        pdf.set_font(family="Times", size=10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=70, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt="", border=1)
        pdf.cell(w=30, h=8, txt=str(total), border=1, ln=1)

        #Add total price sentence

        pdf.set_font(family="Times", size=10)
        pdf.cell(w=30, h=8, txt=f"The Total Price is {total} taka", ln=1)

        #Add company name and logo

        pdf.set_font(family="Times", size=14, style="B")
        pdf.cell(w=40, h=8, txt="SILICA SHEARD")
        pdf.image(f"{image_path}", w=10)
        
        if not os.path.exists(pdfs_path):
            os.makedirs(pdfs_path)
        pdf.output(f"{pdfs_path}/{filename}")

    
