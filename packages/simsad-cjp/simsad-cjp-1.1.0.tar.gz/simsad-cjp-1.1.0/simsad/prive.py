import pandas as pd 
import numpy as np 
from itertools import product
import os
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),'simsad/data')
from numba import njit, float64, int64, boolean, prange
from numba.types import Tuple
from .needs import needs
from itertools import product




# autres services achetés, AVQ + soins infirmiers     
class prive:
    """
    Secteur privé

    Cette classe permet de modéliser les services offerts par le secteur privé et financés par le public.
    
    Parameters
    ----------
    policy: object
        paramètres du scénario
    """
    def __init__(self, policy):
        self.load_registry()
        self.policy = policy
        return
    def load_registry(self, start_yr = 2021):
        """
        Fonction qui permet de créer le registre du secteur privé. Ce registre contient des informations concernant 
        la main d'oeuvre, les heures fournies et les coûts.

        Parameters
        ----------
        start_yr: integer
            année de référence (défaut=2021)
        """
        self.registry = pd.read_csv(os.path.join(data_dir, 'registre_prive.csv'),
                                        delimiter=';', low_memory=False)
        self.registry = self.registry[self.registry.annee == start_yr]
        self.registry.set_index('region_id', inplace=True)
        self.registry['hrs_per_etc_avq'] = self.registry[
                                            'heures_tot_trav_avq']/self.registry['nb_etc_avq']
        self.registry['hrs_per_etc_avd'] = self.registry[
                                            'heures_tot_trav_avd']/self.registry[
            'nb_etc_avd']
        tups = list(product(*[np.arange(1,19),np.arange(1,15)]))
        itups = pd.MultiIndex.from_tuples(tups)
        itups.names = ['region_id','smaf']
        self.count = pd.DataFrame(index=itups,columns =['users','hrs_avq',
                                                        'hrs_avd'],
                                  dtype='float64')
        self.count.loc[:,:] = 0.0
        self.days_per_year = 365
        return
    def assign(self, users):
        """
        Fonction qui comptabilise le nombre d'usagers et le nombre total d'heures de services fournis (en AVQ et AVD) 
        par région et profil Iso-SMAF.

        Parameters
        ----------
        users: dataframe
            Bassin d'individus d'un milieu de vie donné
        
        Returns
        -------
        users: dataframe
            Bassin d'individus d'un milieu de vie donné
        """
        for r in range(1,19):
            for s in range(1,15):
                select = (users['region_id']==r) & (users['smaf']==s) & (users['ces_any'])
                self.count.loc[(r,s),'users'] = users.loc[select,'wgt'].sum()
                self.count.loc[(r,s),'hrs_avq'] = users.loc[select,['wgt',
                                                                 'ces_hrs_avq']].prod(axis=1).sum()
                self.count.loc[(r,s),'hrs_avd'] = users.loc[select,['wgt',
                                                                 'ces_hrs_avd']].prod(axis=1).sum()
        return
    def cap(self, users):
        """
        Fonction qui ajuste les heures de services fournis au niveau individuel (AVQ et AVD) 
        selon la main d'oeuvre disponible 
        et qui comptabilise les besoins supplémentaires en main d'oeuvre pour le privé.

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
        hrs_free = self.count.groupby('region_id').sum()['hrs_avq']
        factor = self.registry['supply_avq']/hrs_free
        factor.clip(upper=1.0,inplace=True)
        factor[factor.isna()] = 1.0
        excess = hrs_free - self.registry['supply_avq']
        excess.clip(lower=0.0, inplace=True)
        excess[excess.isna()] = 0.0
        indirect = (1.0 - self.registry['tx_hrs_dep_avq'])
        excess = excess / indirect
        excess = excess / self.registry['hrs_per_etc_avq']
        self.registry['worker_needs_avq'] = excess
        self.registry.loc[self.registry.worker_needs_avq.isna(),
                'worker_needs_avq'] = 0.0
        for r in range(1,19):
            users.loc[users.region_id==r,'ces_hrs_avq'] *= factor[r]

        hrs_free = self.count.groupby('region_id').sum()['hrs_avd']
        factor = self.registry['supply_avd']/hrs_free
        factor.clip(upper=1.0,inplace=True)
        factor[factor.isna()] = 1.0
        excess = hrs_free - self.registry['supply_avd']
        excess.clip(lower=0.0, inplace=True)
        excess[excess.isna()] = 0.0
        indirect = (1.0 - self.registry['tx_hrs_dep_avd'])
        excess = excess / indirect
        excess = excess / self.registry['hrs_per_etc_avd']
        self.registry['worker_needs_avd'] = excess
        self.registry.loc[self.registry.worker_needs_avd.isna(),
                'worker_needs_avd'] = 0.0
        for r in range(1,19):
            users.loc[users.region_id==r,'ces_hrs_avq'] *= factor[r]
        return users
    def compute_supply(self):
        """
        Fonction qui calcule le nombre total d'heures de services pouvant être fournies par le privé (AVQ et AVD)
        selon la main d'oeuvre disponible.
        """
        self.registry['supply_avq'] = self.registry['nb_etc_avq'] * \
                                      self.registry['hrs_per_etc_avq'] * (1.0
                                                                          -
                                                                          self.registry['tx_hrs_dep_avq'])
        self.registry['supply_avd'] = self.registry['nb_etc_avd'] * \
                                      self.registry['hrs_per_etc_avd']*(1.0
                                                                          -
                                                                          self.registry['tx_hrs_dep_avd'])

        return
    def compute_costs(self):
        """
        Fonction qui calcule les coûts du privé.
        """
        self.registry['cout_fixe'] = 0.0
        self.registry['cout_var'] = self.registry['sal_avq'] * self.registry[
            'nb_etc_avq'] * self.registry['hrs_per_etc_avq']
        self.registry['cout_var'] += self.registry['sal_avd'] * self.registry[
            'nb_etc_avd'] * self.registry['hrs_per_etc_avd']
        self.registry['cout_total'] = self.registry['cout_var'] + self.registry['cout_fixe']
        return
    def workforce(self,before_base_yr=False):
        """
        Fonction qui ajuste le nombre d'ETC du privé selon les besoins supplémentaires en main d'oeuvre et
        le taux d'ajustement de celle-ci.

        Parameters
        ----------
        before_base_yr: boolean
            True si l'année en cours de la simulation est inférieure 
            à l'année de départ de la comptabilisation des résultats 
        """
        for c in ['avd','avq']:
            if before_base_yr:
                attr = 1.0
            else:
                attr = getattr(self.policy,'prive_'+c+'_rate')
            self.registry['nb_etc_'+c] += \
                        attr * self.registry['worker_needs_'+c]
        return
    def collapse(self, domain = 'registry', rowvars=['region_id'],colvars=['needs_inf']):
        if domain == 'registry':
            if 'smaf' in colvars:
                table = self.registry.loc[:,['iso_smaf'+str(s) for s in range(1,15)]]
                table.columns = [s for s in range(1,15)]
            else :
                table = self.registry.loc[:,colvars]
        if domain == 'users':
                table = pd.concat([self.users.groupby(rowvars).apply(lambda d: (d[c] * d.wgt).sum()) for c in colvars], axis=1)
                table.columns = colvars
                table = table[colvars]
        return table
    

@njit((int64[:])(float64[:,:]), cache=True, parallel=True)
def draw_multinomial(prob):
        n, m = prob.shape
        set = np.arange(m)
        result = np.zeros(n,dtype='int64')
        u = np.random.uniform(low=0.0,high=1.0,size=n)
        for i in prange(n):
            cp = 0.0
            for j  in range(m):
                cp += prob[i,j]
                if u[i]<=cp:
                    result[i] = j
                    break
        return result

