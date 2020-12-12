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

clientes = []
PATH_DATABASE = "Database/administraciones.mdb"

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
        self.ui.cb_seleccionar_cliente.currentIndexChanged.connect(self.cambiar_seleccion)
        self.ui.btn_actualizar_aguas_cordobesas.clicked.connect(self.activar_extraer_info)

        self.ui.cb_seleccionar_cliente.model().item(0).setEnabled(False)

        self.ui.btn_actualizar_aguas_cordobesas.setEnabled(False)
        self.ui.le_periodo_a_buscar.setEnabled(False)
        self.conectar_access()           

    @Slot()
    def cambiar_seleccion(self):
        self.ui.btn_actualizar_aguas_cordobesas.setEnabled(True)
        self.ui.le_periodo_a_buscar.setEnabled(True)
        global index_seleccionado
        index_seleccionado = self.ui.cb_seleccionar_cliente.currentIndex() - 1
        print(index_seleccionado)
        self.actualizar_data()

    def actualizar_data(self):
        self.ui.label_id_cliente.setText(str(clientes[index_seleccionado][0]))
        self.ui.label_domicilio.setText(str(clientes[index_seleccionado][2]))
        self.ui.label_numero_de_telefono.setText(str(clientes[index_seleccionado][3]))
        self.ui.label_monto_de_alquiler.setText("$ " + str(clientes[index_seleccionado][4]))
        self.ui.label_monto_deposito_numero.setText(str(clientes[index_seleccionado][5]))
        self.ui.dateEdit.setDate(clientes[index_seleccionado][6])
        self.ui.dateEdit_2.setDate(clientes[index_seleccionado][7])
        self.ui.label_nombre_propietario.setText(str(clientes[index_seleccionado][8]))
        self.ui.label_tipo_de_comision.setText(str(clientes[index_seleccionado][9]))
        self.ui.label_monto_de_comision.setText(str(clientes[index_seleccionado][10]) + " %")
        self.ui.label_cuota_aguas_cordobesas.setText(str(clientes[index_seleccionado][11]))
        self.ui.label_importe_aguas_cordobesas.setText("$ " + str(clientes[index_seleccionado][12]))
        self.ui.label_porcentual_aguas_cordobesas.setText(str(clientes[index_seleccionado][13]) + " %")
        self.ui.label_quien_paga_aguas.setText(str(clientes[index_seleccionado][14]))
        self.ui.label_cuota_muni.setText(str(clientes[index_seleccionado][15]))
        self.ui.label_importe_muni.setText("$ " + str(clientes[index_seleccionado][16]))
        self.ui.label_quien_paga_muni.setText(str(clientes[index_seleccionado][17]))
        self.ui.label_cuota_rentas.setText(str(clientes[index_seleccionado][18]))
        self.ui.label_importe_rentas.setText("$ " + str(clientes[index_seleccionado][19]))
        self.ui.label_quien_paga_rentas.setText(str(clientes[index_seleccionado][20]))
        self.ui.label_monto_unico.setText("$ " + str(clientes[index_seleccionado][21]))
        self.ui.label_mes_expensa.setText(str(clientes[index_seleccionado][22]))
        self.ui.label_monto_expensa.setText("$ " + str(clientes[index_seleccionado][23]))
        self.ui.label_adicional_pagares.setText("$ " + str(clientes[index_seleccionado][24]))

        if clientes[index_seleccionado][25] == False:
            self.ui.label_cuenta_orden.setText("No")
        else:
            self.ui.label_cuenta_orden.setText("Si")

        self.ui.label_libre.setText(str(clientes[index_seleccionado][26]))
        self.ui.label_codigo_catastro.setText(str(clientes[index_seleccionado][27]))
        self.ui.label_codigo_rentas.setText(str(clientes[index_seleccionado][28]))
        self.ui.label_codigo_aguas_cordobesas.setText(str(clientes[index_seleccionado][29]))
        self.ui.label_conceptos_incluidos.setText(str(clientes[index_seleccionado][30]))

        if clientes[index_seleccionado][31] == False:
            self.ui.label_paga_por_transferencia.setText("No")
        else:
            self.ui.label_paga_por_transferencia.setText("Si")

        if clientes[index_seleccionado][11] != None and clientes[index_seleccionado][32] != None:
            self.ui.le_periodo_a_buscar.setEnabled(True)
            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(True)
        else:
            self.ui.le_periodo_a_buscar.setEnabled(False)
            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(False)
        

    @Slot()
    def activar_extraer_info(self):
        thread = threading.Thread(target = self.extraer_info, daemon=True)
        thread.start()

    @Slot()
    def conectar_access(self):
        global conn
        conn = pyodbc.connect("Driver={%s};DBQ=%s;" % (DRIVER_NAME, PATH_DATABASE))
        global cursor
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Inquilinos")
        for row in cursor.fetchall():
            clientes.append(row)
        for i in range(len(clientes)):
            self.ui.cb_seleccionar_cliente.addItem(clientes[i][1])
            print(clientes[i])
            print("\n")
        



    def extraer_info(self):
        if self.ui.le_periodo_a_buscar.text() != "":

            print("inicio")
            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(False)
            self.ui.le_periodo_a_buscar.setEnabled(False)
             
            periodo_deseado = int(self.ui.le_periodo_a_buscar.text())
            driver = webdriver.Chrome()

            global index_seleccionado
            try:
                    url = clientes[index_seleccionado][32]
                    print(url)
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

                    clientes[index_seleccionado][12] = text[8]
                    clientes[index_seleccionado][11] = periodo[0]
                    cursor.execute("UPDATE [Inquilinos] SET [Aguas_Importe] = ?, [Aguas_cuota] = ? WHERE [URL_Aguas_Cbesas] = ?", text[8], periodo[0], url)
                    print("Modificado")
                    conn.commit()
                    self.actualizar_data()
            except:
                print('Error con el cliente')
                cursor.execute("UPDATE [Inquilinos] SET [Aguas_Importe] = ?, [Aguas_cuota] = ? WHERE [URL_Aguas_Cbesas] = ?", "0", periodo_deseado, url)

            driver.close()

            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(True)
            self.ui.le_periodo_a_buscar.setEnabled(True)


        
        
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
