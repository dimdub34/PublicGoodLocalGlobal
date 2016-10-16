# -*- coding: utf-8 -*-

# variables
TREATMENTS = {0: "baseline"}

# parameters
DOTATION = 20
TAUX_INDIV = 1
TAUX_LOCAL = 0.5
TAUX_GLOBAL = 0.5
TREATMENT = 0
TAUX_CONVERSION = 0.1
NOMBRE_PERIODES = 2
TAILLE_GROUPES = 4
TAILLE_SOUS_GROUPES = 2
GROUPES_CHAQUE_PERIODE = False
MONNAIE = u"ecu"

# DECISION
DECISION_MIN = 0
DECISION_MAX = DOTATION
DECISION_STEP = 1


def get_treatment(code_or_name):
    if type(code_or_name) is int:
        return TREATMENTS.get(code_or_name, None)
    elif type(code_or_name) is str:
        for k, v in TREATMENTS.viewitems():
            if v.lower() == code_or_name.lower():
                return k
    return None
