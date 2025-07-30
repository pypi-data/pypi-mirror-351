import pandas as pd 
import numpy as np 
import os
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),'simsad/data')


# SAD credit (maison et RPA)   
class cmd:
    """
    Crédit d'impôt pour maintien à domicile (CMD) des aînés

    Cette classe permet de modéliser les coûts liés au Crédit d'impôt pour maintien à domicile des aînés.
    """
    def __init__(self):
        self.load_params()
        self.load_registry()
        return
    def load_registry(self):
        """
        Fonction qui permet de créer le registre du CMD. Ce registre contient des informations 
        sur les montants agrégés.
        """
        nregions = 18
        last_region = nregions + 1
        self.registry = pd.DataFrame(index=np.arange(1,last_region),columns=['cost_rpa','cost_home','cout_total'])

        self.targets = pd.read_csv(os.path.join(data_dir,'calib_cmd.csv'),
            delimiter=';',low_memory=False)
        self.targets.set_index('annee',inplace=True)
        self.targets.mnt.astype('float64')
        return
    def load_params(self, start_yr = 2019):
        """
        Fonction qui permet de charger les paramètres liés aux montants de CMD par individu.

        Parameters
        ----------
        start_yr: int
            année de référence (défaut=2019)
        """
        self.params =  pd.read_csv(os.path.join(data_dir,'mnt_cmd.csv'),
            delimiter=';',low_memory=False)
        self.params = self.params[self.params['annee']==start_yr]
        self.params['gr_age'] = 3
        params_frame = self.params.copy()
        for x in [1, 2]:
            params_frame['gr_age'] = x
            self.params = pd.concat([self.params,params_frame])
        self.params.set_index(['region_id', 'iso_smaf', 'gr_age'], inplace=True)
        self.params = self.params[['dom','rpa']]
        self.params.columns = ['mnt_home','mnt_rpa']
        self.params.loc[self.params.index.get_level_values(2)==1,:] = 0.0
        self.params.loc[self.params.index.get_level_values(2)==2,:] = 0.0
        return
    def assign(self, users, milieu):
        """
        Fonction qui détermine les prestataires du CMD et qui attribue les montants reçu.

        Parameters
        ----------
        users: dataframe
            Bassin d'individus d'un milieu de vie donné
        milieu: str
            Nom du milieu de vie

        Returns
        -------
        users: dataframe
           Bassin d'individus d'un milieu de vie donné   
        """
        work = users.copy()
        merge_keys = ['region_id','iso_smaf','gr_age']
        work = work.merge(self.params,left_on=merge_keys,right_on=merge_keys,how='left')
        users['cmd_mnt'] = work['mnt_'+milieu]
        return users
    def calibrate(self, users_home, users_rpa, yr):
        """
        Fonction qui calibre les montants simulés de CMD sur les montants agrégés budgétés jusqu'en 2026.

        Parameters
        ----------
        users_home: dataframe
            Bassin d'individus à domicile
        users_home: dataframe
            Bassin d'individus en RPA
        yr: int
            Année en cours de la simulation  

        Returns
        -------
        users_home: dataframe
            Bassin d'individus à domicile
        users_home: dataframe
            Bassin d'individus en RPA   
        """
        tot_home = users_home[['cmd_mnt','wgt']].prod(axis=1).sum(axis=0)
        tot_rpa  = users_rpa[['cmd_mnt','wgt']].prod(axis=1).sum(axis=0)
        tot = tot_home + tot_rpa
        if yr<=2026:
            target = self.targets.loc[yr,'mnt']
            self.factor = target/tot
        users_home['cmd_mnt'] *= self.factor
        users_rpa['cmd_mnt'] *= self.factor
        return users_home, users_rpa
    def compute_costs(self, users_home, users_rpa):
        """
        Fonction qui calcule les coûts du CMD.

        Parameters
        ----------
        users_home: dataframe
            Bassin d'individus à domicile
        users_home: dataframe
            Bassin d'individus en RPA
        """
        self.registry['cost_home'] = users_home.groupby('region_id').apply(lambda d: (d['cmd_mnt'] * d.wgt).sum())
        self.registry['cost_rpa'] = users_rpa.groupby('region_id').apply(lambda d: (d['cmd_mnt'] * d.wgt).sum())
        self.registry['cout_total'] = self.registry['cost_home'] + \
                                      self.registry['cost_rpa']
        return

    def collapse(self, domain = 'registry', rowvars=['region_id'],colvars=['smaf']):
        if domain == 'registry':
            if 'smaf' in colvars:
                table = self.registry.loc[:,['iso_smaf_tot'+str(s) for s in range(1,15)]]
                table.columns = [s for s in range(1,15)]
            else :
                table = self.registry.loc[:,colvars]
        if domain == 'users':
                table = pd.concat([self.users.groupby(rowvars).apply(lambda d: (d[c] * d.wgt).sum()) for c in colvars], axis=1)
                table.columns = colvars
                table = table[colvars]
        return table


