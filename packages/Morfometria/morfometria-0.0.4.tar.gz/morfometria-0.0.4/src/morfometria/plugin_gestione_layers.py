from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QHBoxLayout, QLabel

class LayerPlugin:
    def __init__(self, viewer):
        self.viewer = viewer

    def activate(self):
        dialog = LayerManagerDialog(self.viewer)
        self.viewer.disattiva_zoom()
        dialog.exec()

class LayerManagerDialog(QDialog):
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.setWindowTitle("Gestione Layer")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        # Label e ComboBox per i layer
        layout.addWidget(QLabel("Seleziona un layer:"))
        self.layer_combo = QComboBox()
        self.layer_combo.addItems(self.get_layer_names())
        layout.addWidget(self.layer_combo)

        # Pulsanti per azioni
        btn_layout = QHBoxLayout()
        self.btn_attiva = QPushButton("Attiva/Disattiva")
        self.btn_ripulisci = QPushButton("Ripulisci")
        self.btn_cancella = QPushButton("Cancella")
        btn_layout.addWidget(self.btn_attiva)
        btn_layout.addWidget(self.btn_ripulisci)
        btn_layout.addWidget(self.btn_cancella)
        layout.addLayout(btn_layout)

        # Pulsante OK
        self.ok_button = QPushButton("OK")
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

        # Connessioni ai pulsanti
        self.btn_attiva.clicked.connect(self.attiva_layer)
        self.btn_ripulisci.clicked.connect(self.ripulisci_layer)
        self.btn_cancella.clicked.connect(self.cancella_layer)
        self.ok_button.clicked.connect(self.update_layers)

    def get_layer_names(self): 
        return self.viewer.layer_manager.layers

    def get_selected_layer(self):
        name = self.layer_combo.currentText()
        for layer in self.viewer.layer_manager.layers:
            if layer == name:
                return layer
        return None

    def attiva_layer(self):
        layer = self.get_selected_layer()
        self.viewer.layer_manager.toggle_visibility(layer)
        #print(f"Layer '{layer}' attivato")

    def ripulisci_layer(self):
        layer = self.get_selected_layer()
        self.viewer.layer_manager.clear_layer(layer)
        print(f"Layer '{layer}' ripulito")
        if layer == "landmarks":
            for dati in self.viewer.landmarks.values():
                dati["coordinates"] = None
            #print(self.viewer.landmarks)
            self.viewer.landmark_combo.setCurrentIndex(0)
        self.update_layers()

    def cancella_layer(self):
        layer = self.get_selected_layer()
        self.viewer.layer_manager.delete_layer(layer)
        print(f"Layer '{layer}' cancellato")
        if layer == "landmarks":
            for dati in self.viewer.landmarks.values():
                dati["coordinates"] = None
            self.viewer.landmark_combo.setCurrentIndex(0)
        self.layer_combo.clear()
        self.layer_combo.addItems(self.get_layer_names())

    def update_layers(self):
        print("update_layers avviato")
        self.viewer.layer_manager.update_display()
        self.accept()
