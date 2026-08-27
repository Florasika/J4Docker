"""
JOUR 4 / 10 — Docker : Multi-stage Build
Pipeline ETL dans une image optimisée.

Démontre que l'application fonctionne exactement pareil
dans une image légère (~100MB) que dans une image naive (~900MB).
"""

import pandas as pd
import os
import json
import sys
from datetime import datetime, date

OUTPUT_PATH = os.getenv('OUTPUT_PATH', '/app/output')


def infos_environnement():
    """Affiche les infos de l'environnement Docker."""
    import platform
    print(f"\n── Environnement ──")
    print(f"  Python       : {sys.version.split()[0]}")
    print(f"  OS           : {platform.system()} {platform.release()}")
    print(f"  Pandas       : {pd.__version__}")
    print(f"  Utilisateur  : {os.getenv('USER', 'appuser')}")
    print(f"  Répertoire   : {os.getcwd()}")
    print(f"  Output       : {OUTPUT_PATH}")


def extraire():
    import random
    random.seed(42)
    produits = ['Laptop Pro','Smartphone X','Tablette Air','Écouteurs BT']
    prix     = {'Laptop Pro':1200,'Smartphone X':650,'Tablette Air':450,'Écouteurs BT':120}
    vendeurs = ['Alice','Karim','Lucie','Thomas','Nadia']

    rows = [{'date':date.today().isoformat(),
             'produit':(p:=random.choice(produits)),
             'vendeur':random.choice(vendeurs),
             'quantite':(q:=random.randint(1,10)),
             'montant':q*prix[p]}
            for _ in range(25)]

    df = pd.DataFrame(rows)
    print(f"\n── Extract ──")
    print(f"  {len(df)} lignes — CA: {df['montant'].sum():.0f}€")
    return df


def transformer(df):
    df = df.copy()
    df['marge']      = (df['montant'] * 0.42).round(2)
    df['charge_le']  = datetime.now().isoformat()
    print(f"\n── Transform ──")
    print(f"  Marge totale: {df['marge'].sum():.0f}€")
    return df


def charger(df):
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_path = f"{OUTPUT_PATH}/ventes_{ts}.csv"
    df.to_csv(csv_path, index=False)

    kpis = {
        'timestamp'   : datetime.now().isoformat(),
        'ca_total'    : round(float(df['montant'].sum()), 2),
        'marge_totale': round(float(df['marge'].sum()), 2),
        'nb_ventes'   : len(df),
        'top_produit' : df.groupby('produit')['montant'].sum().idxmax(),
    }
    kpi_path = f"{OUTPUT_PATH}/kpis_{ts}.json"
    with open(kpi_path, 'w') as f:
        json.dump(kpis, f, indent=2, ensure_ascii=False)

    print(f"\n── Load ──")
    print(f"  CSV  → {csv_path}")
    print(f"  KPIs → {kpi_path}")
    for k, v in kpis.items():
        print(f"  {k:15} : {v}")


if __name__ == '__main__':
    print("=" * 45)
    print("  ETL Optimisé — Jour 4 Docker Multi-stage")
    print("=" * 45)

    infos_environnement()
    df_raw   = extraire()
    df_clean = transformer(df_raw)
    charger(df_clean)

    print("\n✓ Pipeline terminé — image multi-stage ✓")
