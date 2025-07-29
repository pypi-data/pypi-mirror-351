from PySide6.QtGui import QColor
from PySide6.QtCore import QPointF, Qt
import math


class ArtiPlugin:
    def __init__(self, viewer):
        self.viewer = viewer
        self.active = False

    def activate(self):
        self.active = True
        self.viewer.disattiva_zoom()
        self.viewer.image.setCursor(Qt.CrossCursor)
        # self.nomi = self.viewer.landmark_names
        LD_groups = list(self.viewer.landmarks_groups.keys())
        for layer_name in ["landmarks", "spezzata", "axis_definition"]:
            if layer_name in self.viewer.layer_manager.visible:
                self.viewer.layer_manager.visible[layer_name] = False

        self.viewer.layer_manager.clear_layer("spezzata_idealizzata")
        self.viewer.layer_manager.clear_layer("landmarks")
        self.viewer.layer_manager.clear_layer("axis_definition")
        # self.viewer.layer_manager.update_display()

        # print("LANDMARKS", self.viewer.landmarks)
        for gruppo in LD_groups:
            # print("GRUPPO FUNZIONALE", gruppo)
            landmark_names = self.viewer.landmarks_groups[gruppo]["landmarks"]
            angoli = self.viewer.landmarks_groups[gruppo]["angles"]
            nuova_spezzata = []
            if len(angoli) > 0:
                print(landmark_names, angoli)
                try:
                    punti = self.get_landmark_points_by_names(self.viewer.landmarks, landmark_names)
                    print("punti", punti)
                    nuova_spezzata = self.ricalcola_spezzata_orientata(landmark_names, punti, angoli)
                except ValueError as e:
                    print("Errore:", e)
            else:
                punti = self.get_landmark_points_by_names(self.viewer.landmarks, landmark_names)
                print("LLL", landmark_names)

            # Aggiorna il dizionario dei landmarks
            lista_tuple = [self.viewer.landmarks[k]["coordinates"] for k in landmark_names]
            lista_qpointf = []
            for coor in lista_tuple:
                if coor:
                    lista_qpointf.append(QPointF(coor[0], coor[1]))

            self.viewer.layer_manager.draw_points("spezzata_idealizzata", lista_qpointf, color=QColor(255, 0, 0, 180))

            if len(nuova_spezzata) > 0:
                self.viewer.layer_manager.draw_lines("spezzata_idealizzata", nuova_spezzata, color=QColor(0, 255, 0, 180))
            else:
                self.viewer.layer_manager.draw_lines("spezzata_idealizzata", punti, color=QColor(0, 255, 0, 180))

    def get_landmark_points_by_names(self, landmark_dict: dict, names: list[str]) -> list[tuple]:
        missing = [name for name in names if name not in landmark_dict]
        if missing:
            raise ValueError(f"I seguenti nomi non sono stati trovati nei landmark: {missing}")

        punti = []
        for name in names:
            dati = landmark_dict[name]
            if not dati["coordinates"]:
                raise ValueError(f"Il landmark '{name}' non ha coordinate assegnate.")
            punti.append(dati["coordinates"])  # un tuple (x, y)
        return punti

    def ricalcola_spezzata_orientata(self, landmark_names: list[str], punti: list[tuple], angoli: list[float]) -> list[tuple]:
        if len(punti) < 2 or len(punti) != len(angoli):
            raise ValueError("Hai bisogno di n punti e n-1 angoli tra i segmenti")
        # print(punti)
        distanze = [math.hypot(punti[i + 1][0] - punti[i][0], punti[i + 1][1] - punti[i][1]) for i in range(len(punti) - 1)]

        nuova_spezzata = [punti[0]]
        angolo_attuale = angoli[0]

        for i in range(len(distanze)):
            dx = distanze[i] * math.cos(math.radians(angolo_attuale))
            dy = distanze[i] * math.sin(math.radians(angolo_attuale))
            ultimo = nuova_spezzata[-1]
            nuovo_punto = (ultimo[0] + dx, ultimo[1] + dy)
            nuova_spezzata.append(nuovo_punto)
            self.viewer.landmarks[landmark_names[i + 1]]["coordinates"] = nuovo_punto

            angolo_attuale += angoli[i + 1]

        return nuova_spezzata
