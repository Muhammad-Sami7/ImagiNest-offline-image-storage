import sys, os, json, uuid, time, requests, mimetypes
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QFileDialog, QMessageBox, QCompleter
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from PIL import Image

# === CouchDB Config ===
COUCHDB_USER = 'user_name' # Write User name here
COUCHDB_PASS = 'password'# write password of your database here
COUCHDB_NAME = 'database_name' #write database name here
COUCHDB_URL = f'http://{COUCHDB_USER}:{COUCHDB_PASS}@127.0.0.1:5984/{COUCHDB_NAME}'

class ImagiNestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 ImagiNest")
        self.setFixedSize(580, 640)
        self.setStyleSheet("""
            QWidget { background-color: #f9f4ff; font-family: Segoe UI; }
            QLabel { font-size: 15px; font-weight: bold; color: #333; }
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                background-color: #ffffff;
                border-radius: 6px;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #7b2cbf;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5a189a;
            }
        """)
        self.metadata = self.fetch_metadata()
        self.image_path = None
        self.build_ui()

    def fetch_metadata(self):
        try:
            types = requests.get(f"{COUCHDB_URL}/metadata_image_types", auth=(COUCHDB_USER, COUCHDB_PASS)).json()["data"]
            resolutions = requests.get(f"{COUCHDB_URL}/metadata_image_resolutions", auth=(COUCHDB_USER, COUCHDB_PASS)).json()["data"]
            classes = requests.get(f"{COUCHDB_URL}/metadata_image_classes", auth=(COUCHDB_USER, COUCHDB_PASS)).json()["data"]
            return {"types": types, "res": resolutions, "classes": classes}
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to load metadata.\n{str(e)}")
            return {"types": [], "res": [], "classes": []}

    def build_ui(self):
        layout = QVBoxLayout()

        title = QLabel("🧠 ImagiNest")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.type_input = self.create_input("Image Type", [t["name"] for t in self.metadata["types"]])
        layout.addLayout(self.type_input[1])

        self.res_input = self.create_input("Resolution", [r["resolution"] for r in self.metadata["res"]])
        layout.addLayout(self.res_input[1])

        self.class_input = self.create_input("Image Class", [c["name"] for c in self.metadata["classes"]])
        layout.addLayout(self.class_input[1])

        self.image_label = QLabel("📸 No Image Selected")
        self.image_label.setStyleSheet("border: 1px dashed gray; padding: 10px;")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.preview = QLabel()
        self.preview.setFixedSize(300, 200)
        self.preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview, alignment=Qt.AlignCenter)

        browse_btn = QPushButton("📁 Browse Image")
        browse_btn.clicked.connect(self.browse_image)
        layout.addWidget(browse_btn)

        upload_btn = QPushButton("⬆️ Upload to CouchDB")
        upload_btn.clicked.connect(self.upload_to_db)
        layout.addWidget(upload_btn)

        self.setLayout(layout)

    def create_input(self, label_text, items):
        layout = QVBoxLayout()
        label = QLabel(label_text)
        input_field = QLineEdit()
        completer = QCompleter(items)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        input_field.setCompleter(completer)
        layout.addWidget(label)
        layout.addWidget(input_field)
        return input_field, layout

    def browse_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.gif *.bmp)")
        if file_name:
            self.image_path = file_name
            self.image_label.setText(os.path.basename(file_name))
            self.preview.setPixmap(QPixmap(file_name).scaled(self.preview.size(), Qt.KeepAspectRatio))

            ext = os.path.splitext(file_name)[1].lower()
            width, height = Image.open(file_name).size
            resolution_str = f"{width}x{height}"
            filename_lower = os.path.basename(file_name).lower()

            img_type = self.get_image_type_from_extension(ext)
            resolution = self.get_resolution_from_dimensions(resolution_str)
            img_class = self.get_class_from_filename(filename_lower)

            self.type_input[0].setText(img_type or "")
            self.res_input[0].setText(resolution or "")
            self.class_input[0].setText(img_class or "")

            missing = []
            if not img_type: missing.append("Image Type")
            if not resolution: missing.append("Resolution")
            if not img_class: missing.append("Image Class")

            if missing:
                QMessageBox.information(
                    self, "Partial Metadata Found",
                    f"⚠️ Could not auto-detect:\n" + "\n".join(missing) +
                    "\n\nPlease fill in these fields manually."
                )

    def get_image_type_from_extension(self, ext):
        for t in self.metadata["types"]:
            if t["extension"].lower() == ext:
                return t["name"]
        return None

    def get_resolution_from_dimensions(self, res_str):
        for r in self.metadata["res"]:
            if r["resolution"] == res_str:
                return r["resolution"]
        try:
            w, h = map(int, res_str.split('x'))
            for r in self.metadata["res"]:
                rw, rh = map(int, r["resolution"].split('x'))
                if abs(w - rw) <= 2 and abs(h - rh) <= 2:
                    return r["resolution"]
        except:
            pass
        return None

    def get_class_from_filename(self, filename):
        tokens = set(os.path.splitext(filename)[0].lower().replace("-", " ").replace("_", " ").split())
        best_match = None
        best_score = 0

        for c in self.metadata["classes"]:
            keywords = set(k.lower() for k in c.get("keywords", []))
            score = len(tokens.intersection(keywords))
            if score > best_score:
                best_score = score
                best_match = c["name"]

        return best_match if best_score > 0 else None

    def get_id(self, category, name):
        data = self.metadata.get(category, [])
        for item in data:
            if category == "types" and item.get("name", "").lower() == name.lower():
                return str(item.get("type_id")).zfill(2)
            elif category == "res" and item.get("resolution", "").lower() == name.lower():
                return str(item.get("resolution_id")).zfill(2)
            elif category == "classes" and item.get("name", "").lower() == name.lower():
                return str(item.get("class_id")).zfill(3)
        return "00"

    def upload_to_db(self):
        if not self.image_path:
            QMessageBox.warning(self, "Missing Image", "Please select an image first.")
            return

        img_type = self.type_input[0].text().strip()
        resolution = self.res_input[0].text().strip()
        img_class = self.class_input[0].text().strip()

        if not img_type or not resolution or not img_class:
            QMessageBox.warning(self, "Missing Fields", "Please fill in all fields.")
            return

        type_id = self.get_id("types", img_type)
        res_id = self.get_id("res", resolution)
        class_id = self.get_id("classes", img_class)

        ext = os.path.splitext(self.image_path)[1].lstrip(".")
        mime_type = mimetypes.guess_type(self.image_path)[0] or f"image/{ext}"
        timestamp = str(int(time.time()))
        short_uuid = uuid.uuid4().hex[:4]
        unique_id = f"{type_id}_{res_id}_{class_id}_{timestamp}_{short_uuid}.{ext}"

        doc = {
            "_id": unique_id,
            "image_type": img_type,
            "resolution": resolution,
            "image_class": img_class
        }

        try:
            doc_resp = requests.put(f"{COUCHDB_URL}/{unique_id}", json=doc, auth=(COUCHDB_USER, COUCHDB_PASS))
            rev = doc_resp.json().get("rev")

            with open(self.image_path, "rb") as f:
                image_data = f.read()

            img_resp = requests.put(
                f"{COUCHDB_URL}/{unique_id}/image?rev={rev}",
                data=image_data,
                headers={"Content-Type": mime_type},
                auth=(COUCHDB_USER, COUCHDB_PASS)
            )

            if img_resp.status_code in [201, 202]:
                QMessageBox.information(self, "Success", f"✅ Image uploaded as:\n{unique_id}")
                self.reset_ui()
            else:
                QMessageBox.critical(self, "Upload Failed", f"❌ Upload error:\n{img_resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def reset_ui(self):
        self.type_input[0].clear()
        self.res_input[0].clear()
        self.class_input[0].clear()
        self.image_label.setText("📸 No Image Selected")
        self.preview.clear()
        self.image_path = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ImagiNestApp()
    win.show()
    sys.exit(app.exec_())
