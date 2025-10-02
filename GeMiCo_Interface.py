import tkinter as tk

# Función para crear una ventana XY en una posición específica
def crear_ventana_xy(x_pos, y_pos, nombre):
    ventana = tk.Toplevel()
    ventana.title(nombre)
    ventana.geometry("200x200+{}+{}".format(x_pos, y_pos))
    ventana.configure(bg='white')
    ventana.attributes('-transparentcolor', 'white')
    ventana.overrideredirect(True)
    ventana.attributes('-topmost', True)

    canvas = tk.Canvas(ventana, width=200, height=200, bg='white', highlightthickness=0)
    canvas.pack()

    canvas.create_rectangle(0, 0, 200, 200, outline='cyan', width=2)
    punto = canvas.create_oval(95, 95, 105, 105, fill='cyan', outline='')

    def mover_punto(event):
        x = max(5, min(event.x, 195))
        y = max(5, min(event.y, 195))
        canvas.coords(punto, x-5, y-5, x+5, y+5)
        print(f"{nombre} → X: {x}, Y: {y}")

    canvas.bind("<B1-Motion>", mover_punto)
    return ventana

# Crear ventana principal con botón de salida
root = tk.Tk()
root.geometry("100x50+900+500")  # Pequeña ventana flotante con botón
root.configure(bg='white')
root.attributes('-transparentcolor', 'white')
root.overrideredirect(True)
root.attributes('-topmost', True)

btn_salir = tk.Button(root, text="Finalizar", command=root.quit, bg='black', fg='white', relief='flat')
btn_salir.pack()

# Obtener tamaño de pantalla para posicionar las ventanas
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Crear dos ventanas XY
ventana_izquierda = crear_ventana_xy(100, 100, "Control XY Izquierdo")
ventana_derecha = crear_ventana_xy(screen_width - 300, 100, "Control XY Derecho")

# Ejecutar la app
root.mainloop()