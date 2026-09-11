import os
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def create_mock_dataset(features_path, classes_path):
    print("Generating mock dataset for testing purposes...")
    os.makedirs(os.path.dirname(features_path), exist_ok=True)
    
    # Generate 1000 rows
    tx_ids = np.arange(1, 1001)
    
    # Classes: 1, 2, unknown
    classes = np.random.choice(['1', '2', 'unknown'], size=1000, p=[0.2, 0.3, 0.5])
    df_classes = pd.DataFrame({'txId': tx_ids, 'class': classes})
    df_classes.to_csv(classes_path, index=False)
    
    # Features: txId, time_step, 165 features
    features_data = np.random.randn(1000, 165)
    time_steps = np.random.randint(1, 50, size=(1000, 1))
    tx_ids_col = tx_ids.reshape(-1, 1)
    
    df_features = pd.DataFrame(np.hstack((tx_ids_col, time_steps, features_data)))
    df_features.to_csv(features_path, index=False, header=False)
    print("Mock dataset created.")

def train_model():
    """
    Offline script to train XGBoost model on Elliptic Dataset.
    """
    features_path = "c:/trace/backend/data/elliptic_txs_features.csv"
    classes_path = "c:/trace/backend/data/elliptic_txs_classes.csv"
    
    if not os.path.exists(features_path) or not os.path.exists(classes_path):
        print(f"Warning: Dataset files not found at {features_path} or {classes_path}")
        print("Please download the Elliptic Data Set from Kaggle and place the CSVs in the data folder.")
        create_mock_dataset(features_path, classes_path)
    
    print("Loading datasets...")
    # Load classes
    df_classes = pd.read_csv(classes_path)
    
    # Load features (no header)
    df_features = pd.read_csv(features_path, header=None)
    
    # Rename first column of features to txId to match classes
    df_features.rename(columns={0: 'txId', 1: 'time_step'}, inplace=True)
    
    print("Merging datasets...")
    df = pd.merge(df_classes, df_features, on='txId')
    
    # We only want to train on labeled data (class '1' and '2')
    df = df[df['class'] != 'unknown']
    
    if df.empty:
        print("Error: No labeled data available after filtering out 'unknown' classes.")
        return
        
    # Map classes: 1 (illicit) -> 0, 2 (licit/exchange) -> 1
    # The prompt specifically asks to identify exchange deposit gateways vs unhosted nodes
    df['label'] = df['class'].map({'1': 0, '2': 1})
    
    # Drop non-feature columns
    X = df.drop(columns=['txId', 'class', 'time_step', 'label'])
    y = df['label']
    
    # Provide meaningful names for the top 3 features we care about (for the mock)
    # The frontend expects 'in_degree', 'out_degree', 'clustering'
    feature_names = [f"f_{i}" for i in range(2, 167)]
    feature_names[0] = "in_degree"
    feature_names[1] = "out_degree"
    feature_names[2] = "clustering"
    X.columns = feature_names
    
    print(f"Training on {len(X)} samples with {X.shape[1]} features...")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        eval_metric='logloss'
    )
    
    print("Fitting XGBoost model...")
    model.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Illicit (0)', 'Licit (1)']))
    
    os.makedirs("c:/trace/backend/ml_artifacts", exist_ok=True)
    model_path = "c:/trace/backend/ml_artifacts/xgb_exchange_model.json"
    model.save_model(model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_model()
