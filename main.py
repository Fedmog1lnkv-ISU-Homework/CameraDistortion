import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class GraphApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Выбор файла")
        self.master.geometry("400x300")

        self.open_button = tk.Button(self.master, text="Выбрать файл", command=self.open_file)
        self.open_button.pack(pady=(self.master.winfo_reqheight() - self.open_button.winfo_reqheight()) / 2)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.master.withdraw()
            self.show_graph_screen(file_path)

    def show_graph_screen(self, file_path):
        graph_screen = tk.Tk()
        graph_screen.title("График с ползунками и текстовыми полями")

        frame = ttk.Frame(graph_screen)
        frame.grid(row=0, column=0, padx=10, pady=10)

        fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        center_frame = ttk.Frame(graph_screen)
        center_frame.grid(row=1, column=0, padx=10, pady=10)
        center_frame.columnconfigure(0, weight=1)

        def update_plot(*args):
            Zfar = -10
            Zfar = float(Zfar_slider.get())
            Znear = float(Znear_slider.get())
            dX = float(dX_slider.get())
            dY = float(dY_slider.get())
            camx = float(camx_slider.get())
            camy = float(camy_slider.get())
            angle = np.radians(float(XY_slider.get()))

            K1 = float(K1_slider.get())

            Zrange = Zfar - Znear

            dots_center = np.array([0.1, 0.1])

            cos_val = np.cos(angle)
            sin_val = np.sin(angle)

            if Zrange == 0:
                Zrange = 1

            P = np.array(
                [[cos_val, -sin_val, dX, 0], [sin_val, cos_val, dY, 0], [0, 0, -Zfar / Zrange, Znear * Zfar / Zrange],
                 [0, 0, 1, 0]])
            Cam = np.array([[camx, 0, 0, 0], [0, camy, 0, 0], [0, 0, 1, 0]])
            dots = []

            for i in range(object.shape[0]):
                f = Cam @ P @ object[i, :]
                if f[2] == 0:
                    dots.append(f)
                    continue
                dots.append(f / f[2])
            dots = np.array(dots)

            r = (dots[:, :2] - dots_center) ** 2

            f1 = (r).sum(axis=1)
            f2 = (r ** 2).sum(axis=1)

            K2 = 0.0
            mask = np.expand_dims(K1 * f1 + K2 * f2, axis=-1)
            dots_new = (dots[:, :2]) + (dots[:, :2] - dots_center) * mask

            self.ax.clear()
            self.ax.plot(dots_new[:, 0], dots_new[:, 1], '-D')
            self.canvas.draw()

        def apply_values():
            try:
                XY = float(XY_entry.get())
                XY_slider.set(XY)

                Zfar = float(Zfar_entry.get())
                Zfar_slider.set(Zfar)

                Znear = float(Znear_entry.get())
                Znear_slider.set(Znear)

                dX = float(dX_entry.get())
                dX_slider.set(dX)

                dY = float(dY_entry.get())
                dY_slider.set(dY)

                camx = float(camx_entry.get())
                camx_slider.set(camx)

                camy = float(camx_entry.get())
                camy_slider.set(camx)

                K1 = float(K1_entry.get())
                K1_slider.set(K1)
                update_plot()
            except ValueError:
                pass

        def reset_values(row):
            XY_entry.delete(0, tk.END)
            XY_entry.insert(0, "0.0")

            Zfar_entry.delete(0, tk.END)
            Zfar_entry.insert(0, "-10.0")

            Znear_entry.delete(0, tk.END)
            Znear_entry.insert(0, "-3.0")

            dX_entry.delete(0, tk.END)
            dX_entry.insert(0, "-0.2")

            dY_entry.delete(0, tk.END)
            dY_entry.insert(0, "-0.5")

            camx_entry.delete(0, tk.END)
            camx_entry.insert(0, "1.0")

            camy_entry.delete(0, tk.END)
            camy_entry.insert(0, "1.0")

            K1_entry.delete(0, tk.END)
            K1_entry.insert(0, "1.0")

            apply_values()

        def update_from_entry(entry, slider):
            try:
                value = float(entry.get())
                slider.set(value)
                update_plot()
            except ValueError:
                pass

        def update_from_slider(slider, entry):
            value = slider.get()
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            update_plot()

        def select_all(event):
            event.widget.icursor(0)
            event.widget.select_range(0, 'end')

        def create(name, original_meaning="0.0", from_=0, to=10, row=0):
            label = ttk.Label(center_frame, text=name)
            label.grid(row=row, column=0, padx=10, pady=5)
            slider = ttk.Scale(center_frame, from_=from_, to=to, command=lambda x: update_from_slider(slider, entry))
            slider.grid(row=row, column=1, padx=10, pady=5)
            entry = ttk.Entry(center_frame)
            entry.grid(row=row, column=2, padx=10, pady=5)
            entry.insert(0, original_meaning)
            entry.bind("<FocusIn>", select_all)

            slider.bind("<ButtonRelease-1>", lambda event: update_from_entry(entry, slider))
            entry.bind("<Return>", lambda event: update_from_entry(entry, slider))

            return label, slider, entry

        object = []
        with open(file_path, 'r') as f:
            for s in f:
                s += ' 1'
                object.append(s.split())
            object = np.array(object).astype(float)

        row = 0
        XY_label, XY_slider, XY_entry = create(name="Повороты в плоскости XY:", original_meaning="0.0", from_=-180,
                                               to=180, row=row)
        Zfar_label, Zfar_slider, Zfar_entry = create(name="Zfar:", original_meaning="-10.0", from_=-10, to=10,
                                                     row=row + 1)
        Znear_label, Znear_slider, Znear_entry = create("Znear:", original_meaning="-3.0", from_=-10, to=10,
                                                        row=row + 2)
        dX_label, dX_slider, dX_entry = create("dX:", original_meaning="-0.2", from_=-10, to=10, row=row + 3)
        dY_label, dY_slider, dY_entry = create("dY:", original_meaning="-0.5", from_=-10, to=10, row=row + 4)
        camx_label, camx_slider, camx_entry = create("cam x:", original_meaning="1.0", from_=-10, to=10, row=row + 5)
        camy_label, camy_slider, camy_entry = create("cam y:", original_meaning="1.0", from_=-10, to=10, row=row + 6)
        K1_label, K1_slider, K1_entry = create("K1:", original_meaning="1.0", from_=-10, to=10, row=row + 7)

        apply_values()

        apply_button = ttk.Button(graph_screen, text="Применить", command=apply_values)
        apply_button.grid(row=row + 8, column=0, padx=10, pady=5)

        reset_button = ttk.Button(graph_screen, text="Сбросить", command=lambda: reset_values(row))
        reset_button.grid(row=row + 9, column=0, padx=10, pady=5)

        update_plot()

        graph_screen.mainloop()


root = tk.Tk()
app = GraphApp(root)
root.mainloop()
