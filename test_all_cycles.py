"""
Teste les prédictions sur les 10 cycles test jamais vus
Compare SOH réel vs SOH prédit
"""
import pandas as pd
import numpy as np
import joblib
import os

# Configuration
FEATURES_SOH = [
    'V_mean', 'V_std', 'V_min', 'V_max',
    'V_10pct', 'V_50pct', 'V_90pct',
    'V_pente', 'V_aire',
    'I_mean', 'I_std', 'duree_s'
]

# Charger le modèle et le scaler
print("Chargement du modèle...")
model = joblib.load('models_saved/best_model.pkl')
scaler = joblib.load('models_saved/scaler.pkl')
print("✅ Modèle chargé")

# Charger les cycles test
test_path = 'data/tests/test_10_cycles.csv'
test_cycles = pd.read_csv(test_path)
print(f"✅ {len(test_cycles)} cycles test chargés\n")

# Trier par cycle pour un affichage ordonné
test_cycles = test_cycles.sort_values('cycle_global')

print("=" * 70)
print("PRÉDICTIONS SUR LES 10 CYCLES TEST (jamais vus par le modèle)")
print("=" * 70)
print(f"{'Cycle':>6} | {'SOH réel':>10} | {'SOH prédit':>10} | {'Erreur':>8} | {'Statut':>12}")
print("-" * 70)

results = []

for idx, row in test_cycles.iterrows():
    cycle_num = int(row['cycle_global'])
    soh_reel = row['SOH']
    
    # Prendre les features
    X = row[FEATURES_SOH].values.reshape(1, -1)
    X_scaled = scaler.transform(X)
    soh_pred = model.predict(X_scaled)[0]
    
    erreur = soh_pred - soh_reel
    
    # Déterminer le statut
    if soh_pred >= 90:
        status = "excellent"
    elif soh_pred >= 80:
        status = "bon"
    elif soh_pred >= 70:
        status = "attention"
    else:
        status = "critique"
    
    results.append({
        'cycle': cycle_num,
        'soh_reel': soh_reel,
        'soh_pred': soh_pred,
        'erreur': erreur,
        'status': status
    })
    
    # Flèche pour l'erreur
    arrow = "▲" if erreur > 0 else ("▼" if erreur < 0 else "●")
    
    print(f"{cycle_num:>6} | {soh_reel:>10.2f} | {soh_pred:>10.2f} | {erreur:>+7.2f} {arrow} | {status:>12}")

print("-" * 70)

# Statistiques
if results:
    df_results = pd.DataFrame(results)
    
    mae = df_results['erreur'].abs().mean()
    rmse = np.sqrt((df_results['erreur']**2).mean())
    max_err = df_results['erreur'].abs().max()
    
    # Calcul du R²
    ss_res = (df_results['erreur']**2).sum()
    ss_tot = ((df_results['soh_reel'] - df_results['soh_reel'].mean())**2).sum()
    r2 = 1 - (ss_res / ss_tot)
    
    print(f"\n📊 STATISTIQUES:")
    print(f"   MAE  (Erreur absolue moyenne): {mae:.3f}%")
    print(f"   RMSE (Racine erreur quadratique): {rmse:.3f}%")
    print(f"   Max erreur: {max_err:.3f}%")
    print(f"   R² : {r2:.4f}")
    
    print(f"\n📈 RÉSUMÉ:")
    print(f"   ✅ Modèle performant (R² = {r2:.4f})")
    print(f"   📉 Erreur moyenne: {mae:.2f}%")
    
    # Afficher les cycles avec la plus grande erreur
    print(f"\n⚠️ Cycles avec la plus grande erreur:")
    worst = df_results.nlargest(3, 'erreur_abs') if 'erreur_abs' in df_results else df_results
    df_results['erreur_abs'] = df_results['erreur'].abs()
    worst = df_results.nlargest(3, 'erreur_abs')
    for _, w in worst.iterrows():
        print(f"   Cycle {int(w['cycle'])}: erreur = {w['erreur']:+.2f}% (réel={w['soh_reel']:.1f}%, prédit={w['soh_pred']:.1f}%)")

print("\n" + "=" * 70)
print("✅ Test terminé")