
# ZenGrad: Gradient Descent Optimizer 

ZenGrad is a sophisticated gradient descent optimizer designed to provide a stable and controlled optimization process. By prioritizing smooth, gradual transitions and maintaining stability throughout training, ZenGrad minimizes the risk of erratic updates that can hinder model convergence. It is fully compatible with TensorFlow and offers an adaptive approach to model training, ensuring efficient and effective optimization.

## Key Features

- **Smooth Gradient Descent**: ZenGrad ensures stable and consistent updates, facilitating a balanced and effective learning process.
- **Adaptive Optimization**: The optimizer adjusts its parameters based on the loss landscape, improving convergence and training efficiency.
- **Seamless TensorFlow Integration**: ZenGrad is designed to integrate smoothly within the TensorFlow framework, making it easy to implement in deep learning workflows.

## Installation

To install ZenGrad, run the following command:

```bash
pip install zengrad
```

## Example Usage

You can use ZenGrad in your TensorFlow models as shown below:

```python
import tensorflow as tf
from loglu import LogLU
from zengrad import ZenGrad  # ZenGrad Gradient Descent

# Define a model
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(128, input_shape=(784,)),
    tf.keras.layers.Activation(LogLU()),  
    tf.keras.layers.Dense(10, activation='softmax')
])

# Compile the model with ZenGrad optimizer
model.compile(optimizer=ZenGrad(learning_rate=0.01), loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()
```

## Feedback & Contributions

If you have feedback or would like to contribute, please feel free to open an issue or contribute on GitHub.

Contact: Email: poorni.m0405@gmail.com, rishichaitanya888@gmail.com


## License

ZenGrad is released under the [Apache License 2.0](https://github.com/Poorni-Murumuri/ZenGrad/blob/main/LICENSE).