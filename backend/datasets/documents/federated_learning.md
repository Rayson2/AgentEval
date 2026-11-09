# Federated Learning and Privacy

Federated learning is a distributed machine learning
approach in which multiple clients collaboratively
train a shared model without directly sharing their
local training datasets.

Advantages:
- Raw training data remains on local devices.
- Reduces centralized data collection.
- Supports distributed model training.

Limitations:
- Model updates may leak private information.
- Model poisoning attacks are possible.
- Non-IID data can reduce model performance.
- Communication overhead can be significant.

Potential privacy mechanisms:
- Differential privacy.
- Secure aggregation.
- Homomorphic encryption.

Conclusion:
Federated learning can improve data privacy, but it
does not guarantee complete privacy protection.
