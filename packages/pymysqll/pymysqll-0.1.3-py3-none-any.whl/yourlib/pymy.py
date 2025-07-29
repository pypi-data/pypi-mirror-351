import sys
import pymysql
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QLabel, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt

class MaterialRequestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Заявки на материалы")
        self.resize(800, 400)

        self.db = pymysql.connect(
            host="localhost",
            user="root",
            password="",  # Замените на ваш пароль
            database="furniture_factory",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Артикул (ID)", "Материал", "Кол-во", "Дата"])
        self.layout.addWidget(self.table)

        # Форма добавления/редактирования
        form_layout = QHBoxLayout()
        self.product_cb = QComboBox()
        self.material_cb = QComboBox()
        self.quantity_sb = QSpinBox()
        self.quantity_sb.setMinimum(1)
        form_layout.addWidget(QLabel("Продукт:"))
        form_layout.addWidget(self.product_cb)
        form_layout.addWidget(QLabel("Материал:"))
        form_layout.addWidget(self.material_cb)
        form_layout.addWidget(QLabel("Кол-во:"))
        form_layout.addWidget(self.quantity_sb)
        self.layout.addLayout(form_layout)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.update_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(btn_layout)

        self.load_data()
        self.load_comboboxes()

        # Сигналы
        self.add_btn.clicked.connect(self.add_request)
        self.update_btn.clicked.connect(self.update_request)
        self.delete_btn.clicked.connect(self.delete_request)
        self.table.itemSelectionChanged.connect(self.fill_form_from_selection)

    def load_data(self):
        self.table.setRowCount(0)
        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT mr.id, p.id AS product_id, m.name AS material, mr.quantity, mr.created_at
                FROM material_requests mr
                JOIN products p ON mr.product_id = p.id
                JOIN materials m ON mr.material_id = m.id
            """)
            for row_data in cursor.fetchall():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(row_data["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(str(row_data["product_id"])))
                self.table.setItem(row, 2, QTableWidgetItem(row_data["material"]))
                self.table.setItem(row, 3, QTableWidgetItem(str(row_data["quantity"])))
                self.table.setItem(row, 4, QTableWidgetItem(str(row_data["created_at"])))

    def load_comboboxes(self):
        self.product_cb.clear()
        self.material_cb.clear()
        with self.db.cursor() as cursor:
            cursor.execute("SELECT id, name FROM products")
            self.products = {f"{row['id']} - {row['name']}": row["id"] for row in cursor.fetchall()}
            self.product_cb.addItems(self.products.keys())

            cursor.execute("SELECT id, name FROM materials")
            self.materials = {row["name"]: row["id"] for row in cursor.fetchall()}
            self.material_cb.addItems(self.materials.keys())

    def add_request(self):
        product_id = self.products.get(self.product_cb.currentText())
        material_id = self.materials.get(self.material_cb.currentText())
        quantity = self.quantity_sb.value()
        with self.db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO material_requests (product_id, material_id, quantity)
                VALUES (%s, %s, %s)
            """, (product_id, material_id, quantity))
        self.db.commit()
        self.load_data()

    def update_request(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для редактирования.")
            return

        request_id = int(self.table.item(selected, 0).text())
        product_id = self.products.get(self.product_cb.currentText())
        material_id = self.materials.get(self.material_cb.currentText())
        quantity = self.quantity_sb.value()

        with self.db.cursor() as cursor:
            cursor.execute("""
                UPDATE material_requests
                SET product_id=%s, material_id=%s, quantity=%s
                WHERE id=%s
            """, (product_id, material_id, quantity, request_id))
        self.db.commit()
        self.load_data()

    def delete_request(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления.")
            return
        request_id = int(self.table.item(selected, 0).text())
        reply = QMessageBox.question(self, "Подтверждение", "Удалить заявку?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            with self.db.cursor() as cursor:
                cursor.execute("DELETE FROM material_requests WHERE id=%s", (request_id,))
            self.db.commit()
            self.load_data()

    def fill_form_from_selection(self):
        selected = self.table.currentRow()
        if selected == -1:
            return
        product_id = self.table.item(selected, 1).text()
        material_name = self.table.item(selected, 2).text()
        quantity = int(self.table.item(selected, 3).text())

        for key, val in self.products.items():
            if str(val) == product_id:
                self.product_cb.setCurrentText(key)
                break
        self.material_cb.setCurrentText(material_name)
        self.quantity_sb.setValue(quantity)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MaterialRequestApp()
    window.show()
    sys.exit(app.exec())



"""CREATE DATABASE IF NOT EXISTS furniture_factory DEFAULT CHARACTER SET utf8mb4;
USE furniture_factory;

-- Типы продукции
CREATE TABLE product_types (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE
);

-- Материалы
CREATE TABLE materials (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(120) NOT NULL UNIQUE
);

-- Продукция
CREATE TABLE products (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    type_id       INT NOT NULL,
    name          VARCHAR(180) NOT NULL,
    main_material INT NOT NULL,
    param_a       DECIMAL(10,3) NOT NULL,
    param_b       DECIMAL(10,3) NOT NULL,
    image_path    VARCHAR(255),
    FOREIGN KEY (type_id) REFERENCES product_types(id),
    FOREIGN KEY (main_material) REFERENCES materials(id)
);

-- Заявки на сырьё
CREATE TABLE material_requests (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    product_id   INT NOT NULL,
    material_id  INT NOT NULL,
    quantity     INT NOT NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id)  REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
);"""