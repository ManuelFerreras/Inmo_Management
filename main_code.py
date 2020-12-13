import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QDialog
from PySide2.QtCore import Slot
import threading
from PySide2.QtWidgets import QMessageBox
import datetime


import tkinter
from tkinter import filedialog
import os


from clientes_interface import Ui_MainWindow
from editar_clientes_interface import Ui_Dialog

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

index_seleccionado = 0

clientes = []
PATH_DATABASE = "Database/administraciones.mdb"

cambios = []
facturas = []
url = []

DRIVER_NAME = "Microsoft Access Driver (*.mdb)"

class Dialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__()
        self.ui = Ui_Dialog()
        self.setupUi(self)

        self.btn_exit.clicked.connect(self.salir)
        self.btn_volver.clicked.connect(self.volver)
        self.btn_aplicar.clicked.connect(self.aplicar)
        self.btn_aplicar_volver.clicked.connect(self.aplicar_volver)
        self.cb_seleccionar_cliente.currentIndexChanged.connect(self.cambiar_seleccion)

        self.de_inicio_contrato.setDate(clientes[1][6])
        self.de_final_contrato.setDate(clientes[1][6])

        self.cb_seleccionar_cliente.model().item(0).setEnabled(False)
        self.le_id.setEnabled(False)
        self.cargar_clientes()

    def mostrar_dialog(self, mensaje, titulo):
        msg = QMessageBox.about(self, titulo, mensaje)

    def actualizar_nombres_clientes(self):
        global index_seleccionado

        index_temp = index_seleccionado

        self.cb_seleccionar_cliente.clear()
        self.cb_seleccionar_cliente.addItem("Sin Seleccion")
        self.cb_seleccionar_cliente.model().item(0).setEnabled(False)

        for i in range(len(clientes)):
            self.cb_seleccionar_cliente.addItem(clientes[i][1])

        self.cb_seleccionar_cliente.setCurrentIndex(index_temp + 1)
        index_seleccionado = index_temp
        

    def cargar_clientes(self):
        for i in range(len(clientes)):
            self.cb_seleccionar_cliente.addItem(clientes[i][1])

    def actualizar_data(self):
        self.le_nombre.setText(str(clientes[index_seleccionado][1]))
        self.le_id.setText(str(clientes[index_seleccionado][0]))
        self.le_domicilio_alquiler.setText(str(clientes[index_seleccionado][2]))
        self.le_numero_telefono.setText(str(clientes[index_seleccionado][3]))
        self.le_monto_alquiler.setText("$ " + str(clientes[index_seleccionado][4]))
        self.le_monto_deposito_numero.setText(str(clientes[index_seleccionado][5]))
        self.de_inicio_contrato.setDate(clientes[index_seleccionado][6])
        self.de_final_contrato.setDate(clientes[index_seleccionado][7])
        self.le_propietario.setText(str(clientes[index_seleccionado][8]))
        self.le_tipo_comision.setText(str(clientes[index_seleccionado][9]))
        self.le_monto_comision.setText(str(clientes[index_seleccionado][10]) + " %")
        self.le_cuota_aguas.setText(str(clientes[index_seleccionado][11]))
        self.le_importe_aguas.setText("$ " + str(clientes[index_seleccionado][12]))
        self.le_porcentual_aguas.setText(str(clientes[index_seleccionado][13]) + " %")
        self.le_quien_paga_aguas.setText(str(clientes[index_seleccionado][14]))
        self.le_cuota_de_muni.setText(str(clientes[index_seleccionado][15]))
        self.le_importe_muni.setText("$ " + str(clientes[index_seleccionado][16]))
        self.le_quien_paga_muni.setText(str(clientes[index_seleccionado][17]))
        self.le_cuota_rentas.setText(str(clientes[index_seleccionado][18]))
        self.le_importe_rentas.setText("$ " + str(clientes[index_seleccionado][19]))
        self.le_quien_paga_rentas.setText(str(clientes[index_seleccionado][20]))
        self.le_monto_unico.setText("$ " + str(clientes[index_seleccionado][21]))
        self.le_mes_expensa.setText(str(clientes[index_seleccionado][22]))
        self.le_monto_expensa.setText("$ " + str(clientes[index_seleccionado][23]))
        self.le_adicional_pagares.setText("$ " + str(clientes[index_seleccionado][24]))
        self.checkBox_2.setChecked(clientes[index_seleccionado][25])
        self.le_libre.setText(str(clientes[index_seleccionado][26]))
        self.le_codigo_catastro.setText(str(clientes[index_seleccionado][27]))
        self.le_codigo_rentas.setText(str(clientes[index_seleccionado][28]))
        self.le_codigo_aguas.setText(str(clientes[index_seleccionado][29]))
        self.le_conceptos_incluidos.setText(str(clientes[index_seleccionado][30]))
        self.checkBox.setChecked(clientes[index_seleccionado][31])
        self.le_url_aguas.setText(str(clientes[index_seleccionado][32]))

    def resetear_campos(self):
        self.cb_seleccionar_cliente.setCurrentIndex(0)
        self.le_nombre.setText("")
        self.le_id.setText("")
        self.le_domicilio_alquiler.setText("")
        self.le_numero_telefono.setText("")
        self.le_monto_alquiler.setText("")
        self.le_monto_deposito_numero.setText("")
        self.le_propietario.setText("")
        self.le_tipo_comision.setText("")
        self.le_monto_comision.setText("")
        self.le_cuota_aguas.setText("")
        self.le_importe_aguas.setText("")
        self.le_porcentual_aguas.setText("")
        self.le_quien_paga_aguas.setText("")
        self.le_cuota_de_muni.setText("")
        self.le_importe_muni.setText("")
        self.le_quien_paga_muni.setText("")
        self.le_cuota_rentas.setText("")
        self.le_importe_rentas.setText("")
        self.le_quien_paga_rentas.setText("")
        self.le_monto_unico.setText("")
        self.le_mes_expensa.setText("")
        self.le_monto_expensa.setText("")
        self.le_adicional_pagares.setText("")
        self.le_libre.setText("")
        self.le_codigo_catastro.setText("")
        self.le_codigo_rentas.setText("")
        self.le_codigo_aguas.setText("")
        self.le_conceptos_incluidos.setText("")
        self.de_inicio_contrato.setDate(clientes[1][6])
        self.de_final_contrato.setDate(clientes[1][6])
        self.checkBox.setChecked(False)
        self.checkBox_2.setChecked(False)
        self.le_url_aguas.setText("")

    @Slot()
    def volver(self):
        self.volver_sin_guardar(self.cb_seleccionar_cliente.currentIndex() - 1)

    @Slot()
    def aplicar_volver(self, index):
        global index_seleccionado

        self.aplicar()
        self.volver_sin_guardar(self.cb_seleccionar_cliente.currentIndex() - 1)

    @Slot()
    def aplicar(self):
        nombre_viejo = clientes[index_seleccionado][1]

        clientes[index_seleccionado][1] = self.le_nombre.text()
        clientes[index_seleccionado][2] = self.le_domicilio_alquiler.text()
        clientes[index_seleccionado][3] = self.le_numero_telefono.text()
        clientes[index_seleccionado][4] = self.le_monto_alquiler.text().replace('$ ', '')
        clientes[index_seleccionado][5] = self.le_monto_deposito_numero.text()
        clientes[index_seleccionado][6] = self.de_inicio_contrato.date()
        clientes[index_seleccionado][7] = self.de_final_contrato.date()
        clientes[index_seleccionado][8] = self.le_propietario.text()
        clientes[index_seleccionado][9] = self.le_tipo_comision.text()
        clientes[index_seleccionado][10] = self.le_monto_comision.text().replace(' %', '')
        clientes[index_seleccionado][11] = self.le_cuota_aguas.text()
        clientes[index_seleccionado][12] = self.le_importe_aguas.text().replace('$ ', '')
        clientes[index_seleccionado][13] = self.le_porcentual_aguas.text().replace(' %', '')
        clientes[index_seleccionado][14] = self.le_quien_paga_aguas.text()
        clientes[index_seleccionado][15] = self.le_cuota_de_muni.text()
        clientes[index_seleccionado][16] = self.le_importe_muni.text().replace('$ ', '')
        clientes[index_seleccionado][17] = self.le_quien_paga_muni.text()
        clientes[index_seleccionado][18] = self.le_cuota_rentas.text()
        clientes[index_seleccionado][19] = self.le_importe_rentas.text().replace('$ ', '')
        clientes[index_seleccionado][20] = self.le_quien_paga_rentas.text()
        clientes[index_seleccionado][21] = self.le_monto_unico.text().replace('$ ', '')
        clientes[index_seleccionado][22] = self.le_mes_expensa.text()
        clientes[index_seleccionado][23] = self.le_monto_expensa.text().replace('$ ', '')
        clientes[index_seleccionado][24] = self.le_adicional_pagares.text().replace('$ ', '')
        clientes[index_seleccionado][25] = self.checkBox_2.isChecked()
        clientes[index_seleccionado][26] = self.le_libre.text()
        clientes[index_seleccionado][27] = self.le_codigo_catastro.text()
        clientes[index_seleccionado][28] = self.le_codigo_rentas.text()
        clientes[index_seleccionado][29] = self.le_codigo_aguas.text()
        clientes[index_seleccionado][30] = self.le_conceptos_incluidos.text()
        clientes[index_seleccionado][31] = self.checkBox.isChecked()
        clientes[index_seleccionado][32] = self.le_url_aguas.text()

        fecha_inicio = datetime.datetime(clientes[index_seleccionado][6].year(), clientes[index_seleccionado][6].month(), clientes[index_seleccionado][6].day())
        fecha_final = datetime.datetime(clientes[index_seleccionado][7].year(), clientes[index_seleccionado][7].month(), clientes[index_seleccionado][7].day())

        cursor.execute("UPDATE [Inquilinos] SET [Inquilino] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][1], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Domicilio_alquiler] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][2], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Numero_telefono] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][3], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Monto_Alquiler] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][4], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Monto_deposito_numero] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][5], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Fecha_inicio_contrato] = ? WHERE [Inquilino] = ?", fecha_inicio, clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Fecha_fin_contrato] = ? WHERE [Inquilino] = ?", fecha_final, clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Propietario] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][8], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Tipo_comision] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][9], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Monto_comision] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][10], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Aguas_cuota] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][11], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Aguas_Importe] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][12], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Porcentual_agua_e_imp] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][13], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Quien_paga_Agua] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][14], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Muni_Cuota] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][15], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Muni_Importe] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][16], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Quien_paga_Muni] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][17], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Rentas_cuota] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][18], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Rentas_Importe] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][19], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Quien_paga_rentas] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][20], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Monto_unico_agua_e_imp] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][21], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Mes_Expensa] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][22], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Monto_Expensa] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][23], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Adicional_pagares] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][24], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Cuenta_y_orden] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][25], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Libre] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][26], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [catastro] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][27], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [rentas] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][28], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Aguas_cordobesas] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][29], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [conceptos_incluidos] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][30], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [Paga_x_transf] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][31], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [URL_Aguas_Cbesas] = ? WHERE [Inquilino] = ?", clientes[index_seleccionado][32], clientes[index_seleccionado][0])

        conn.commit()

        self.actualizar_nombres_clientes()

        self.mostrar_dialog("Se aplicaron correctamente los cambios.", "Cambios Aplicados")


    @Slot()
    def cambiar_seleccion(self):
        global index_seleccionado
        index_seleccionado = self.cb_seleccionar_cliente.currentIndex() - 1
        print(index_seleccionado)
        self.actualizar_data()

    @Slot()
    def volver_sin_guardar(self, index):
        dialog.hide()
        self.resetear_campos()
        window.actualizar_nombres_clientes(index)
        window.show()

    @Slot()
    def salir(self):
        sys.exit(app.exec_())

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_exit.clicked.connect(self.salir)
        self.ui.cb_seleccionar_cliente.currentIndexChanged.connect(self.cambiar_seleccion)
        self.ui.btn_actualizar_aguas_cordobesas.clicked.connect(self.activar_extraer_info)
        self.ui.btn_actualizar_agua_todos.clicked.connect(self.actualizar_aguas_de_todos)
        self.ui.btn_editar_cliente.clicked.connect(self.abrir_editar)

        self.ui.cb_seleccionar_cliente.model().item(0).setEnabled(False)

        self.ui.btn_actualizar_aguas_cordobesas.setEnabled(False)
        self.conectar_access()       

    @Slot()
    def abrir_editar(self):
        window.hide()
        dialog.show()
        dialog.cb_seleccionar_cliente.setCurrentIndex(self.ui.cb_seleccionar_cliente.currentIndex())
        dialog.actualizar_data()

    @Slot()
    def cambiar_seleccion(self):
        self.ui.btn_actualizar_aguas_cordobesas.setEnabled(True)
        self.ui.le_periodo_a_buscar.setEnabled(True)
        global index_seleccionado
        index_seleccionado = self.ui.cb_seleccionar_cliente.currentIndex() - 1
        print(index_seleccionado)
        self.actualizar_data()

    def actualizar_nombres_clientes(self, index_temp):
        global index_seleccionado

        print("El index seleccionado es: ", index_temp)

        self.ui.cb_seleccionar_cliente.clear()
        self.ui.cb_seleccionar_cliente.addItem("Sin Seleccion")
        self.ui.cb_seleccionar_cliente.model().item(0).setEnabled(False)

        for i in range(len(clientes)):
            self.ui.cb_seleccionar_cliente.addItem(clientes[i][1])

        self.ui.cb_seleccionar_cliente.setCurrentIndex(index_temp + 1)
        index_seleccionado = index_temp

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
            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(True)
        else:
            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(False)

    @Slot()
    def activar_extraer_info(self):
        thread = threading.Thread(target = self.extraer_info_un_cliente, daemon=True)
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
        



    def extraer_info_un_cliente(self):
        if self.ui.le_periodo_a_buscar.text() != "":
            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(False)
            self.ui.btn_actualizar_agua_todos.setEnabled(False)
            self.ui.le_periodo_a_buscar.setEnabled(False)
             
            periodo_deseado = int(self.ui.le_periodo_a_buscar.text())
            driver = webdriver.Chrome()

            global index_seleccionado
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


            driver.close()

            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(True)
            self.ui.le_periodo_a_buscar.setEnabled(True)
            self.ui.btn_actualizar_agua_todos.setEnabled(True)

    @Slot()
    def actualizar_aguas_de_todos(self):
        if self.ui.le_periodo_a_buscar.text() != "":
            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(False)
            self.ui.btn_actualizar_agua_todos.setEnabled(False)
            self.ui.le_periodo_a_buscar.setEnabled(False)

            periodo_deseado = int(self.ui.le_periodo_a_buscar.text())
            driver = webdriver.Chrome()
            i = -1
            for row in clientes:
                i = i + 1
                if row[11] != None and row[32] != None:
                    url = row[32]

                    try:
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

                        clientes[i][12] = text[8]
                        clientes[i][11] = periodo[0]
                        cursor.execute("UPDATE [Inquilinos] SET [Aguas_Importe] = ?, [Aguas_cuota] = ? WHERE [URL_Aguas_Cbesas] = ?", text[8], periodo[0], url)
                        self.actualizar_data()
                        conn.commit()

                    except:
                        print('Error con el cliente')
                        cursor.execute("UPDATE [Inquilinos] SET [Aguas_Importe] = ?, [Aguas_cuota] = ? WHERE [URL_Aguas_Cbesas] = ?", "0", periodo_deseado, url)

            driver.close()
            print("Se ha completado la actualizacion")

            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(True)
            self.ui.le_periodo_a_buscar.setEnabled(True)
            self.ui.btn_actualizar_agua_todos.setEnabled(True)

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
    dialog = Dialog()
    window.show()

    sys.exit(app.exec_())
