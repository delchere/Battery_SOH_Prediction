#!/usr/bin/env python
"""
Exporte les cycles test en CSV BRUT (données brutes)
Lit la liste des cycles depuis data/tests/test_cycles_list.txt
"""
import pandas as pd
import os

DATA_PATH = "./data"
EXCEL_DIR = os.path.join(DATA_PATH, "raw", "CS2_datasets0.5c", "CS2_34")
OUTPUT_DIR = os.path.join(DATA_PATH, "client_csv")
CYCLES_LIST_FILE = os.path.join(DATA_PATH, "tests", "test_cycles_list.txt")


def get_channel_sheet(filepath):
    try:
        xl = pd.ExcelFile(filepath, engine='openpyxl')
        sheet = next((s for s in xl.sheet_names if s.lower().startswith('channel')), None)
        return xl, sheet
    except Exception:
        return None, None


def extract_raw_cycle(filepath, cycle_local):
    xl, sheet = get_channel_sheet(filepath)
    if sheet is None:
        return None
    
    df = xl.parse(sheet, header=0)
    df.columns = df.columns.str.strip()
    
    if 'Cycle_Index' not in df.columns:
        return None
    
    vcol = next((c for c in df.columns if 'voltage' in c.lower()), None)
    icol = next((c for c in df.columns if 'current' in c.lower()), None)
    tcol = next((c for c in df.columns if 'test_time' in c.lower() or 'time' in c.lower()), None)
    
    if vcol is None or icol is None:
        return None
    
    cycle_data = df[df['Cycle_Index'] == cycle_local].copy()
    if len(cycle_data) == 0:
        return None
    
    cycle_data[icol] = pd.to_numeric(cycle_data[icol], errors='coerce')
    cycle_data = cycle_data[cycle_data[icol] < 0]  # Ne garder que la décharge
    
    if len(cycle_data) == 0:
        return None
    
    result = pd.DataFrame()
    result['temps_s'] = cycle_data[tcol].values if tcol else range(len(cycle_data))
    result['tension_V'] = cycle_data[vcol].values
    result['courant_A'] = cycle_data[icol].values
    
    return result


def main():
    print("=" * 50)
    print("EXPORT CSV BRUT POUR CLIENT")
    print("=" * 50)
    
    if not os.path.exists(CYCLES_LIST_FILE):
        print(f"❌ Fichier non trouvé: {CYCLES_LIST_FILE}")
        print("   Exécutez d'abord: python src/extract_test_cycles.py")
        return
    
    with open(CYCLES_LIST_FILE, 'r') as f:
        test_cycles = [int(line.strip()) for line in f.readlines()]
    
    print(f"📋 Cycles test à exporter: {test_cycles}")
    
    if not os.path.exists(EXCEL_DIR):
        print(f"❌ Dossier non trouvé: {EXCEL_DIR}")
        return
    
    files = sorted([f for f in os.listdir(EXCEL_DIR) if f.endswith('.xlsx')])
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    current_cycle = 0
    exported = []
    
    for fname in files:
        fpath = os.path.join(EXCEL_DIR, fname)
        xl, sheet = get_channel_sheet(fpath)
        
        if sheet is None:
            continue
        
        df = xl.parse(sheet, header=0)
        df.columns = df.columns.str.strip()
        
        if 'Cycle_Index' not in df.columns:
            continue
        
        cycles_in_file = sorted(df['Cycle_Index'].unique())
        
        for cyc_local in cycles_in_file:
            current_cycle += 1
            
            if current_cycle in test_cycles:
                raw_data = extract_raw_cycle(fpath, cyc_local)
                if raw_data is not None:
                    filename = f"cycle_{current_cycle}.csv"
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    raw_data.to_csv(filepath, index=False)
                    exported.append(current_cycle)
                    print(f"✅ cycle_{current_cycle}.csv ({len(raw_data)} points)")
    
    print(f"\n✅ {len(exported)} CSV bruts créés dans: {OUTPUT_DIR}")
    print(f"   Cycles: {sorted(exported)}")


if __name__ == "__main__":
    main()