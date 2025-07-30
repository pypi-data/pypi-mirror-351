# classifier_module.py
import torch

class ProteinClassifier(torch.nn.Module):
    def __init__(self, esm_model, embedding_dim=2560, num_classes=2):
        super().__init__()
        self.esm_model = esm_model
        self.fc = torch.nn.Linear(embedding_dim, num_classes)

    def forward(self, tokens):
        with torch.no_grad():
            results = self.esm_model(tokens, repr_layers=[36])
        embeddings = results["representations"][36].mean(1)
        logits = self.fc(embeddings)
        return logits, embeddings

