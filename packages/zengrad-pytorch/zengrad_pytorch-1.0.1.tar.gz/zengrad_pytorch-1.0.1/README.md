
# ZenGrad: Gradient Descent Optimizer 

ZenGrad is a sophisticated gradient descent optimizer designed to provide a stable and controlled optimization process. By prioritizing smooth, gradual transitions and maintaining stability throughout training, ZenGrad minimizes the risk of erratic updates that can hinder model convergence. It is fully compatible with TensorFlow and offers an adaptive approach to model training, ensuring efficient and effective optimization.

## Installation

To install ZenGrad, run the following command:

```bash
pip install zengrad-pytorch
```

## Example Usage

You can use ZenGrad in your TensorFlow models as shown below:

```python
import torch
from zengrad_pytorch import ZenGrad  # Custom optimizer

# Define the model

# Instantiate the model
model = SimpleModel()

# Define loss function
criterion = nn.CrossEntropyLoss()

# Instantiate optimizer
optimizer = ZenGrad(model.parameters(), lr=0.01)

# Model summary (optional)
print(model)

```

## Feedback & Contributions

If you have feedback or would like to contribute, please feel free to open an issue or contribute on GitHub.

Contact: Email: poorni.m0405@gmail.com, rishichaitanya888@gmail.com

## License

ZenGrad_pytorch is released under the [Apache License 2.0](https://github.com/Rishichaitanya-Nalluri/zengrad-pytorch/blob/main/LICENSE).