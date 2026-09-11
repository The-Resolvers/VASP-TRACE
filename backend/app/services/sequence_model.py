import torch
import torch.nn as nn
import os

class PathLSTM(nn.Module):
    def __init__(self, input_size=165, hidden_size=64, num_layers=1):
        super(PathLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x is shape (batch_size, sequence_length, input_size)
        out, (h_n, c_n) = self.lstm(x)
        
        # Take the output from the last time step
        last_out = out[:, -1, :]
        
        # Pass to fully connected and sigmoid
        logits = self.fc(last_out)
        prob = self.sigmoid(logits)
        return prob

def get_pretrained_model():
    model = PathLSTM()
    
    # Use absolute path to guarantee we find ml_artifacts
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model_path = os.path.join(base_dir, "ml_artifacts", "path_lstm.pth")
    
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, weights_only=True))
        print(f"Loaded trained PathLSTM weights from {model_path}")
    else:
        print(f"No trained weights found at {model_path}. Using random initialization.")
    
    model.eval()
    return model
