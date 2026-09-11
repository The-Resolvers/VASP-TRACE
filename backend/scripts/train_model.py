import sys
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np

# Add the parent directory to sys.path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.sequence_model import PathLSTM

def generate_synthetic_data(num_samples=1000, seq_length=3, input_size=165):
    """
    Generates a synthetic dataset of transaction paths.
    - Labels = 1 (Exchange pattern): feature_60 (volume) steadily increases over the sequence.
    - Labels = 0 (Normal transfer): random noise.
    """
    print(f"Generating {num_samples} synthetic transaction sequences...")
    X = np.random.rand(num_samples, seq_length, input_size).astype(np.float32)
    y = np.zeros((num_samples, 1), dtype=np.float32)
    
    # Make 50% of the data "Exchange" (Label 1)
    num_exchanges = num_samples // 2
    y[:num_exchanges] = 1.0
    
    for i in range(num_exchanges):
        # Inject an "exchange deposit" pattern into the sequence
        # e.g. feature index 60 represents 'volume aggregation'
        # It increases exponentially over the sequence
        base_vol = np.random.uniform(0.1, 0.5)
        for t in range(seq_length):
            X[i, t, 60] = base_vol * (2.0 ** t) # Volume grows
            X[i, t, 6] = np.random.uniform(0.8, 1.0) # High velocity
            X[i, t, 30] = 0.0 # Low change-address probability

    # Shuffle the dataset
    indices = np.random.permutation(num_samples)
    X = X[indices]
    y = y[indices]
    
    return torch.tensor(X), torch.tensor(y)

def train():
    # 1. Prepare Data
    X, y = generate_synthetic_data()
    dataset = TensorDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # 2. Initialize Model, Loss, Optimizer
    model = PathLSTM(input_size=165, hidden_size=64, num_layers=1)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 3. Training Loop
    epochs = 50
    print("Starting Training Loop...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        
        for batch_X, batch_y in dataloader:
            optimizer.zero_grad()
            
            # Forward pass
            predictions = model(batch_X)
            loss = criterion(predictions, batch_y)
            
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        avg_loss = total_loss / len(dataloader)
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}")
            
    # 4. Save the trained weights
    os.makedirs("ml_artifacts", exist_ok=True)
    model_path = "ml_artifacts/path_lstm.pth"
    torch.save(model.state_dict(), model_path)
    print(f"\nTraining Complete! Model weights successfully saved to {model_path}")

if __name__ == "__main__":
    train()
