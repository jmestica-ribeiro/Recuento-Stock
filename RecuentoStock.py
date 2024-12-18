import tkinter as tk
from tkinter import ttk, messagebox  # Importar messagebox correctamente
from collections import defaultdict
import pandas as pd
from fpdf import FPDF
import psycopg2
from dotenv import load_dotenv
import os

class BarcodeCounterApp:
    def __init__(self, root):

        host = os.getenv("HOST")
        database = os.getenv("DATABASE")
        user = os.getenv("USER")
        password = os.getenv("PASSWORD")

        # Configuración de la base de datos
        self.db_conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        self.db_cursor = self.db_conn.cursor()

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
        self.tree = ttk.Treeview(root, columns=("Codigo", "Nombre", "Unidades"), show="headings", height=15)
        self.tree.heading("Codigo", text="Código")
        self.tree.heading("Nombre", text="Nombre del Producto")
        self.tree.heading("Unidades", text="Unidades")
        self.tree.column("Codigo", width=150, anchor="center")
        self.tree.column("Nombre", width=200, anchor="center")
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
            try:
                # Buscar en la base de datos
                query = "SELECT productonombre FROM productos WHERE productocodigo = %s;"
                self.db_cursor.execute(query, (barcode,))
                result = self.db_cursor.fetchone()

                if result:
                    productonombre = result[0]  # Extraer el nombre del producto
                    
                    # Contabilizar el ítem
                    if barcode in self.items:
                        self.items[barcode]["unidades"] += 1
                    else:
                        self.items[barcode] = {"nombre": productonombre, "unidades": 1}

                    # Actualizar la tabla
                    self.update_treeview()

                else:
                    # Mostrar mensaje si no se encuentra el código
                    messagebox.showwarning("Código no encontrado", f"El código {barcode} no está en la base de datos.")

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo buscar el código: {e}")

        # Leer el código de barras y limpiar entrada
        barcode = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if barcode:
            try:
                # Buscar en la base de datos
                query = "SELECT productonombre FROM productos WHERE productocodigo = %s;"
                self.db_cursor.execute(query, (barcode,))
                result = self.db_cursor.fetchone()

                if result:
                    productonombre.nombre = result
                    # Contabilizar el ítem
                    self.items[barcode] += 1
                    self.update_treeview()
                    print(productonombre)
                    # Opcional: mostrar información adicional
                    # print(f"Código: {barcode}, Descripción: {descripcion}, Precio: {precio}")
                else:
                    # Mostrar mensaje si no se encuentra el código
                    messagebox.showwarning("Código no encontrado", f"El código {barcode} no está en la base de datos.")

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo buscar el código: {e}")

    def update_treeview(self):
        # Limpiar el Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insertar datos actualizados
        for barcode, info in self.items.items():
            self.tree.insert("", tk.END, values=(barcode, info["nombre"], info["unidades"]))

    def export_to_excel(self):
        # Crear un DataFrame con los datos
        data = {
            "Código": [barcode for barcode in self.items],
            "Nombre del Producto": [info["nombre"] for info in self.items.values()],
            "Unidades": [info["unidades"] for info in self.items.values()],
        }
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

        # Título del documento
        pdf.cell(200, 10, txt="Recuento de Stock", ln=True, align="C")
        pdf.ln(10)

        # Encabezados de la tabla
        pdf.set_font("Arial", size=10, style="B")
        pdf.cell(70, 10, txt="Código", border=1, align="C")
        pdf.cell(90, 10, txt="Nombre del Producto", border=1, align="C")
        pdf.cell(30, 10, txt="Unidades", border=1, align="C")
        pdf.ln()

        # Contenido de la tabla
        pdf.set_font("Arial", size=10)
        for barcode, info in self.items.items():
            pdf.cell(70, 10, txt=barcode, border=1, align="C")
            pdf.cell(90, 10, txt=info["nombre"], border=1, align="C")
            pdf.cell(30, 10, txt=str(info["unidades"]), border=1, align="C")
            pdf.ln()

        # Guardar el archivo PDF
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

    #Database
    load_dotenv()

    root = tk.Tk()
    app = BarcodeCounterApp(root)
    root.mainloop()

