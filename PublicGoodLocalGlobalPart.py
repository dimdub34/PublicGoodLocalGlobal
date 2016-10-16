# -*- coding: utf-8 -*-

from twisted.internet import defer
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, ForeignKey, String
import logging
from datetime import datetime
from util.utiltools import get_module_attributes
from server.servbase import Base
from server.servparties import Partie
import PublicGoodLocalGlobalParams as pms


logger = logging.getLogger("le2m")


class PartiePGLG(Partie):
    __tablename__ = "partie_PublicGoodLocalGlobal"
    __mapper_args__ = {'polymorphic_identity': 'PublicGoodLocalGlobal'}
    partie_id = Column(Integer, ForeignKey('parties.id'), primary_key=True)
    repetitions = relationship('RepetitionsPGLG')

    def __init__(self, le2mserv, joueur):
        super(PartiePGLG, self).__init__("PublicGoodLocalGlobal", "PGLG")
        self._le2mserv = le2mserv
        self.joueur = joueur
        self.PGLG_gain_ecus = 0
        self.PGLG_gain_euros = 0

    @defer.inlineCallbacks
    def configure(self, *args):
        logger.debug(u"{} Configure".format(self.joueur))
        yield (self.remote.callRemote("configure", get_module_attributes(pms)))

    @defer.inlineCallbacks
    def newperiod(self, period):
        """
        Create a new period and inform the remote
        If this is the first period then empty the historic
        :param period:
        :return:
        """
        logger.debug(u"{} New Period".format(self.joueur))
        self.currentperiod = RepetitionsPGLG(period)
        self.currentperiod.PGLG_group = self.joueur.groupe
        self.currentperiod.PGLG_sousgroup = self.joueur.sousgroupe
        self._le2mserv.gestionnaire_base.ajouter(self.currentperiod)
        self.repetitions.append(self.currentperiod)
        yield (self.remote.callRemote("newperiod", period))
        logger.info(u"{} Ready for periode {}".format(self.joueur, period))

    @defer.inlineCallbacks
    def display_decision(self):
        """
        Display the decision screen on the remote
        Get back the decision
        :return:
        """
        logger.debug(u"{} Decision".format(self.joueur))
        debut = datetime.now()
        indiv, loc, glob = yield(self.remote.callRemote("display_decision"))
        self.currentperiod.PGLG_decisiontime = \
            (datetime.now() - debut).seconds
        self.currentperiod.PGLG_indiv = indiv
        self.currentperiod.PGLG_local = loc
        self.currentperiod.PGLG_global = glob
        self.joueur.info(u"{}".format((indiv, loc, glob)))
        self.joueur.remove_waitmode()

    def compute_periodpayoff(self):
        """
        Compute the payoff for the period
        :return:
        """
        logger.debug(u"{} Period Payoff".format(self.joueur))
        self.currentperiod.PGLG_indivpayoff = self.currentperiod.PGLG_indiv * \
                                              pms.TAUX_INDIV

        self.currentperiod.PGLG_localpayoff = \
            self.currentperiod.PGLG_localsousgroup * pms.TAUX_LOCAL

        self.currentperiod.PGLG_globalpayoff = \
            self.currentperiod.PGLG_globalgroup * pms.TAUX_GLOBAL

        self.currentperiod.PGLG_periodpayoff = \
            self.currentperiod.PGLG_indivpayoff + \
            self.currentperiod.PGLG_localpayoff + \
            self.currentperiod.PGLG_globalpayoff

        # cumulative payoff since the first period
        if self.currentperiod.PGLG_period < 2:
            self.currentperiod.PGLG_cumulativepayoff = \
                self.currentperiod.PGLG_periodpayoff
        else: 
            previousperiod = self.periods[
                self.currentperiod.PGLG_period - 1]
            self.currentperiod.PGLG_cumulativepayoff = \
                previousperiod.PGLG_cumulativepayoff + \
                self.currentperiod.PGLG_periodpayoff

        # we store the period in the self.periodes dictionnary
        self.periods[self.currentperiod.PGLG_period] = self.currentperiod

        logger.debug(u"{} Period Payoff {}".format(
            self.joueur, self.currentperiod.PGLG_periodpayoff))

    @defer.inlineCallbacks
    def display_summary(self, *args):
        logger.debug(u"{} Summary".format(self.joueur))
        yield(self.remote.callRemote(
                "display_summary", self.currentperiod.todict()))
        self.joueur.info("Ok")
        self.joueur.remove_waitmode()

    @defer.inlineCallbacks
    def compute_partpayoff(self):
        logger.debug(u"{} Part Payoff".format(self.joueur))

        self.PGLG_gain_ecus = \
            self.currentperiod.PGLG_cumulativepayoff
        self.PGLG_gain_euros = \
            float(self.PGLG_gain_ecus) * \
            float(pms.TAUX_CONVERSION)
        yield (self.remote.callRemote(
            "set_payoffs", self.PGLG_gain_euros, self.PGLG_gain_ecus))

        logger.info(u'{} Part Payoff ecus {} Part Payoff euros {:.2f}'.format(
            self.joueur, self.PGLG_gain_ecus, self.PGLG_gain_euros))


class RepetitionsPGLG(Base):
    __tablename__ = 'partie_PublicGoodLocalGlobal_repetitions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    partie_partie_id = Column(
        Integer,
        ForeignKey("partie_PublicGoodLocalGlobal.partie_id"))

    PGLG_period = Column(Integer)
    PGLG_treatment = Column(Integer)
    PGLG_group = Column(String)
    PGLG_sousgroup = Column(String)
    PGLG_indiv = Column(Integer)
    PGLG_local = Column(Integer)
    PGLG_global = Column(Integer)
    PGLG_decisiontime = Column(Integer)
    PGLG_localsousgroup = Column(Integer)
    PGLG_localothersousgroup = Column(Integer)
    PGLG_globalsousgroup = Column(Integer)
    PGLG_globalgroup = Column(Integer)
    PGLG_indivpayoff = Column(Float)
    PGLG_localpayoff = Column(Float)
    PGLG_globalpayoff = Column(Float)
    PGLG_periodpayoff = Column(Float)
    PGLG_cumulativepayoff = Column(Float)

    def __init__(self, periode):
        self.PGLG_treatment = pms.TREATMENT
        self.PGLG_period = periode
        self.PGLG_decisiontime = 0
        self.PGLG_periodpayoff = 0
        self.PGLG_cumulativepayoff = 0

    def todict(self, joueur=None):
        temp = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if joueur:
            temp["joueur"] = joueur
        return temp
