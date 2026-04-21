"""
API Flask pour la prédiction SOH
L'utilisateur upload un fichier CSV avec les données brutes d'un cycle
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.predict import get_predictor
from src.utils import logger

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    """Health check pour DevOps"""
    return jsonify({
        'status': 'ok',
        'service': 'SOH Predictor',
        'version': '1.0.0'
    }), 200


@app.route('/predict', methods=['POST'])
def predict():
    """
    Prédit le SOH à partir d'un fichier CSV
    
    Utilisation:
        curl -X POST -F "file=@cycle_data.csv" http://localhost:5000/predict
    
    Le CSV doit contenir les colonnes:
        - temps_s
        - tension_V
        - courant_A (optionnel)
        - capacite_mAh (optionnel)
    """
    
    # Vérifier qu'un fichier a été envoyé
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier fourni'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide'}), 400
    
    # Vérifier l'extension
    if not file.filename.endswith(('.csv', '.xlsx')):
        return jsonify({'error': 'Format non supporté. Utilisez CSV ou Excel'}), 400
    
    try:
        # Sauvegarder temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        # Charger et prédire
        predictor = get_predictor()
        
        if file.filename.endswith('.csv'):
            import pandas as pd
            df_raw = pd.read_csv(tmp_path)
        else:
            import pandas as pd
            df_raw = pd.read_excel(tmp_path)
        
        result = predictor.predict_from_dataframe(df_raw)
        
        # Nettoyer
        os.unlink(tmp_path)
        
        return jsonify({
            'success': True,
            'prediction': result
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction : {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/predict/json', methods=['POST'])
def predict_json():
    """
    Prédiction à partir de JSON (pour les intégrations)
    
    Body:
    {
        "temps_s": [0, 1, 2, ...],
        "tension_V": [4.2, 4.19, ...],
        "courant_A": [1.0, 1.0, ...],
        "capacite_mAh": [0, 2.7, ...]
    }
    """
    try:
        data = request.get_json()
        
        import pandas as pd
        df_raw = pd.DataFrame(data)
        
        predictor = get_predictor()
        result = predictor.predict_from_dataframe(df_raw)
        
        return jsonify({
            'success': True,
            'prediction': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
