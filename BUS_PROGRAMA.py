import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime

# Excepciones personalizadas
class HoraInvalidaException(Exception):
    pass

class PasajeDuplicadoException(Exception):
    pass

class ArchivoNoEncontradoException(Exception):
    pass

class Ruta:
    def __init__(self, codigo, origen, destino, hora_salida, hora_llegada):
        self.__codigo = codigo
        self.__origen = origen
        self.__destino = destino
        self.__hora_salida = self.validar_hora(hora_salida)
        self.__hora_llegada = self.validar_hora(hora_llegada)
        self.pasajes = set()
    @staticmethod
    def validar_hora(hora):
        try:
            datetime.strptime(hora, "%H:%M")
            return hora
        except ValueError:
            raise HoraInvalidaException(f"Hora inválida: {hora}")
    @property
    def codigo(self):
        return self.__codigo
    @property
    def origen(self):
        return self.__origen
    @property
    def destino(self):
        return self.__destino
    @property
    def hora_salida(self):
        return self.__hora_salida
    @property
    def hora_llegada(self):
        return self.__hora_llegada
    def vender_pasaje(self, pasajero):
        if pasajero in self.pasajes:
            raise PasajeDuplicadoException(f"El pasajero {pasajero} ya tiene un pasaje.")
        self.pasajes.add(pasajero)
    def cancelar_pasaje(self, pasajero):
        self.pasajes.discard(pasajero)
    def ocupacion(self):
        return len(self.pasajes)
    def lista_pasajeros(self):
        return list(self.pasajes)
    def generar_reporte(self):
        raise NotImplementedError("Método debe ser implementado por subclases.")

class Bus(Ruta):
    def __init__(self, codigo, origen, destino, hora_salida, hora_llegada, capacidad, tipo="Normal"):
        super().__init__(codigo, origen, destino, hora_salida, hora_llegada)
        self.__capacidad = capacidad
        self.tipo = tipo
    @property
    def capacidad(self):
        return self.__capacidad
    def vender_pasaje(self, pasajero):
        if self.ocupacion() >= self.capacidad:
            raise Exception("Bus lleno. No se puede vender más pasajes.")
        super().vender_pasaje(pasajero)
    def cancelar_pasaje(self, pasajero):
        super().cancelar_pasaje(pasajero)
    def generar_reporte(self):
        return (f"Bus {self.codigo}: {self.origen} -> {self.destino} | "
                f"Salida: {self.hora_salida} | Llegada: {self.hora_llegada} | "
                f"Capacidad: {self.capacidad} | Ocupación: {self.ocupacion()} | Tipo: {self.tipo}")

rutas_ciudad = {}

# Ventana para mostrar rutas registradas
def mostrar_rutas_gui():
    top = tk.Toplevel(root)
    top.title("Rutas Registradas")
    top.geometry("520x400")
    tree = ttk.Treeview(top, columns=("codigo", "origen", "destino", "salida", "llegada", "capacidad", "tipo", "ocupacion"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col.capitalize())
    tree.pack(fill="both", expand=True)
    for ciudad, rutas in rutas_ciudad.items():
        for bus in rutas.values():
            tree.insert("", tk.END, values=(
                bus.codigo,
                bus.origen,
                bus.destino,
                bus.hora_salida,
                bus.hora_llegada,
                bus.capacidad,
                bus.tipo,
                bus.ocupacion()
            ))
    if not tree.get_children():
        tk.Label(top, text="No hay rutas registradas.").pack()

# Ventana para mostrar pasajeros de una ruta
def mostrar_pasajeros_gui():
    ciudad = simpledialog.askstring("Mostrar pasajeros", "Ciudad de origen:", initialvalue="Huancayo")
    if not ciudad or ciudad not in rutas_ciudad:
        messagebox.showerror("Error", "Ciudad no encontrada.")
        return
    codigos = list(rutas_ciudad[ciudad].keys())
    codigo = simpledialog.askstring("Mostrar pasajeros", f"Código de ruta ({', '.join(codigos)}):")
    if not codigo or codigo not in rutas_ciudad[ciudad]:
        messagebox.showerror("Error", "Ruta no encontrada.")
        return
    bus = rutas_ciudad[ciudad][codigo]
    lista = bus.lista_pasajeros()
    top = tk.Toplevel(root)
    top.title(f"Pasajeros en ruta {codigo}")
    top.geometry("400x300")
    if lista:
        tk.Label(top, text=f"Pasajeros de la ruta {codigo} ({bus.origen} - {bus.destino}):").pack()
        listbox = tk.Listbox(top, width=50)
        listbox.pack(padx=10, pady=10, fill="both", expand=True)
        for nombre in lista:
            listbox.insert(tk.END, nombre)
    else:
        tk.Label(top, text="No hay pasajeros en esta ruta.").pack(padx=10, pady=30)

# Resto del sistema (igual que antes)
def registrar_ruta_gui():
    top = tk.Toplevel(root)
    top.title("Registrar Ruta")
    top.geometry("350x350")
    labels = ["Código", "Origen (Huancayo)", "Destino", "Hora Salida (HH:MM)", "Hora Llegada (HH:MM)", "Capacidad", "Tipo (Ej: Económico)"]
    entries = []
    for i, text in enumerate(labels):
        tk.Label(top, text=text).grid(row=i, column=0, sticky='w', pady=2)
        entry = tk.Entry(top)
        entry.grid(row=i, column=1)
        entries.append(entry)
    def submit():
        try:
            codigo = entries[0].get()
            origen = entries[1].get() or "Huancayo"
            destino = entries[2].get()
            hora_salida = entries[3].get()
            hora_llegada = entries[4].get()
            capacidad = int(entries[5].get())
            tipo = entries[6].get() or "Normal"
            bus = Bus(codigo, origen, destino, hora_salida, hora_llegada, capacidad, tipo)
            if origen not in rutas_ciudad:
                rutas_ciudad[origen] = {}
            rutas_ciudad[origen][codigo] = bus
            messagebox.showinfo("OK", f"Ruta registrada para {origen} a {destino}.")
            top.destroy()
        except HoraInvalidaException as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")
    tk.Button(top, text="Registrar", command=submit).grid(row=len(labels), column=0, columnspan=2, pady=10)

def consultar_rutas_gui():
    ciudad = simpledialog.askstring("Consultar rutas", "Ingrese la ciudad de origen:", initialvalue="Huancayo")
    reporte = ""
    if ciudad and ciudad in rutas_ciudad:
        for bus in rutas_ciudad[ciudad].values():
            reporte += bus.generar_reporte() + "\n"
    else:
        reporte = "No hay rutas para esta ciudad."
    messagebox.showinfo("Consulta de rutas", reporte)

def vender_pasaje_gui():
    ciudad = simpledialog.askstring("Venta pasaje", "Ciudad de origen:", initialvalue="Huancayo")
    if not ciudad or ciudad not in rutas_ciudad:
        messagebox.showerror("Error", "Ciudad no encontrada.")
        return
    codigos = list(rutas_ciudad[ciudad].keys())
    codigo = simpledialog.askstring("Venta pasaje", f"Código de ruta ({', '.join(codigos)}):")
    if not codigo or codigo not in rutas_ciudad[ciudad]:
        messagebox.showerror("Error", "Ruta no encontrada.")
        return
    pasajero = simpledialog.askstring("Venta pasaje", "Nombre del pasajero:")
    if not pasajero:
        return
    try:
        rutas_ciudad[ciudad][codigo].vender_pasaje(pasajero)
        messagebox.showinfo("OK", f"Pasaje vendido a {pasajero}.")
    except PasajeDuplicadoException as e:
        messagebox.showerror("Error", str(e))
    except Exception as e:
        messagebox.showerror("Error", str(e))

def cancelar_pasaje_gui():
    ciudad = simpledialog.askstring("Cancelar pasaje", "Ciudad de origen:", initialvalue="Huancayo")
    if not ciudad or ciudad not in rutas_ciudad:
        messagebox.showerror("Error", "Ciudad no encontrada.")
        return
    codigos = list(rutas_ciudad[ciudad].keys())
    codigo = simpledialog.askstring("Cancelar pasaje", f"Código de ruta ({', '.join(codigos)}):")
    if not codigo or codigo not in rutas_ciudad[ciudad]:
        messagebox.showerror("Error", "Ruta no encontrada.")
        return
    pasajero = simpledialog.askstring("Cancelar pasaje", "Nombre del pasajero:")
    if not pasajero:
        return
    rutas_ciudad[ciudad][codigo].cancelar_pasaje(pasajero)
    messagebox.showinfo("OK", f"Pasaje cancelado para {pasajero}.")

def reporte_diario_gui():
    nombre_archivo = "reporte_huancayo.txt"
    try:
        with open(nombre_archivo, "w") as f:
            for ciudad, rutas in rutas_ciudad.items():
                f.write(f"Ciudad: {ciudad}\n")
                for bus in rutas.values():
                    f.write(bus.generar_reporte() + "\n")
                f.write("\n")
        messagebox.showinfo("Reporte", f"Reporte diario guardado como '{nombre_archivo}'.")
    except Exception as e:
        raise ArchivoNoEncontradoException(f"Archivo {nombre_archivo} no encontrado.")

# Interfaz principal
root = tk.Tk()
root.title("Control de Horarios de Transporte - Huancayo, Junín, Perú")
root.geometry("400x600")

frame = tk.Frame(root, pady=20)
frame.pack()

btn1 = tk.Button(frame, text="Registrar Ruta", width=30, command=registrar_ruta_gui)
btn1.pack(pady=6)
btn2 = tk.Button(frame, text="Consultar Rutas por Ciudad", width=30, command=consultar_rutas_gui)
btn2.pack(pady=6)
btn3 = tk.Button(frame, text="Vender Pasaje", width=30, command=vender_pasaje_gui)
btn3.pack(pady=6)
btn4 = tk.Button(frame, text="Cancelar Pasaje", width=30, command=cancelar_pasaje_gui)
btn4.pack(pady=6)
btn5 = tk.Button(frame, text="Generar Reporte Diario", width=30, command=reporte_diario_gui)
btn5.pack(pady=6)
btn6 = tk.Button(frame, text="Mostrar Rutas Registradas", width=30, command=mostrar_rutas_gui)
btn6.pack(pady=6)
btn7 = tk.Button(frame, text="Mostrar Pasajeros de Ruta", width=30, command=mostrar_pasajeros_gui)
btn7.pack(pady=6)

lbl = tk.Label(root, text="Hecho para la empresa de buses de Huancayo, Junín, Perú.", font=("Arial", 9))
lbl.pack(side="bottom", pady=10)

root.mainloop()