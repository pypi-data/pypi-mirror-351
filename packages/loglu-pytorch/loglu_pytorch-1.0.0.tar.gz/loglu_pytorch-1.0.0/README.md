
## LogLU (Logarithmic Linear Units) — Activation Function

Welcome to **LogLU**, a novel activation function designed to enhance the performance of deep neural networks.

The **Logarithmic Linear Unit (LogLU)** improves convergence speed, stability, and overall model performance. Whether you're working on AI for image recognition, NLP, or other applications, this activation function is designed to make your models more efficient.

### Why LogLU?

Activation functions like ReLU are commonly used, but sometimes a more refined and efficient solution is required. Here’s why LogLU stands out:

- **Faster Convergence**: LogLU helps your models train more quickly, saving time and computational resources.
- **Stability**: It prevents issues like exploding or vanishing gradients, ensuring smooth training.
- **Performance**: LogLU consistently improves accuracy and reduces loss compared to traditional activation functions.

### Installation

To use LogLU, simply install it using the following command:

```bash
pip install loglu-pytorch
```

### Usage

Here’s how to integrate LogLU into your deep learning models.

#### With Pytorch:

```python
import torch
from loglu_pytorch import LogLU

# Define the model
class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.fc1 = nn.Linear(784, 128)
        self.loglu = LogLU()
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.fc1(x)
        x = self.loglu(x)
        x = self.fc2(x)
        return F.softmax(x, dim=1)  # Equivalent to 'softmax' activation in final layer

# Instantiate the model
model = MyModel()

# Print the model summary (you can use torchsummary for a detailed view)
from torchsummary import summary
summary(model, input_size=(1, 784))

```

### How It Works

LogLU combines the smooth characteristics of logarithmic functions with the simplicity of linear functions like ReLU. It maintains gradient flow even in deep networks, ensuring fast and stable learning without the typical issues of gradient vanishing or exploding.

For those interested in the mathematical details:
- If `x > 0`: LogLU behaves as a linear function.
- If `x <= 0`: It adopts a logarithmic form, providing a smoother handling of negative values.

## Feedback & Contributions

If you have feedback or would like to contribute, please feel free to open an issue or contribute on GitHub.

Contact: Email: poorni.m0405@gmail.com, rishichaitanya888@gmail.com



## License

LogLU_Pytorch is released under the [Apache License 2.0](https://github.com/Poorni-Murumuri/loglu-pytorch/blob/main/LICENSE).
