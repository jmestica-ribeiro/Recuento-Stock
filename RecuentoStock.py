import tkinter as tk
from tkinter import ttk, messagebox  # Importar messagebox correctamente
from collections import defaultdict
import pandas as pd
from fpdf import FPDF

class BarcodeCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recuento de Stock")
        self.root.geometry("500x550")
        self.root.resizable(False, False)

        # Almacén de conteo
        self.items = defaultdict(int)

        # Interfaz
        self.label = tk.Label(root, text="Escanee un código de barras:", font=("Arial", 14))
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, font=("Arial", 14))
        self.entry.pack(pady=10)
        self.entry.focus()

        # Treeview para mostrar datos tabulares
        self.tree = ttk.Treeview(root, columns=("Codigo", "Unidades"), show="headings", height=15)
        self.tree.heading("Codigo", text="Código")
        self.tree.heading("Unidades", text="Unidades")
        self.tree.column("Codigo", width=300, anchor="center")
        self.tree.column("Unidades", width=100, anchor="center")
        self.tree.pack(pady=10)

        # Botones
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.export_excel_btn = tk.Button(self.button_frame, text="Exportar a Excel", font=("Arial", 12), command=self.export_to_excel)
        self.export_excel_btn.grid(row=0, column=0, padx=10)

        self.export_pdf_btn = tk.Button(self.button_frame, text="Exportar a PDF", font=("Arial", 12), command=self.export_to_pdf)
        self.export_pdf_btn.grid(row=0, column=1, padx=10)

        self.clear_btn = tk.Button(self.button_frame, text="Limpiar", font=("Arial", 12), command=self.clear_data)
        self.clear_btn.grid(row=0, column=2, padx=10)

        # Vincular evento para procesar cuando se presione Enter
        self.entry.bind("<Return>", self.add_item)

    def add_item(self, event):
        # Leer el código de barras y limpiar entrada
        barcode = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if barcode:
            # Contabilizar el ítem
            self.items[barcode] += 1
            self.update_treeview()

    def update_treeview(self):
        # Limpiar el Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insertar datos actualizados
        for barcode, count in self.items.items():
            self.tree.insert("", tk.END, values=(barcode, count))

    def export_to_excel(self):
        # Crear un DataFrame con los datos
        data = {"Código": list(self.items.keys()), "Unidades": list(self.items.values())}
        df = pd.DataFrame(data)

        # Guardar en un archivo Excel
        try:
            df.to_excel("recuento_stock.xlsx", index=False)
            messagebox.showinfo("Éxito", "Datos exportados a 'recuento_stock.xlsx'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel: {e}")

    def export_to_pdf(self):
        # Crear un archivo PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Recuento de Stock", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=10)
        pdf.cell(100, 10, txt="Código", border=1, align="C")
        pdf.cell(50, 10, txt="Unidades", border=1, align="C")
        pdf.ln()

        for barcode, count in self.items.items():
            pdf.cell(100, 10, txt=barcode, border=1, align="C")
            pdf.cell(50, 10, txt=str(count), border=1, align="C")
            pdf.ln()

        try:
            pdf.output("recuento_stock.pdf")
            messagebox.showinfo("Éxito", "Datos exportados a 'recuento_stock.pdf'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a PDF: {e}")

    def clear_data(self):
        # Limpiar datos almacenados y el Treeview
        self.items.clear()
        self.update_treeview()
        messagebox.showinfo("Datos Limpiados", "Todos los datos han sido eliminados.")

# Inicializar la app
if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeCounterApp(root)
    root.mainloop()
