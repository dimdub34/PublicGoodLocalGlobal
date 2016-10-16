# -*- coding: utf-8 -*-

from twisted.internet import defer
import pandas as pd
import matplotlib.pyplot as plt
import logging
from collections import OrderedDict
from util import utiltools
import PublicGoodLocalGlobalParams as pms
from PublicGoodLocalGlobalTexts import trans_PGLG


logger = logging.getLogger("le2m".format(__name__))


class Serveur(object):
    def __init__(self, le2mserv):
        self._le2mserv = le2mserv

        # creation of the menu (will be placed in the "part" menu on the
        # server screen
        actions = OrderedDict()
        actions[trans_PGLG(u"Configure")] = self._configure
        actions[trans_PGLG(u"Display parameters")] = \
            lambda _: self._le2mserv.gestionnaire_graphique. \
            display_information2(
                utiltools.get_module_info(pms), u"Paramètres")
        actions[trans_PGLG(u"Start")] = lambda _: self._demarrer()
        actions[trans_PGLG(u"Display payoffs")] = \
            lambda _: self._le2mserv.gestionnaire_experience.\
            display_payoffs_onserver("PublicGoodLocalGlobal")
        self._le2mserv.gestionnaire_graphique.add_topartmenu(
            u"Public Good - Local Global", actions)

        self._fig = None

    def _configure(self):
        self._le2mserv.gestionnaire_graphique.display_information(
            trans_PGLG(u"There is no nothing to configure"))
        return

    @defer.inlineCallbacks
    def _demarrer(self):
        """
        Start the part
        :return:
        """
        # check conditions =====================================================
        if self._le2mserv.gestionnaire_joueurs.nombre_joueurs % \
                pms.TAILLE_GROUPES != 0 :
            self._le2mserv.gestionnaire_graphique.display_error(
                trans_PGLG(u"The number of players is not compatible "
                          u"with the group size"))
            return
        confirmation = self._le2mserv.gestionnaire_graphique.\
            question(u"Start PublicGoodLocalGlobal?")
        if not confirmation:
            return

        # init part ============================================================
        yield (self._le2mserv.gestionnaire_experience.init_part(
            "PublicGoodLocalGlobal", "PartiePGLG", "RemotePGLG", pms))
        self._tous = self._le2mserv.gestionnaire_joueurs.get_players(
            'PublicGoodLocalGlobal')

        # groups
        self._le2mserv.gestionnaire_groupes.former_groupes(
            self._le2mserv.gestionnaire_joueurs.get_players(),
            pms.TAILLE_GROUPES, forcer_nouveaux=True)

        # subgroups
        self._le2mserv.gestionnaire_groupes.former_sousgroupes(
            pms.TAILLE_SOUS_GROUPES, forcer_nouveaux=True)

        # set parameters on remotes
        yield (self._le2mserv.gestionnaire_experience.run_func(
            self._tous, "configure"))

        # start ================================================================
        for period in range(1 if pms.NOMBRE_PERIODES else 0,
                        pms.NOMBRE_PERIODES + 1):

            if self._le2mserv.gestionnaire_experience.stop_repetitions:
                break

            # init period
            self._le2mserv.gestionnaire_graphique.infoserv(
                [None, u"Période {}".format(period)])
            self._le2mserv.gestionnaire_graphique.infoclt(
                [None, u"Période {}".format(period)], fg="white", bg="gray")
            yield (self._le2mserv.gestionnaire_experience.run_func(
                self._tous, "newperiod", period))
            
            # decision
            yield(self._le2mserv.gestionnaire_experience.run_step(
                u"Décision", self._tous, "display_decision"))

            # compute total amount in the public account by group --------------
            self._le2mserv.gestionnaire_graphique.infoserv(
                trans_PGLG(u"Total amount by group"))

            for g, m in self._le2mserv.gestionnaire_groupes.get_groupes(
                    "PublicGoodLocalGlobal").viewitems():

                global_sg, local_sg = {}, {}
                for sg, msg in self._le2mserv.gestionnaire_groupes.get_sousgroupes(g).viewitems():
                    global_sg[sg] = sum([p.get_part("PublicGoodLocalGlobal").currentperiod.PGLG_global for p in msg])
                    local_sg[sg] = sum([p.get_part("PublicGoodLocalGlobal").currentperiod.PGLG_local for p in msg])
                    for p in msg:
                        p.get_part("PublicGoodLocalGlobal").currentperiod.PGLG_globalsousgroup = global_sg[sg]
                        p.get_part("PublicGoodLocalGlobal").currentperiod.PGLG_localsousgroup = local_sg[sg]
                    self._le2mserv.gestionnaire_graphique.infoserv(
                        u"G{} SG{} local {} global {}".format(
                            g.split("_")[2], sg.split("_")[2],
                            local_sg[sg], global_sg[sg]))

                total_global = sum(global_sg.viewvalues())
                self._le2mserv.gestionnaire_graphique.infoserv(
                    u"G{} global {}".format(g.split("_")[2], total_global))
                total_local = sum(local_sg.viewvalues())
                for p in m:
                    p.currentperiod.PGLG_globalgroup = total_global
                    p.currentperiod.PGLG_localothersousgroup = total_local - \
                        p.currentperiod.PGLG_localsousgroup

            # period payoff
            self._le2mserv.gestionnaire_experience.compute_periodpayoffs(
                "PublicGoodLocalGlobal")
        
            # summary
            yield(self._le2mserv.gestionnaire_experience.run_step(
                u"Summary", self._tous, "display_summary"))

        # end of part ==========================================================
        yield (self._le2mserv.gestionnaire_experience.finalize_part(
            "PublicGoodLocalGlobal"))


