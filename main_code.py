import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QDialog
from PySide2.QtCore import Slot
import threading

import tkinter
from tkinter import filedialog
import os


from clientes_interface import Ui_MainWindow

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pyautogui
import json
from openpyxl import load_workbook
import os
import pyodbc

cambios = []
facturas = []
url = []

DRIVER_NAME = "Microsoft Access Driver (*.mdb)"

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_exit.clicked.connect(self.salir)


    @Slot()
    def activar_extraer_info(self):
        thread = threading.Thread(target = self.extraer_info, daemon=True)
        self.ui.btn_extraer_info.setDisabled(True)
        thread.start()

    @Slot()
    def elegir_access(self):
        root = tkinter.Tk()
        root.withdraw() #use to hide tkinter window

        global DB_PATH
        DB_PATH = search_for_file_path(root)
        print("1")
        global conn
        conn = pyodbc.connect("Driver={%s};DBQ=%s;" % (DRIVER_NAME, DB_PATH))
        global cursor
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Inquilinos")
        print("1")
        self.ui.btn_extraer_info.setDisabled(False)
        self.ui.lineEdit.setDisabled(False)
        


    

    def extraer_info(self):
        if self.ui.lineEdit.text() != "":
            periodo_deseado = int(self.ui.lineEdit.text())
            driver = webdriver.Chrome()

            for row in cursor.fetchall():
                try:
                    if row[11] != None and row[31] != None:
                        url = row[31]
                        print(row[11])
                        driver.get(url)

                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sUf"]')))   # Espera hasta que se cargue almenos un boton de copiar aviso en la pagina.
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="tbl-detalleDeuda"]/tbody[2]')))
                        text = driver.find_element_by_xpath('//*[@id="tbl-detalleDeuda"]/tbody[2]').text
                        codigo = driver.find_element_by_xpath('//*[@id="sUf"]').text
                        
                        text = text.split()

                        while len(text) > 10:
                            comprobacion = text[1].split('/')
                            if int(comprobacion[0]) == periodo_deseado:
                                break
                            del text[0:10]
                        
                            
                        text[8] = text[8].replace(",", ".")

                        print(text)

                        periodo = text[1].split('/')
                        cursor.execute("UPDATE [Inquilinos] SET [Aguas_Importe] = ?, [Aguas_cuota] = ? WHERE [URL_Aguas_Cbesas] = ?", text[8], periodo[0], url)
                        print("Modificado")
                        conn.commit()
                except:
                    print('Error con el cliente')
                    cursor.execute("UPDATE [Inquilinos] SET [Aguas_Importe] = ?, [Aguas_cuota] = ? WHERE [URL_Aguas_Cbesas] = ?", "0", periodo_deseado, url)

            driver.close()
            print("Se ha completado la actualizacion")

            self.ui.btn_extraer_info.setDisabled(False)


        
        
    @Slot()
    def look_for_url(self):
        if self.ui.lineEdit_2.text() != "":
            self.ui.lineEdit_2.setText("")

            urls = []
        
            with open('urls.txt') as json_file:
                urls = json.load(json_file)
                
            driver = webdriver.Chrome()
            codigo = self.ui.lineEdit_2.text()

            driver.get('https://www.aguascordobesas.com.ar/espacioClientes/')

            sleep(2)

            driver.find_element_by_xpath('//*[@id="modal-impactoEspacioClientes"]/div/div/div/button').click()
            driver.find_element_by_xpath('//*[@id="consulta-deuda"]').click()

            sleep(2)

            pyautogui.click(221, 636) # Unidad de facturacion
            pyautogui.typewrite(codigo, interval=0.1)

            element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, '//*[@id="frmInitConsultaDeuda"]/div')))

            urls.append(driver.current_url)
            print(driver.current_url)

            with open('urls.txt', 'w') as f:
                json.dump(urls, f)

            driver.close()

	
    @Slot()
    def actualizar_clientes(self):
        new_inquilinos = []
        inquilinos2 = []

        FILE_PATH = 'inquilinos2.xlsx'
        SHEET = 'consulta BD'

        workbook = load_workbook(FILE_PATH, read_only=True)
        sheet = workbook[SHEET]

        for row in sheet.iter_rows(min_row=2):
                if row[13].value != None:
                        inquilinos2.append(row[1].value)

        inquilinos1 = []

        FILE_PATH2 = 'inquilinos.xlsx'
        SHEET2 = 'Copia_de_Inquilinos'

        workbook2 = load_workbook(FILE_PATH2, read_only=False)
        sheet2 = workbook2[SHEET2]

        for row in sheet.iter_rows(min_row=2):
                if row[13].value != None:
                        inquilinos1.append(row[1].value)

        for i in range(len(inquilinos2)):
                if not inquilinos2[i] in inquilinos1:
                        new_inquilinos.append(inquilinos2[i])

        print(new_inquilinos)

    @Slot()
    def salir(self):
        sys.exit(app.exec_())

def search_for_file_path(root):
    currdir = os.getcwd()
    tempdir = filedialog.askopenfilename(parent=root, initialdir=currdir, title='Porfavor, eliga el archivo access', filetypes = [("Access Database File", "*.mdb")])

    return tempdir    




        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
