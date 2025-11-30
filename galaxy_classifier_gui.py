import sys
import json
import h5py
from pathlib import Path
import tensorflow as tf
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog,
    QVBoxLayout, QMessageBox
)
from PySide6.QtGui import (
    QFont, QPixmap, QImage, QBrush, QPalette
)
from PySide6.QtCore import Qt, Slot, QTimer, QPropertyAnimation


MODEL_PATH = Path("model.h5")
IMG_SIZE = (224, 224)
BACKGROUND_IMAGE = Path("no.jpg")


def pixmap_to_tensor(pixmap: QPixmap) -> tf.Tensor:
    img = pixmap.toImage().convertToFormat(QImage.Format_RGB888)
    w, h = img.width(), img.height()
    bits = img.constBits()
    raw = bytes(bits.asstring()) if hasattr(bits, "asstring") else bytes(bits)
    arr = tf.io.decode_raw(raw, tf.uint8)
    arr = tf.reshape(arr, (h, w, 3))
    tensor = tf.image.resize(arr, IMG_SIZE)
    tensor = tf.cast(tensor, tf.float32)
    tensor = tf.keras.applications.efficientnet.preprocess_input(tensor)
    return tf.expand_dims(tensor, axis=0)


class GalaxyClassifier(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galaxy Classifier")
        self.setMinimumSize(480, 620)
        self.model = None
        self.class_names = []
        self.current_pixmap = None
        self.anim = None
        self.init_ui()
        self.load_model_async()
        self.start_fade_in()

    def init_ui(self):
        font = QFont("Segoe UI", 10)
        font.setWeight(QFont.Medium)
        QApplication.instance().setFont(font)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)
        layout.setContentsMargins(44, 44, 44, 44)

        title = QLabel("GALAXY CLASSIFIER")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #e0d4ff; letter-spacing: 1px;")
        layout.addWidget(title)

        self.upload_label = QLabel("Click to upload galaxy image")
        self.upload_label.setAlignment(Qt.AlignCenter)
        self.upload_label.setFixedSize(320, 160)
        self.upload_label.setStyleSheet("""
            border: 2.5px dashed #8a7bff; border-radius: 20px; padding: 30px;
            background: rgba(0, 0, 0, 0.5); color: #e0d4ff; font-size: 16px; font-weight: 600;
        """)
        self.upload_label.setCursor(Qt.PointingHandCursor)
        self.upload_label.mousePressEvent = self.browse_image
        layout.addWidget(self.upload_label, alignment=Qt.AlignCenter)

        self.predict_btn = QPushButton("PREDICT")
        self.predict_btn.setFixedWidth(180)
        self.predict_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7b6bff, stop:1 #5e4bff);
                color: white; border: none; border-radius: 28px; padding: 14px 0;
                font-size: 16px; font-weight: 700; letter-spacing: 1px;
            }
            QPushButton:disabled { background: #444; }
            QPushButton:hover:!pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8a7bff, stop:1 #6b5bff);
            }
        """)
        self.predict_btn.clicked.connect(self.predict)
        self.predict_btn.setEnabled(False)
        layout.addWidget(self.predict_btn, alignment=Qt.AlignCenter)

        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("""
            background: rgba(0, 0, 0, 0.6); color: #d9d9ff; font-size: 17px; font-weight: 600;
            min-height: 36px; border-radius: 12px; padding: 12px; margin: 8px;
        """)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label, alignment=Qt.AlignCenter)

        self.apply_background()

    def apply_background(self):
        if BACKGROUND_IMAGE.exists():
            bg = QPixmap(str(BACKGROUND_IMAGE)).scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            pal = self.palette()
            pal.setBrush(self.backgroundRole(), QBrush(bg))
            self.setPalette(pal)
            self.setAutoFillBackground(True)
            self.setStyleSheet("QWidget { color: #e0d4ff; } QLabel, QPushButton { background: rgba(0,0,0,0.5); border-radius: 12px; padding: 8px; }")
        else:
            self.setStyleSheet("QWidget { background: qradialgradient(cx:0.5, cy:0, radius:1.4, stop:0 #1a1a2e, stop:1 #0a0a1a); color: #e0d4ff; }")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_background()

    def start_fade_in(self):
        self.setWindowOpacity(0)
        self.show()
        self.raise_()
        self.activateWindow()
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(900)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

    def load_model_async(self):
        self.result_label.setText("Loading model… Please wait.")

        @Slot()
        def _load():
            try:
                if not MODEL_PATH.exists():
                    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

                def swish(x): return x * tf.nn.sigmoid(x)
                from tensorflow.keras.layers import Layer

                class Cast(Layer):
                    def __init__(self, dtype, **kwargs):
                        super().__init__(dtype=dtype, **kwargs)
                    def call(self, inputs):
                        return tf.cast(inputs, self.dtype)

                with tf.keras.utils.custom_object_scope({'swish': tf.keras.layers.Activation(swish), 'Cast': Cast}):
                    self.model = tf.keras.models.load_model(str(MODEL_PATH), compile=False)

                with h5py.File(MODEL_PATH, "r") as f:
                    self.class_names = json.loads(f.attrs["class_names"])

                self.result_label.setText("Model loaded")
                self.predict_btn.setEnabled(True)
            except Exception as e:
                import traceback
                print("LOAD ERROR:\n", traceback.format_exc())
                self.result_label.setText("Load failed.")
                QMessageBox.critical(self, "Error", str(e))

        QTimer.singleShot(200, _load)

    def browse_image(self, event=None):
        file, _ = QFileDialog.getOpenFileName(self, "Select Galaxy Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if not file:
            return
        pix = QPixmap(file)
        if pix.isNull():
            QMessageBox.warning(self, "Invalid", "Could not load image.")
            return
        thumb = pix.scaled(300, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.upload_label.setPixmap(thumb)
        self.upload_label.setText("")
        self.current_pixmap = pix
        self.result_label.clear()

    def predict(self):
        if not self.model or not self.current_pixmap:
            return
        self.result_label.setText("Analyzing galaxy…")
        self.predict_btn.setEnabled(False)
        try:
            tensor = pixmap_to_tensor(self.current_pixmap)
            pred = self.model.predict(tensor, verbose=0)[0]
            idx = int(tf.argmax(pred))
            conf = float(pred[idx]) * 100

            
            UNKNOWN_THRESHOLD = 30.0  

            if conf < UNKNOWN_THRESHOLD:
                self.result_label.setText(
                    "<b style='font-size:18px; color:#ff7070'>Unknown Object</b><br>"
                    "<font color='#a0a0ff'>Not identified as a known galaxy type</font>"
                )
            else:
                self.result_label.setText(
                    f"<b style='font-size:18px'>{self.class_names[idx]}</b><br>"
                    f"<font color='#a0a0ff'>Confidence: {conf:.2f}%</font>"
                )

        except Exception as e:
            self.result_label.setText(f"Error: {e}")
            print("PREDICTION ERROR:", e)
        finally:
            self.predict_btn.setEnabled(True)

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = GalaxyClassifier()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
