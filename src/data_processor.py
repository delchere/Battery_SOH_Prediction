"""
Traitement des données : des fichiers Excel bruts au CSV avec features
"""
import numpy as np
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import RAW_DATA_PATH, PROCESSED_DATA_PATH, BATTERIES, INITIAL_CAPACITY_MAH, FEATURES_SOH
from src.utils import date_from_filename, get_channel_sheet, logger


def load_capacity_from_excel(bid: str) -> pd.DataFrame:
    """
    Charge tous les fichiers Excel d'une batterie et extrait la capacité par cycle
    """
    bat_path = os.path.join(RAW_DATA_PATH, bid)
    if not os.path.exists(bat_path):
        raise ValueError(f"Dossier non trouvé : {bat_path}")
    
    files = sorted(
        [os.path.join(bat_path, f) for f in os.listdir(bat_path) if f.endswith('.xlsx')],
        key=date_from_filename
    )
    
    logger.info(f"  Chargement de {len(files)} fichiers pour {bid}")
    
    all_caps = []
    cycle_global = 0
    
    for fpath in files:
        xl, sheet = get_channel_sheet(fpath)
        if sheet is None:
            continue
        
        df = xl.parse(sheet, header=0)
        df.columns = df.columns.str.strip()
        
        # Trouver colonne de capacité
        dcap_col = next(
            (c for c in df.columns if 'discharge' in c.lower() and 'capacity' in c.lower()),
            None
        )
        
        if dcap_col is None or 'Cycle_Index' not in df.columns:
            continue
        
        df['Cycle_Index'] = pd.to_numeric(df['Cycle_Index'], errors='coerce')
        df[dcap_col] = pd.to_numeric(df[dcap_col], errors='coerce')
        df = df.dropna(subset=['Cycle_Index', dcap_col])
        
        # Capacité = max - min par cycle
        grp = df.groupby('Cycle_Index')[dcap_col].agg(['min', 'max'])
        grp['capacity_Ah'] = grp['max'] - grp['min']
        grp = grp.reset_index()[['Cycle_Index', 'capacity_Ah']]
        grp.columns = ['cycle_in_file', 'capacity_Ah']
        
        # Cycles complets uniquement
        grp = grp[grp['capacity_Ah'] > 0.5].copy()
        if len(grp) == 0:
            continue
        
        grp['cycle_global'] = np.arange(cycle_global + 1, cycle_global + len(grp) + 1)
        grp['source'] = os.path.basename(fpath)
        cycle_global = int(grp['cycle_global'].max())
        all_caps.append(grp[['cycle_global', 'capacity_Ah', 'source']])
    
    df_all = pd.concat(all_caps, ignore_index=True)
    logger.info(f"    {len(df_all)} cycles chargés")
    return df_all


def clean_capacity_data(df: pd.DataFrame, window: int = 20, iqr_threshold: float = 2.0) -> pd.DataFrame:
    """
    Nettoie et interpole les cycles aberrants
    """
    df = df.copy().sort_values('cycle_global').reset_index(drop=True)
    cap = df['capacity_Ah'].values.copy()
    n = len(cap)
    
    aberrants = np.zeros(n, dtype=bool)
    
    for i in range(n):
        lo = max(0, i - window)
        hi = min(n, i + window + 1)
        voisins = np.concatenate([cap[lo:i], cap[i+1:hi]])
        if len(voisins) < 4:
            continue
        q25, q75 = np.percentile(voisins, [25, 75])
        iqr = q75 - q25
        if iqr < 1e-6:
            continue
        if cap[i] < q25 - iqr_threshold * iqr:
            aberrants[i] = True
    
    n_aberrants = aberrants.sum()
    logger.info(f"    Cycles aberrants : {n_aberrants}/{n}")
    
    # Interpolation
    idx_valid = np.where(~aberrants)[0]
    idx_all = np.arange(n)
    cap_interp = np.interp(idx_all, idx_valid, cap[idx_valid])
    
    df['capacity_raw'] = cap
    df['is_aberrant'] = aberrants
    df['capacity_Ah'] = cap_interp
    
    return df


def calculate_soh(df: pd.DataFrame, initial_capacity: float = INITIAL_CAPACITY_MAH) -> pd.DataFrame:
    """
    Calcule SOH à partir de la capacité
    """
    df = df.copy()
    q_ref = df['capacity_Ah'].iloc[0]
    df['Q_ref'] = q_ref
    df['SOH'] = df['capacity_Ah'] / q_ref * 100
    
    # Trouver EOL (premier cycle où SOH <= 80%)
    eol_cycle = None
    soh_vals = df['SOH'].values
    cyc_vals = df['cycle_global'].values
    
    for i in range(len(soh_vals)):
        if soh_vals[i] <= 80:
            eol_cycle = int(cyc_vals[i])
            break
    
    if eol_cycle is None:
        eol_cycle = int(df['cycle_global'].max()) + 1
        logger.info(f"    EOL non atteint (SOH min = {df['SOH'].min():.1f}%)")
    else:
        logger.info(f"    EOL au cycle {eol_cycle}")
    
    df['EOL_cycle'] = eol_cycle
    return df


def extract_features_from_cycle(df_cycle: pd.DataFrame) -> dict:
    """
    Extrait les features d'un cycle de décharge
    """
    # Trouver les colonnes
    vcol = next((c for c in df_cycle.columns if 'voltage' in c.lower()), None)
    icol = next((c for c in df_cycle.columns if 'current' in c.lower()), None)
    tcol = next((c for c in df_cycle.columns 
                 if 'test_time' in c.lower() or 
                    ('time' in c.lower() and 'step' not in c.lower() and 'date' not in c.lower())), None)
    
    if vcol is None or len(df_cycle) < 5:
        return None
    
    v = df_cycle[vcol].values.astype(float)
    t = df_cycle[tcol].values.astype(float) if tcol is not None else np.arange(len(v))
    i = df_cycle[icol].values.astype(float) if icol is not None else np.zeros(len(v))
    
    # Normaliser le temps
    t_norm = (t - t[0]) / (t[-1] - t[0] + 1e-10)
    duration = t[-1] - t[0]
    
    # Tension à 10%, 50%, 90%
    v_10 = np.interp(0.10, t_norm, v)
    v_50 = np.interp(0.50, t_norm, v)
    v_90 = np.interp(0.90, t_norm, v)
    
    # Pente
    slope = np.polyfit(t_norm, v, 1)[0]
    
    # Aire sous courbe
    area = np.trapz(v, t_norm)
    
    features = {
        'V_mean': np.mean(v),
        'V_std': np.std(v),
        'V_min': np.min(v),
        'V_max': np.max(v),
        'V_10pct': v_10,
        'V_50pct': v_50,
        'V_90pct': v_90,
        'V_pente': slope,
        'V_aire': area,
        'I_mean': np.mean(np.abs(i)),
        'I_std': np.std(i),
        'duree_s': duration,
    }
    return features


def build_features_dataset(bid: str, df_labels: pd.DataFrame) -> pd.DataFrame:
    """
    Construit le dataset avec features pour chaque cycle
    """
    bat_path = os.path.join(RAW_DATA_PATH, bid)
    files = sorted(
        [os.path.join(bat_path, f) for f in os.listdir(bat_path) if f.endswith('.xlsx')],
        key=date_from_filename
    )
    
    rows = []
    cycle_global = 0
    
    for fpath in files:
        xl, sheet = get_channel_sheet(fpath)
        if sheet is None:
            continue
        
        df = xl.parse(sheet, header=0)
        df.columns = df.columns.str.strip()
        
        if 'Cycle_Index' not in df.columns:
            continue
        
        # Trouver colonne de capacité
        dcap_col = next(
            (c for c in df.columns if 'discharge' in c.lower() and 'capacity' in c.lower()),
            None
        )
        if dcap_col is None:
            continue
        
        df['Cycle_Index'] = pd.to_numeric(df['Cycle_Index'], errors='coerce')
        df[dcap_col] = pd.to_numeric(df[dcap_col], errors='coerce')
        
        # Cycles complets
        grp = df.groupby('Cycle_Index')[dcap_col].agg(['min', 'max'])
        grp['cap'] = grp['max'] - grp['min']
        cycles_complets = grp[grp['cap'] > 0.5].index.tolist()
        
        for cyc_local in cycles_complets:
            cycle_global += 1
            
            label_row = df_labels[df_labels['cycle_global'] == cycle_global]
            if len(label_row) == 0:
                continue
            
            # Données du cycle (décharge uniquement)
            seg = df[df['Cycle_Index'] == cyc_local].copy()
            icol = next((c for c in seg.columns if 'current' in c.lower()), None)
            if icol:
                seg[icol] = pd.to_numeric(seg[icol], errors='coerce')
                seg = seg[seg[icol] < -0.01]
            
            feats = extract_features_from_cycle(seg)
            if feats is None:
                continue
            
            row = {
                'battery_id': bid,
                'cycle_global': cycle_global,
                'capacity_Ah': float(label_row['capacity_Ah'].iloc[0]),
                'SOH': float(label_row['SOH'].iloc[0]),
                'EOL_cycle': float(label_row['EOL_cycle'].iloc[0]),
            }
            row.update(feats)
            rows.append(row)
    
    df_feat = pd.DataFrame(rows)
    logger.info(f"    Dataset features : {len(df_feat)} cycles, {len(FEATURES_SOH)} features")
    return df_feat


def process_battery(bid: str) -> pd.DataFrame:
    """
    Pipeline complet pour une batterie
    """
    logger.info(f"\n{'='*50}")
    logger.info(f"Traitement de {bid}")
    logger.info(f"{'='*50}")
    
    # 1. Charger capacité brute
    logger.info("[1] Chargement capacité brute...")
    df_capacity = load_capacity_from_excel(bid)
    
    # 2. Nettoyer
    logger.info("[2] Nettoyage...")
    df_clean = clean_capacity_data(df_capacity)
    
    # 3. Calculer SOH
    logger.info("[3] Calcul SOH...")
    df_soh = calculate_soh(df_clean)
    
    # 4. Extraire features
    logger.info("[4] Extraction features...")
    df_features = build_features_dataset(bid, df_soh)
    
    # 5. Sauvegarder
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    output_path = os.path.join(PROCESSED_DATA_PATH, f"dataset_{bid}.csv")
    df_features.to_csv(output_path, index=False)
    logger.info(f"[5] Sauvegardé : {output_path}")
    
    return df_features


def process_all_batteries():
    """
    Traite toutes les batteries
    """
    all_datasets = {}
    
    for bid in BATTERIES.keys():
        df = process_battery(bid)
        all_datasets[bid] = df
    
    # Dataset combiné
    df_combined = pd.concat(all_datasets.values(), ignore_index=True)
    combined_path = os.path.join(PROCESSED_DATA_PATH, "dataset_combined.csv")
    df_combined.to_csv(combined_path, index=False)
    logger.info(f"\n✅ Dataset combiné : {combined_path} ({len(df_combined)} cycles)")
    
    return all_datasets


if __name__ == "__main__":
    process_all_batteries()