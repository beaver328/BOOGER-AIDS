from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ResultWindow(object):
    def setupUi(self, ResultWindow):
        ResultWindow.setObjectName("ResultWindow")
        ResultWindow.resize(300, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(ResultWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.coeff_label = QtWidgets.QLabel(parent=ResultWindow)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.coeff_label.setFont(font)
        self.coeff_label.setObjectName("coeff_label")
        self.verticalLayout.addWidget(self.coeff_label)
        self.ingredients_table = QtWidgets.QTableWidget(parent=ResultWindow)
        self.ingredients_table.setObjectName("ingredients_table")
        self.ingredients_table.setColumnCount(0)
        self.ingredients_table.setRowCount(0)
        self.verticalLayout.addWidget(self.ingredients_table)

        self.retranslateUi(ResultWindow)
        QtCore.QMetaObject.connectSlotsByName(ResultWindow)

    def retranslateUi(self, ResultWindow):
        _translate = QtCore.QCoreApplication.translate
        ResultWindow.setWindowTitle(_translate("ResultWindow", "Результат пересчёта"))
        self.coeff_label.setText(_translate("ResultWindow", "Коэффициент пересчёта"))
