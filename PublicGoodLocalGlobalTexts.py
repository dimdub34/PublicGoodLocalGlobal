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
            trans_PGLG(u"Local\naccount"), trans_PGLG(u"Global\naccount"),
            trans_PGLG(u"Local\naccount\nsubgoup"),
            trans_PGLG(u"Global\naccount\nsubgroup"),
            trans_PGLG(u"Global\naccount\ntotal"),
            trans_PGLG(u"Individual\naccount\npayoff"),
            trans_PGLG(u"Local\naccount\npayoff"),
            trans_PGLG(u"Global\naccount\npayoff"),
            trans_PGLG(u"Period\npayoff"),
            trans_PGLG(u"Cumulative\npayoff")]


def get_text_explanation():
    return trans_PGLG(u"You have an endowment of {} tokens.").format(pms.DOTATION)


def get_text_label_decision():
    return trans_PGLG(u"Please enter the number of token(s) you put on the "
                     u"public account")


def get_text_summary(period_content):
    txt = trans_PGLG(u"You put {} in your individual account, {} in the local "
                     u"account and {} in the global account. "
                     u"Your subgroup put {} in the local account and {} in "
                     u"the global account.\n"
                     u"Your group put {} in the global account.\n"
                     u"Your payoff for the current period is equal "
                     u"to {}.").format(
        get_pluriel(period_content.get("PGLG_indiv"), trans_PGLG(u"token")),
        get_pluriel(period_content.get("PGLG_local"), trans_PGLG(u"token")),
        get_pluriel(period_content.get("PGLG_global"), trans_PGLG(u"token")),
        get_pluriel(period_content.get("PGLG_localsousgroup"), trans_PGLG(u"token")),
        get_pluriel(period_content.get("PGLG_globalsousgroup"), trans_PGLG(u"token")),
        get_pluriel(period_content.get("PGLG_globalgroup"), trans_PGLG(u"token")),
        get_pluriel(period_content.get("PGLG_periodpayoff"), pms.MONNAIE))
    return txt

