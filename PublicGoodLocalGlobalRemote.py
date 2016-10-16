# -*- coding: utf-8 -*-

from twisted.internet import defer
from client.cltremote import IRemote
import logging
import random
from client.cltgui.cltguidialogs import GuiRecapitulatif
import PublicGoodLocalGlobalParams as pms
from PublicGoodLocalGlobalGui import GuiDecision
import PublicGoodLocalGlobalTexts as texts_PGG


logger = logging.getLogger("le2m")


class RemotePGLG(IRemote):
    """
    Class remote, remote_ methods can be called by the server
    """
    def __init__(self, le2mclt):
        IRemote.__init__(self, le2mclt)
        self._histo_vars = ["PGLG_period", "PGLG_indiv", "PGLG_public",
                            "PGLG_publicgroup", "PGLG_periodpayoff",
                            "PGLG_cumulativepayoff"]
        self.histo.append(texts_PGG.get_histo_head())

    def remote_configure(self, params):
        logger.info(u"{} Configure".format(self._le2mclt.uid))
        for k, v in params.viewitems():
            setattr(pms, k, v)

    def remote_newperiod(self, period):
        logger.info(u"{} Period {}".format(self._le2mclt.uid, period))
        self.currentperiod = period
        if self.currentperiod == 1:
            del self.histo[1:]

    def remote_display_decision(self):
        logger.info(u"{} Decision".format(self._le2mclt.uid))
        if self._le2mclt.simulation:
            decision = \
                random.randrange(
                    pms.DECISION_MIN,
                    pms.DECISION_MAX + pms.DECISION_STEP,
                    pms.DECISION_STEP)
            logger.info(u"{} Send back {}".format(self._le2mclt.uid, decision))
            return decision
        else: 
            defered = defer.Deferred()
            ecran_decision = GuiDecision(
                defered, self._le2mclt.automatique,
                self._le2mclt.screen, self.currentperiod, self.histo)
            ecran_decision.show()
            return defered

    def remote_display_summary(self, period_content):
        logger.info(u"{} Summary".format(self._le2mclt.uid))
        self.histo.append([period_content.get(k) for k in self._histo_vars])
        if self._le2mclt.simulation:
            return 1
        else:
            defered = defer.Deferred()
            ecran_recap = GuiRecapitulatif(
                defered, self._le2mclt.automatique, self._le2mclt.screen,
                self.currentperiod, self.histo,
                texts_PGG.get_text_summary(period_content))
            ecran_recap.show()
            return defered
