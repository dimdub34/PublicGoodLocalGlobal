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
