''' IMPORTS '''
import sys
import threading
import datetime
import tkinter
import os
from time import sleep
import pyautogui
import json
import os
import pyodbc
from openpyxl import load_workbook
from tkinter import filedialog

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PySide2.QtWidgets import QApplication, QMainWindow, QDialog, QMessageBox
from PySide2.QtCore import Slot

from clientes_interface import Ui_MainWindow
from editar_clientes_interface import Ui_Dialog


''' DECLARACIÓN DE VARIABLES GLOBALES '''
index_seleccionado = 0   # Sirve para saber qué cliente estamos viendo actualmente.

clientes = []   # Sirve para almacenar los clientes cargados de la base de datos.
url = []   # Sirve para almacenar la url de aguas cordobesas de un cliente.

PATH_DATABASE = "Database/administraciones.mdb"   # Ubicación de la base de datos.
DRIVER_NAME = "Microsoft Access Driver (*.mdb)"   # Driver utilizado para leer la base de datos.


''' PROGRAMA '''
class Dialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__()
        self.ui = Ui_Dialog()
        self.setupUi(self)
        # Hago que no se le pueda modificar el tamaño a la ventana.
        self.setFixedSize(self.size())

        self.btn_exit.clicked.connect(self.salir)
        self.btn_volver.clicked.connect(self.volver)
        self.btn_aplicar.clicked.connect(self.aplicar)
        self.btn_buscar_url.clicked.connect(self.buscar_url)
        self.btn_aplicar_volver.clicked.connect(self.aplicar_volver)
        self.cb_seleccionar_cliente.currentIndexChanged.connect(self.cambiar_seleccion)

        # Seteo una fecha default para los dateEdits.
        self.de_inicio_contrato.setDate(clientes[1][6])   
        self.de_final_contrato.setDate(clientes[1][6])

        # Deshabilito la primera opción "Sin Selección" del comboBox.
        self.cb_seleccionar_cliente.model().item(0).setEnabled(False)

        # Deshabilito el lineEdit del ID del cliente para que no sea modificable.
        self.le_id.setEnabled(False)

        # Carga los clientes desde la base de datos.
        self.cargar_clientes()

    def mostrar_dialog(self, mensaje, titulo):
        # Sirve para crear un messageBox para mostrar un aviso.
        msg = QMessageBox.about(self, titulo, mensaje)

    def actualizar_nombres_clientes(self):
        # Hace referencia a la variable global.
        global index_seleccionado

        # Utilizo esta variable para almacenar el index del cliente actualmente seleccionado
        # así posteriormente se la vuelvo a setear a index_seleccionado, el cual sufre
        # modificaciones en su valor.
        index_temp = index_seleccionado

        # Actualizo las opciones del comboBox.
        self.cb_seleccionar_cliente.clear()
        self.cb_seleccionar_cliente.addItem("Sin Seleccion")
        self.cb_seleccionar_cliente.model().item(0).setEnabled(False)
        for i in range(len(clientes)):
            self.cb_seleccionar_cliente.addItem(clientes[i][1])

        # Vuelvo a seleccionar el cliente que se estaba editando.
        self.cb_seleccionar_cliente.setCurrentIndex(index_temp + 1) # El "+ 1" lo utilizo porque el comboBox posee un item "Sin Selección" el cual no se usa, pero indice de los demás.
        index_seleccionado = index_temp
        

    def cargar_clientes(self):
        # Se cargan los clientes en el comboBox por primera vez.
        for i in range(len(clientes)):
            self.cb_seleccionar_cliente.addItem(clientes[i][1])

    def actualizar_data(self):
        # Se actualizan todos los campos con los datos del cliente seleccionado.
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
        # Se limpian todos los campos.
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
        # Este método es intermediario para poder pasarle parámetros al otro método.
        self.volver_sin_guardar(self.cb_seleccionar_cliente.currentIndex() - 1) # El "- 1" sale de que currentIndex comienza a contar de 1.

    @Slot()
    def aplicar_volver(self, index):
        # Hace referencia a la variable global.
        global index_seleccionado

        # Primero se aplican los cambios y luego se vuelve al menú.
        self.aplicar()
        self.volver_sin_guardar(self.cb_seleccionar_cliente.currentIndex() - 1)

    @Slot()
    def buscar_url(self):
        # Se fija que el cliente tenga un código de acceso a Aguas Cordobesas.
        if self.le_codigo_aguas.text() != "":
            # Se muestra un messageBox.
            self.mostrar_dialog("A continuación se abrirá un navegador.\n\n Debe esperar a que el programa ingrese el código de usuario y manualmente debe completar el captcha y apretar el botón 'CONSULTAR'.\n\n El resto lo hará el programa.", "Aviso")
                
            # Se abre un navegador en la página de Aguas Cordobesas.
            driver = webdriver.Chrome()
            codigo = self.le_codigo_aguas.text()
            driver.get('https://www.aguascordobesas.com.ar/espacioClientes/')

            sleep(2)

            # Ingresa el código de acceso del cliente.
            driver.find_element_by_xpath('//*[@id="modal-impactoEspacioClientes"]/div/div/div/button').click()
            driver.find_element_by_xpath('//*[@id="consulta-deuda"]').click()
            sleep(2)
            pyautogui.click(221, 636) # Unidad de facturacion
            pyautogui.typewrite(codigo, interval=0.1)

            # Espera a que el usuario complete el captcha, apriete en el botón y cargue la página.
            element = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, '//*[@id="frmInitConsultaDeuda"]/div')))

            # Consigue el URL de la página.
            url =driver.current_url
            print("Nuevo URL: ", driver.current_url)
            driver.close()

            # Modifica el URL del cliente.
            self.le_url_aguas.setText(url)
            self.aplicar()
            
        else:
            # Muestra un messageBox en caso de que no se haya especificado un código para el cliente.
            self.mostrar_dialog("Falta especificar el código de cliente de Aguas Cordobesas en el campo correspondiente", "Falta Código de Cliente")


    @Slot()
    def aplicar(self):
        # Se actualizan los valores en el vector de clientes.
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

        if self.le_cuota_aguas.text() != "None":
            clientes[index_seleccionado][11] = self.le_cuota_aguas.text()
        else:
            clientes[index_seleccionado][11] = None

        if self.le_importe_aguas.text().replace('$ ', '') != "None":
            clientes[index_seleccionado][12] = self.le_importe_aguas.text().replace('$ ', '')
        else:
            clientes[index_seleccionado][12] = None

        if self.le_porcentual_aguas.text().replace(' %', '') != "None":
            clientes[index_seleccionado][13] = self.le_porcentual_aguas.text().replace(' %', '')
        else:
            clientes[index_seleccionado][13] = None
 
        clientes[index_seleccionado][14] = self.le_quien_paga_aguas.text()

        if self.le_cuota_de_muni.text() != "None":
            clientes[index_seleccionado][15] = self.le_cuota_de_muni.text()
        else:
            clientes[index_seleccionado][15] = None
        
        if self.le_importe_muni.text().replace('$ ', '') != "None":
            clientes[index_seleccionado][16] = self.le_importe_muni.text().replace('$ ', '')
        else:
            clientes[index_seleccionado][16] = None

        clientes[index_seleccionado][17] = self.le_quien_paga_muni.text()

        if self.le_cuota_rentas.text() != "None":
            clientes[index_seleccionado][18] = self.le_cuota_rentas.text()
        else:
            clientes[index_seleccionado][18] = None
 
        if self.le_importe_rentas.text().replace('$ ', '') != "None":
            clientes[index_seleccionado][19] = self.le_importe_rentas.text().replace('$ ', '')
        else:
            clientes[index_seleccionado][19] = None
        
        clientes[index_seleccionado][20] = self.le_quien_paga_rentas.text()

        if self.le_monto_unico.text().replace('$ ', '') != "None":
            clientes[index_seleccionado][21] = self.le_monto_unico.text().replace('$ ', '')
        else:
            clientes[index_seleccionado][21] = None

        if self.le_mes_expensa.text() != "None":
            clientes[index_seleccionado][22] = self.le_mes_expensa.text().replace('$ ', '')
        else:
            clientes[index_seleccionado][22] = None

        if self.le_monto_expensa.text().replace('$ ', '') != "None":
            clientes[index_seleccionado][23] = self.le_monto_expensa.text().replace('$ ', '')
        else:
            clientes[index_seleccionado][23] = None

        if self.le_adicional_pagares.text().replace('$ ', '') != "None":
            clientes[index_seleccionado][24] = self.le_adicional_pagares.text().replace('$ ', '')
        else:
            clientes[index_seleccionado][24] = None

        clientes[index_seleccionado][25] = self.checkBox_2.isChecked()

        if self.le_libre.text() != "None":
            clientes[index_seleccionado][26] = self.le_libre.text()
        else:
            clientes[index_seleccionado][26] = None
        
        if self.le_codigo_catastro.text() != "None":
            clientes[index_seleccionado][27] = self.le_codigo_catastro.text()
        else:
            clientes[index_seleccionado][27] = None

        if self.le_codigo_rentas.text() != "None":
            clientes[index_seleccionado][28] = self.le_codigo_rentas.text()
        else:
            clientes[index_seleccionado][28] = None

        if self.le_codigo_aguas.text() != "None":
            clientes[index_seleccionado][29] = self.le_codigo_aguas.text()
        else:
            clientes[index_seleccionado][29] = None

        if self.le_conceptos_incluidos.text() != "None":
            clientes[index_seleccionado][30] = self.le_conceptos_incluidos.text()
        else:
            clientes[index_seleccionado][30] = None

        clientes[index_seleccionado][31] = self.checkBox.isChecked()

        if self.le_url_aguas.text() != "None":
            clientes[index_seleccionado][32] = self.le_url_aguas.text()
        else:
            clientes[index_seleccionado][32] = None

        # Se crean variables de las fechas en el formato que soporte la base de datos.
        fecha_inicio = datetime.datetime(clientes[index_seleccionado][6].year(), clientes[index_seleccionado][6].month(), clientes[index_seleccionado][6].day())
        fecha_final = datetime.datetime(clientes[index_seleccionado][7].year(), clientes[index_seleccionado][7].month(), clientes[index_seleccionado][7].day())

        # Se actualiza la base de datos.
        cursor.execute("UPDATE [Inquilinos] SET [Inquilino] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][1], clientes[index_seleccionado][0])     
        cursor.execute("UPDATE [Inquilinos] SET [Domicilio_alquiler] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][2], clientes[index_seleccionado][0])      
        cursor.execute("UPDATE [Inquilinos] SET [Numero_telefono] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][3], clientes[index_seleccionado][0])       
        cursor.execute("UPDATE [Inquilinos] SET [Monto_Alquiler] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][4], clientes[index_seleccionado][0])      
        cursor.execute("UPDATE [Inquilinos] SET [Monto_deposito_numero] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][5], clientes[index_seleccionado][0])      
        cursor.execute("UPDATE [Inquilinos] SET [Fecha_inicio_contrato] = ? WHERE [Inquilino_id] = ?", fecha_inicio, clientes[index_seleccionado][0])      
        cursor.execute("UPDATE [Inquilinos] SET [Fecha_fin_contrato] = ? WHERE [Inquilino_id] = ?", fecha_final, clientes[index_seleccionado][0])       
        cursor.execute("UPDATE [Inquilinos] SET [Propietario] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][8], clientes[index_seleccionado][0])       
        cursor.execute("UPDATE [Inquilinos] SET [Tipo_comision] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][9], clientes[index_seleccionado][0])      
        cursor.execute("UPDATE [Inquilinos] SET [Monto_comision] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][10], clientes[index_seleccionado][0])      
        cursor.execute("UPDATE [Inquilinos] SET [Aguas_cuota] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][11], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Aguas_Importe] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][12], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Porcentual_agua_e_imp] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][13], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Quien_paga_Agua] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][14], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Muni_Cuota] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][15], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Muni_Importe] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][16], clientes[index_seleccionado][0])       
        cursor.execute("UPDATE [Inquilinos] SET [Quien_paga_Muni] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][17], clientes[index_seleccionado][0])       
        cursor.execute("UPDATE [Inquilinos] SET [Rentas_cuota] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][18], clientes[index_seleccionado][0])       
        cursor.execute("UPDATE [Inquilinos] SET [Rentas_Importe] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][19], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Quien_paga_rentas] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][20], clientes[index_seleccionado][0])       
        cursor.execute("UPDATE [Inquilinos] SET [Monto_unico_agua_e_imp] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][21], clientes[index_seleccionado][0])       
        cursor.execute("UPDATE [Inquilinos] SET [Mes_Expensa] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][22], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Monto_Expensa] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][23], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Adicional_pagares] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][24], clientes[index_seleccionado][0])       
        cursor.execute("UPDATE [Inquilinos] SET [Cuenta_y_orden] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][25], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Libre] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][26], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [catastro] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][27], clientes[index_seleccionado][0])       
        cursor.execute("UPDATE [Inquilinos] SET [rentas] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][28], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Aguas_cordobesas] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][29], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [conceptos_incluidos] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][30], clientes[index_seleccionado][0])        
        cursor.execute("UPDATE [Inquilinos] SET [Paga_x_transf] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][31], clientes[index_seleccionado][0])
        cursor.execute("UPDATE [Inquilinos] SET [URL_Aguas_Cbesas] = ? WHERE [Inquilino_id] = ?", clientes[index_seleccionado][32], clientes[index_seleccionado][0])
        conn.commit()

        # Se actualiza el comboBox.
        self.actualizar_nombres_clientes()

        # Se muestra un messageBox de que se completó la acción.
        self.mostrar_dialog("Se aplicaron correctamente los cambios.", "Cambios Aplicados")


    @Slot()
    def cambiar_seleccion(self):
        # Modifica la información mostrada según el cliente seleccionado.
        global index_seleccionado
        index_seleccionado = self.cb_seleccionar_cliente.currentIndex() - 1
        print(index_seleccionado)
        self.actualizar_data()

    @Slot()
    def volver_sin_guardar(self, index):
        # Se resetean los campos de la ventana de edición y se actualizan los campos de la ventana principal.
        dialog.hide()
        self.resetear_campos()
        window.actualizar_nombres_clientes(index)
        window.show()

    @Slot()
    def salir(self):
        # Sale del programa.
        sys.exit(app.exec_())

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Hago que no se le pueda modificar el tamaño a la ventana.
        self.setFixedSize(self.size())

        self.ui.btn_exit.clicked.connect(self.salir)
        self.ui.cb_seleccionar_cliente.currentIndexChanged.connect(self.cambiar_seleccion)
        self.ui.btn_actualizar_aguas_cordobesas.clicked.connect(self.activar_extraer_un_info)
        self.ui.btn_actualizar_agua_todos.clicked.connect(self.activar_extraer_info)
        self.ui.btn_editar_cliente.clicked.connect(self.abrir_editar)

        # Deshabilito la opción "Sin Selección" del comboBox
        self.ui.cb_seleccionar_cliente.model().item(0).setEnabled(False)

        # Deshabilito el botón para buscar el valor de Aguas Cordobesas por default
        # para que no se pueda buscar el valor de "Sin Selección".
        self.ui.btn_actualizar_aguas_cordobesas.setEnabled(False)

        # Traigo la información de la base de datos.
        self.conectar_access()       

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
    def abrir_editar(self):
        # Muestro la ventana de edición conn la información cargada según el cliente seleccionado.
        window.hide()
        dialog.show()

        # Verifico que la ventana de edición de cliente se abra con un cliente seleccionado en el comboBox.
        if self.ui.cb_seleccionar_cliente.currentIndex() != 0:
            dialog.cb_seleccionar_cliente.setCurrentIndex(self.ui.cb_seleccionar_cliente.currentIndex())
        else:
            dialog.cb_seleccionar_cliente.setCurrentIndex(1)

        dialog.actualizar_data()

    @Slot()
    def cambiar_seleccion(self):
        # Modifica la información mostrada según el cliente seleccionado.
        self.ui.btn_actualizar_aguas_cordobesas.setEnabled(True)
        self.ui.le_periodo_a_buscar.setEnabled(True)
        global index_seleccionado
        index_seleccionado = self.ui.cb_seleccionar_cliente.currentIndex() - 1
        print(index_seleccionado)
        self.actualizar_data()

    @Slot()
    def activar_extraer_un_info(self):
        # Comienzo la búsqueda de información de eaguas cordobesas en otro hilo.
        thread = threading.Thread(target = self.extraer_info_un_cliente, daemon=True)
        thread.start()

    @Slot()
    def activar_extraer_info(self):
        # Comienzo la búsqueda de información de eaguas cordobesas en otro hilo.
        thread = threading.Thread(target = self.actualizar_aguas_de_todos, daemon=True)
        thread.start()

    @Slot()
    def conectar_access(self):
        # Creo una conexión a la base de datos. 
        global conn
        conn = pyodbc.connect("Driver={%s};DBQ=%s;" % (DRIVER_NAME, PATH_DATABASE))

        # Selecciono de dónde extraer la información.
        global cursor
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Inquilinos")

        # Extraigo la información y la almaceno en el vector de clientes.
        for row in cursor.fetchall():
            clientes.append(row)

        # Cargo las opciones del comboBox por primera vez y printeo la información en pantalla.
        for i in range(len(clientes)):
            self.ui.cb_seleccionar_cliente.addItem(clientes[i][1])
            print(clientes[i])
            print("\n")
        

    def extraer_info_un_cliente(self):
        # Me fijo que el usuario haya aclarado qué periodo buscar.
        if self.ui.le_periodo_a_buscar.text() != "":
            # Deshabilito los botones de actualizar Aguas Cordobesas.
            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(False)
            self.ui.btn_actualizar_agua_todos.setEnabled(False)
            self.ui.le_periodo_a_buscar.setEnabled(False)
             
            # Consigo el periodo deseado para buscar.
            periodo_deseado = int(self.ui.le_periodo_a_buscar.text())

            # Abro un navegador en el url del cliente seleccionado.
            global index_seleccionado
            url = clientes[index_seleccionado][32]
            driver = webdriver.Chrome()
            print(url)
            driver.get(url)

            # Espero a que cargue la página.
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sUf"]')))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="tbl-detalleDeuda"]/tbody[2]')))

            # Consigo el texto de la boleta.
            text = driver.find_element_by_xpath('//*[@id="tbl-detalleDeuda"]/tbody[2]').text
            codigo = driver.find_element_by_xpath('//*[@id="sUf"]').text
            
            # Extraigo la información relevante de la boleta.
            text = text.split()
            while len(text) > 10:
                comprobacion = text[1].split('/')
                if int(comprobacion[0]) == periodo_deseado:
                    break
                del text[0:10]
            text[8] = text[8].replace(",", ".")

            print(text)

            # Actualizo el vector de clientes con la información extraida.
            periodo = text[1].split('/')
            clientes[index_seleccionado][12] = text[8]
            clientes[index_seleccionado][11] = periodo[0]

            # Actualizo la base de datos con la información extraida y aplico cambios.
            cursor.execute("UPDATE [Inquilinos] SET [Aguas_Importe] = ?, [Aguas_cuota] = ? WHERE [URL_Aguas_Cbesas] = ?", text[8], periodo[0], url)
            conn.commit()
            print("Modificado")
            
            # Actualizo la información mostrada en la ventana.
            self.actualizar_data()

            # Cierro el navegador.
            driver.close()

            # Vuelvo a habilitar los botones para buscar Aguas Cordobesas.
            self.ui.btn_actualizar_aguas_cordobesas.setEnabled(True)
            self.ui.le_periodo_a_buscar.setEnabled(True)
            self.ui.btn_actualizar_agua_todos.setEnabled(True)

    def actualizar_aguas_de_todos(self): # Este método es igual al otro pero lo hace con todos los clientes que posean cuenta de Aguas Cordobesas.
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

                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="sUf"]')))
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
        # Sale del programa.
        sys.exit(app.exec_())

        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    dialog = Dialog()
    window.show()

    sys.exit(app.exec_())
