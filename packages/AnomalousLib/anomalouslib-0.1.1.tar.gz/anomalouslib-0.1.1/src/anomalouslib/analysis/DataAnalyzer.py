import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

# Classe per a l'anàlisi de dades
class DataAnalyzer:
    def __init__(self, dataset):
        self.dataset = dataset
    
    def mostrar_trajectories(self, title="Simulació de Moviment Brownià en 2D", interval=0):
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.subplots_adjust(bottom=0.2)

        def update(val):
            ax.clear()
            try:
                new_interval = int(text_box.text)
            except ValueError:
                new_interval = interval

            for index, row in self.dataset.iterrows():
                x, y = row["coords"]
                ax.plot(x, y, label=f'Trajectòria {index+1}')
                if new_interval > 0:
                    for j in range(0, len(x), new_interval):
                        ax.text(x[j], y[j], f'{j}', fontsize=8, color='black')

            ax.scatter(self.dataset["coords"].apply(lambda c: c[0][0]), 
                       self.dataset["coords"].apply(lambda c: c[1][0]), 
                       color='red', marker='o', label="Inici")
            ax.scatter(self.dataset["coords"].apply(lambda c: c[0][-1]), 
                       self.dataset["coords"].apply(lambda c: c[1][-1]), 
                       color='blue', marker='x', label="Fi")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_title(title)
            ax.legend()
            ax.grid()
            fig.canvas.draw()
        
        ax_textbox = plt.axes([0.2, 0.05, 0.2, 0.075])
        text_box = TextBox(ax_textbox, "Interval", initial=str(interval))
        text_box.on_submit(update)
        update(None)
        plt.show()
    
    def mostrar_evolucio(self):
        num_passos = len(self.dataset.iloc[0]["coords"][0])
        each_range = num_passos // 25
        distances = {i: [] for i in range(each_range, num_passos+1, each_range)}
        
        for index, row in self.dataset.iterrows():
            x, y = row["coords"]
            for step in range(each_range, num_passos+1, each_range):
                distance = np.sqrt((x[step-1] - x[0])**2 + (y[step-1] - y[0])**2)
                distances[step].append(distance)

        # Calcular les mitjanes de les distàncies
        mean_distances = {step: np.mean(distances[step]) for step in distances}

        # Crear el plot
        plt.figure(figsize=(10, 6))
        plt.plot([0] + list(mean_distances.keys()), [0] + list(mean_distances.values()), marker='o', linestyle='-', color='b')
        plt.title("Distància mitjana des del punt (0,0) a diferents punts finals")
        plt.xlabel("Punt final (n)")
        plt.ylabel("Distància mitjana")
        plt.grid(True)
        plt.show()
    
    def mostrar_histograma(self):
        final_points_x = self.dataset["coords"].apply(lambda c: c[0][-1])
        final_points_y = self.dataset["coords"].apply(lambda c: c[1][-1])

        # Crear histogrames en 2D
        hist, x_edges, y_edges = np.histogram2d(final_points_x, final_points_y, bins=[40, 40])

        # Crear el gràfic 3D
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        # Definir coordenades del centre dels bins
        x_pos, y_pos = np.meshgrid(x_edges[:-1] + 0.5, y_edges[:-1] + 0.5)
        x_pos = x_pos.ravel()
        y_pos = y_pos.ravel()
        z_pos = np.zeros_like(x_pos)

        # Alçada de les barres
        dz = hist.ravel()

        # Filtrar les barres amb alçada 0
        non_zero_indices = dz > 0
        x_pos = x_pos[non_zero_indices]
        y_pos = y_pos[non_zero_indices]
        z_pos = z_pos[non_zero_indices]
        dz = dz[non_zero_indices]

        # Ajustar la mida de les barres
        dx = dy = (x_edges[1] - x_edges[0]) * 0.8  # Ajustar l'amplada de les barres

        # Gràficar barres 3D
        ax.bar3d(x_pos, y_pos, z_pos, dx, dy, dz, shade=True)

        # Etiquetes
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Quantitat de partícules')
        ax.set_title('Distribució de partícules al final de les trajectòries')

        plt.show()