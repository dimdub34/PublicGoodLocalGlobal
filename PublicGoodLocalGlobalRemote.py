# -*- coding: utf-8 -*-

from twisted.internet import defer
from client.cltremote import IRemote
import logging
from random import randint
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
        self._histo_vars = ["PGLG_period", "PGLG_indiv", "PGLG_local",
                            "PGLG_global", "PGLG_localsousgroup",
                            "PGLG_globalsousgroup", "PGLG_globalgroup",
                            "PGLG_indivpayoff", "PGLG_localpayoff", "PGLG_globalpayoff",
                            "PGLG_periodpayoff", "PGLG_cumulativepayoff"]
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
            indiv, loc, glob = 0, 0, 0
            while indiv + loc + glob != pms.DOTATION:
                indiv = randint(0, pms.DOTATION)
                loc = randint(0, pms.DOTATION)
                glob = randint(0, pms.DOTATION)
            logger.info(u"{} Send back {}".format(self._le2mclt.uid,
                                                  (indiv, loc, glob)))
            return indiv, loc, glob
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
                texts_PGG.get_text_summary(period_content),
                size_histo=(1100, 120))
            ecran_recap.show()
            return defered
