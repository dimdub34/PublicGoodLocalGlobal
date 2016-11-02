# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import logging
from random import randint
from client.cltgui.cltguidialogs import GuiHistorique
from client.cltgui.cltguiwidgets import WExplication, WPeriod, WSpinbox
from util.utili18n import le2mtrans
import PublicGoodLocalGlobalParams as pms
import PublicGoodLocalGlobalTexts as textes_PGLG
from PublicGoodLocalGlobalTexts import trans_PGLG


logger = logging.getLogger("le2m")


class GuiDecision(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, periode, historique):
        super(GuiDecision, self).__init__(parent)

        # variables
        self._defered = defered
        self._automatique = automatique
        self._historique = GuiHistorique(self, historique, size=(1100, 500))

        layout = QtGui.QVBoxLayout(self)

        wperiod = WPeriod(period=periode, ecran_historique=self._historique,
                          parent=self)
        layout.addWidget(wperiod)

        wexplanation = WExplication(
            text=textes_PGLG.get_text_explanation(),
            parent=self, size=(450, 80))
        layout.addWidget(wexplanation)
        
        gridlayout = QtGui.QGridLayout()
        layout.addLayout(gridlayout)
        
        CURRENT_LINE = 0
        
        gridlayout.addWidget(QtGui.QLabel(u"Saisissez le nombre de jetons que "
                                          u"vous placez sur votre compte individuel"),
                             CURRENT_LINE, 0)
        self._spin_indiv = QtGui.QSpinBox()
        self._spin_indiv.setMinimum(0)
        self._spin_indiv.setMaximum(pms.DOTATION)
        self._spin_indiv.setSingleStep(1)
        self._spin_indiv.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_indiv.setMaximumWidth(80)
        gridlayout.addWidget(self._spin_indiv, CURRENT_LINE, 1)
        
        CURRENT_LINE += 1
        
        gridlayout.addWidget(QtGui.QLabel(u"Saisissez le nombre de jetons que "
                                          u"vous placez sur le compte local"),
                             CURRENT_LINE, 0)
        self._spin_local = QtGui.QSpinBox()
        self._spin_local.setMinimum(0)
        self._spin_local.setMaximum(pms.DOTATION)
        self._spin_local.setSingleStep(1)
        self._spin_local.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_local.setMaximumWidth(80)
        gridlayout.addWidget(self._spin_local, CURRENT_LINE, 1)
        
        CURRENT_LINE += 1
        
        gridlayout.addWidget(QtGui.QLabel(u"Saisissez le nombre de jetons que "
                                          u"vous placez sur le compte global"),
                             CURRENT_LINE, 0)
        self._spin_global = QtGui.QSpinBox()
        self._spin_global.setMinimum(0)
        self._spin_global.setMaximum(pms.DOTATION)
        self._spin_global.setSingleStep(1)
        self._spin_global.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_global.setMaximumWidth(80)
        gridlayout.addWidget(self._spin_global, CURRENT_LINE, 1)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self._accept)
        layout.addWidget(buttons)

        self.setWindowTitle(trans_PGLG(u"Decision"))
        self.adjustSize()
        self.setFixedSize(self.size())

        if self._automatique:
            indiv, loc, glob = 0, 0, 0
            while indiv + loc + glob != pms.DOTATION:
                indiv = randint(0, pms.DOTATION)
                loc = randint(0, pms.DOTATION)
                glob = randint(0, pms.DOTATION)
            self._spin_indiv.setValue(indiv)
            self._spin_local.setValue(loc)
            self._spin_global.setValue(glob)
            self._timer_automatique = QtCore.QTimer()
            self._timer_automatique.timeout.connect(
                buttons.button(QtGui.QDialogButtonBox.Ok).click)
            self._timer_automatique.start(7000)
                
    def reject(self):
        pass
    
    def _accept(self):
        try:
            self._timer_automatique.stop()
        except AttributeError:
            pass
        indiv = self._spin_indiv.value()
        loc = self._spin_local.value()
        glob = self._spin_global.value()
        if indiv + loc + glob != pms.DOTATION:
            QtGui.QMessageBox.warning(
                self, u"Attention", u"Vous devez répartir les {} jetons entre "
                                    u"les trois comptes.".format(pms.DOTATION))
            return
        if not self._automatique:
            confirmation = QtGui.QMessageBox.question(
                self, le2mtrans(u"Confirmation"),
                le2mtrans(u"Do you confirm your choice?"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
            if confirmation != QtGui.QMessageBox.Yes: 
                return
        logger.info(u"Decision callback {}".format((indiv, loc, glob)))
        self.accept()
        self._defered.callback((indiv, loc, glob))


class DConfigure(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        form = QtGui.QFormLayout()
        layout.addLayout(form)

        # treatment
        self._combo_treatment = QtGui.QComboBox()
        self._combo_treatment.addItems(
            list(sorted(pms.TREATMENTS_NAMES.viewvalues())))
        self._combo_treatment.setCurrentIndex(pms.TREATMENT)
        form.addRow(QtGui.QLabel(u"Traitement"), self._combo_treatment)

        # nombre de périodes
        self._spin_periods = QtGui.QSpinBox()
        self._spin_periods.setMinimum(0)
        self._spin_periods.setMaximum(100)
        self._spin_periods.setSingleStep(1)
        self._spin_periods.setValue(pms.NOMBRE_PERIODES)
        self._spin_periods.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_periods.setMaximumWidth(50)
        form.addRow(QtGui.QLabel(u"Nombre de périodes"), self._spin_periods)

        # periode essai
        self._checkbox_essai = QtGui.QCheckBox()
        self._checkbox_essai.setChecked(pms.PERIODE_ESSAI)
        form.addRow(QtGui.QLabel(u"Période d'essai"), self._checkbox_essai)

        # taille groupes
        self._spin_groups = QtGui.QSpinBox()
        self._spin_groups.setMinimum(2)
        self._spin_groups.setMaximum(100)
        self._spin_groups.setSingleStep(1)
        self._spin_groups.setValue(pms.TAILLE_GROUPES)
        self._spin_groups.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_groups.setMaximumWidth(50)
        form.addRow(QtGui.QLabel(u"Taille des groupes"), self._spin_groups)
        
        # taille sous-groupes
        self._sping_subgroups = QtGui.QSpinBox()
        self._sping_subgroups.setMinimum(2)
        self._sping_subgroups.setMaximum(100)
        self._sping_subgroups.setSingleStep(1)
        self._sping_subgroups.setValue(pms.TAILLE_SOUS_GROUPES)
        self._sping_subgroups.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._sping_subgroups.setMaximumWidth(50)
        form.addRow(QtGui.QLabel(u"Taille des sous-groupes"), self._sping_subgroups)

        button = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        button.accepted.connect(self._accept)
        button.rejected.connect(self.reject)
        layout.addWidget(button)

        self.setWindowTitle(u"Configurer")
        self.adjustSize()
        self.setFixedSize(self.size())

    def _accept(self):
        pms.TREATMENT = self._combo_treatment.currentIndex()
        pms.PERIODE_ESSAI = self._checkbox_essai.isChecked()
        pms.NOMBRE_PERIODES = self._spin_periods.value()
        pms.TAILLE_GROUPES = self._spin_groups.value()
        pms.TAILLE_SOUS_GROUPES = self._sping_subgroups.value()
        self.accept()
