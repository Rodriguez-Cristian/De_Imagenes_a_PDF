import os
from tkinter import Tk, filedialog, Button, Label, ttk
import ttkbootstrap as tb
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def resize_image(image_path, max_size):
    img = Image.open(image_path)
    width, height = img.size

    if width > height:
        new_width = max_size
        new_height = int(max_size * height / width)
    else:
        new_height = max_size
        new_width = int(max_size * width / height)

    resized_img = img.resize((new_width, new_height), Image.BICUBIC)
    
    return resized_img

def select_folder():
    global folder_path
    folder_path = filedialog.askdirectory()
    if folder_path:
        label.config(text="Carpeta seleccionada: " + folder_path)
        confirm_button.config(state="normal")

        # Actualizar información de la carpeta
        update_folder_info()

def update_folder_info():
    images = [f for f in os.listdir(folder_path) if f.endswith(('jpg', 'png', 'jpeg'))]
    num_images = len(images)
    folder_info_label.config(text=f"Número total de imágenes encontradas: {num_images}")

def convert_to_pdf():
    if not folder_path:
        label.config(text="Primero selecciona una carpeta")
        return

    images = [f for f in os.listdir(folder_path) if f.endswith(('jpg', 'png', 'jpeg'))]
    if not images:
        label.config(text="No se encontraron imágenes en la carpeta seleccionada")
        return
    
    pdf_filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not pdf_filename:
        label.config(text="No se ha especificado un nombre para el archivo PDF")
        return

    try:
        c = canvas.Canvas(pdf_filename, pagesize=A4)
        max_image_size = 600  

        # Barra de progreso
        progress_bar['maximum'] = len(images)
        progress_bar['value'] = 0

        for idx, img in enumerate(images, 1):
            img_path = os.path.join(folder_path, img)
            try:
                resized_img = resize_image(img_path, max_image_size)
                width, height = resized_img.size
                aspect = width / float(height)
                c.setPageSize((A4[0], A4[1]))
                c.drawInlineImage(resized_img, 0, 0, width=A4[0], height=A4[1])
                c.showPage()
            except Exception as e:
                # Manejo de errores mejorado: Registro de errores en un archivo de registro
                with open('error_log.txt', 'a') as log_file:
                    log_file.write(f"Error al procesar la imagen {img}: {e}\n")
                continue

            # Actualizar barra de progreso
            progress_bar['value'] = idx
            root.update_idletasks()

        c.save()
        if os.path.exists(pdf_filename):
            label.config(text=f"PDF creado en: {pdf_filename}")
        else:
            label.config(text="Hubo un error al crear el PDF")
    except Exception as e:
        label.config(text=f"Hubo un error al crear el PDF: {e}")

root = tb.Window()
root.title("Convertidor de imágenes a PDF")
tb.Style('superhero')
root.geometry("400x200")
folder_path = None

select_button = tb.Button(root, text="Seleccionar carpeta", command=select_folder,bootstyle="SUCCESS")
select_button.pack(pady=10)

confirm_button = tb.Button(root, text="Confirmar conversión", command=convert_to_pdf, state="disabled",bootstyle="WARNING")
confirm_button.pack(pady=10)

label = Label(root, text="")
label.pack()

folder_info_label = Label(root, text="")
folder_info_label.pack()

# Barra de progreso
progress_bar = tb.Progressbar(root, orient='horizontal', mode='determinate')
progress_bar.pack(fill='x', padx=10, pady=5)

root.mainloop()
