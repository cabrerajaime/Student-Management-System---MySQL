import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLineEdit, QPushButton, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, \
    QStatusBar, QGridLayout, QLabel, QMessageBox

import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(500, 600)

        # Ítems que conforman el menu de la ventana principal
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        search_menu_item = self.menuBar().addMenu("&Search")

        # Añadir acciones a los ítems que conforman el menu
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        # Se llama al método insert
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        # QIcon() permite agregar iconos a nuestras acciones
        search_action = QAction(QIcon("icons/search.png"), "Search", self)
        search_action.triggered.connect(self.search)
        search_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ("Id", "Name", "Course", "Mobile"))
        # Quitar visibilidad a los indices verticales de la tabla
        self.table.verticalHeader().setVisible(False)
        # Mostrar la tabla en la ventana principal de la GUI
        self.setCentralWidget(self.table)

        # Creación de barra de herramientas y agregar elementos
        toolbar = QToolBar()
        # Permite que la barra de herramientas pueda moverse de posición
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Creación de barra de estado de elementos
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detectar el clic sobre ua celda
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Implementación para evitar que los botones Edit y Record se acumulen cada
        # vez que se selecciona una celda

        # findChildren retorna una lista de los objetos de QPushBotton
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                # Remover cada uno de esos objetos
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
        #  Ese método reinicia la tabla y toma los datos como nuevos para evitar que se repitan.
        self.table.setRowCount(0)
        # Reservar una fila para comenzar a insertar columnas sobre ella
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            # Extraer datos columna por columna sobre fila
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(data)))
            # Termina ciclo (las columnas se han llenado), sale y se inserta otra fila
        connection.close()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()


class DeleteDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)

        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Obtener el id y el index de la fila seleccionada
        index = menu_window.table.currentRow()
        student_id = menu_window.table.item(index, 0).text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        # Se pone una coma después de student_id para que python lo
        # interprete como una tupla
        cursor.execute("DELETE from students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        menu_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


class EditDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Obtener el nombre del estudiante de acuerdo a la fila seleccionada
        index = menu_window.table.currentRow()
        student_name = menu_window.table.item(index, 1).text()

        # Obtener el id de la fila seleccionada
        self.student_id = menu_window.table.item(index, 0).text()

        # Widget para insertar estudiante
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Widget para seleccionar el curso
        course_name = menu_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Widget para agregar número de telefono
        mobile_number = menu_window.table.item(index, 3).text()
        self.mobile_number = QLineEdit(mobile_number)
        self.mobile_number.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile_number)

        # Agregar botón para enviar
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile_number.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        # Actualizar la tabla del menu principal
        menu_window.load_data()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Widget para insertar estudiante
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Widget para seleccionar el curso
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Widget para agregar número de telefono
        self.mobile_number = QLineEdit()
        self.mobile_number.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile_number)

        # Agregar botón para enviar
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile_number.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?,?,?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        # Refrescar la tabla de estudiantes en el menu principal
        menu_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        self.button = QPushButton("Search")
        self.button.clicked.connect(self.search)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        # Se buscan todas las filas que hagan match con el nombre ingresado
        items = menu_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            # item.row() representa el índice del nombre que estamos buscando
            # el segundo argumento representa la columna que vamos a resaltar
            menu_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


app = QApplication(sys.argv)
menu_window = MainWindow()
menu_window.show()
menu_window.load_data()
sys.exit(app.exec())
