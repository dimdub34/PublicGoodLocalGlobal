# -*- coding: utf-8 -*-
"""
Ce module contient les textes des écrans
"""
__author__ = "Dimitri DUBOIS"

import os
import logging
import configuration.configparam as params
from util.utiltools import get_pluriel
import PublicGoodLocalGlobalParams as pms
import gettext


logger = logging.getLogger("le2m")
localedir = os.path.join(params.getp("PARTSDIR"), "PublicGoodLocalGlobal", "locale")
try:
    trans_PGLG = gettext.translation(
        "PublicGoodLocalGlobal", localedir, languages=[params.getp("LANG")]).ugettext
except IOError:
    logger.critical(u"Translation file not found")
    trans_PGLG = lambda x: x  # if there is an error, no translation



def get_histo_head():
    return [trans_PGLG(u"Period"), trans_PGLG(u"Individual\naccount"),
            trans_PGLG(u"Public\naccount"), trans_PGLG(u"Public\naccount\ngroup"),
            trans_PGLG(u"Period\npayoff"), trans_PGLG(u"Cumulative\npayoff")]


def get_text_explanation():
    return trans_PGLG(u"You have an endowment of {} tokens.").format(pms.DOTATION)


def get_text_label_decision():
    return trans_PGLG(u"Please enter the number of token(s) you put on the "
                     u"public account")


def get_text_summary(period_content):
    txt = trans_PGLG(u"You put {} in your individual account and {} in the "
                    u"public account. Your group put {} in the public "
                    u"account.\nYour payoff for the current period is equal "
                    u"to {}.").format(
        get_pluriel(period_content.get("PGLG_indiv"), trans_PGLG(u"token")),
        get_pluriel(period_content.get("PGLG_public"), trans_PGLG(u"token")),
        get_pluriel(period_content.get("PGLG_publicgroup"), trans_PGLG(u"token")),
        get_pluriel(period_content.get("PGLG_periodpayoff"), pms.MONNAIE))
    return txt

