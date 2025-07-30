import pandas as pd
import numpy as np
import os
from itertools import product
import shutil
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simsad/data')
pd.options.mode.chained_assignment = None


class tracker_entry:
    def __init__(self, entry_name, class_member, domain, rowvars, colvars, aggfunc, start_yr, stop_yr):
        self.entry_name = entry_name
        self.class_member = class_member
        self.domain = domain
        self.rowvars = rowvars
        self.colvars = colvars
        self.aggfunc = aggfunc
        self.start_yr = start_yr
        self.stop_yr = stop_yr
        self.table = []
        return


class tracker:
    """
    Résultats de simulation

    Cette classe permet la création de tableaux de sortie par rapport aux différents résultats du modèle.

    Parameters
    ----------
    scn_name: str
        nom du scénario (défaut='reference')
    """
    def __init__(self, scn_name = 'reference'):
        self.registry = []
        self.scn_name = scn_name
        return

    def add_entry(self, entry_name, class_member, domain, rowvars, colvars, aggfunc, start_yr, stop_yr):
        """
        Fonction qui permet la création d'un nouveau tableau de sortie.

        Parameters
        ----------
        entry_name: str
            nom du tableau
        class_member: str
            nom de la classe d'où proviennent les résultats
        domain: str
            nom du domaine d'où proviennent les résultats
        rowvars: str
            variables définissant les groupes d'agrégation (en ligne)
        colvars: str
            variables de résultats (en colonne)
        aggfunc: str
            nom de la fonction d'agrégation (ex. sum, mean, etc.)
        start_yr: int
            année de départ
        stop_yr: int
            année de fin
        """
        entry = tracker_entry(entry_name, class_member, domain, rowvars, colvars, aggfunc, start_yr, stop_yr)
        self.registry.append(entry)
        return

    def log(self, p, yr):
        """
        Fonction qui procède à la comptabilisation des résultats dans les tableaux de sortie.

        Parameters
        ----------
        p: object
            instance de classe
        yr: int
            année en cours dans la simulation
        """
        for k in self.registry:
            c = getattr(p, k.class_member)
            table = c.collapse(domain=k.domain, rowvars=k.rowvars, colvars=k.colvars).stack()
            if k.colvars == []:
                table = table.droplevel(1)
            if yr == k.start_yr:
                k.table = pd.DataFrame(index=table.index, columns=np.arange(k.start_yr, k.stop_yr + 1))
            if yr >= k.start_yr and yr <= k.stop_yr:
                k.table[yr] = table
        return

    def save(self, dir, scn_policy):
        """
        Fonction qui procède à la sauvegarde des tableaux de sortie dans un fichier excel.

        Parameters
        ----------
        dir: string
            sentier où sauvegarder les résultats
        scn_policy: object
            instance de classe policy
        """
        cwd = os.getcwd()
        target_dir = os.path.join(cwd,dir)
        check = os.path.isdir(target_dir)
        if not check:
            os.makedirs(target_dir)
        writer = pd.ExcelWriter(
            os.path.join(target_dir,'results_scenario_'+self.scn_name+'.xlsx'),
                                engine="xlsxwriter")
        scn = pd.Series(vars(scn_policy))
        scn.to_excel(writer,sheet_name='scenario parameters')
        for k in self.registry:
            k.table.sort_index(inplace=True)
            k.table.to_excel(writer, sheet_name=k.entry_name)
        writer.close()
        return
        
