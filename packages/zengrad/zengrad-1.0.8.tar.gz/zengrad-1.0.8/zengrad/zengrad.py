import tensorflow as tf
from keras import layers, models
from keras.src import initializers, ops
from keras.src.optimizers import optimizer
from keras.src.api_export import keras_export

class ZenGrad(optimizer.Optimizer):
    def __init__(
        self,
        learning_rate=0.01,
        initial_accumulator_value=0.1,
        name="ZenGrad",
        **kwargs,
    ):
        super().__init__(
            learning_rate=learning_rate,
            name=name,
            **kwargs,
        )
        self.initial_accumulator_value = initial_accumulator_value
    def build(self, var_list):
        if self.built:
            return
        super().build(var_list)
        self._accumulators = []
        initializer = initializers.Constant(self.initial_accumulator_value)
        for var in var_list:
            self._accumulators.append(
                self.add_variable(
                    shape=var.shape,
                    initializer=initializer,
                    dtype=var.dtype,
                    name="accumulator",
                )
            )

    def update_step(self, gradient, variable, learning_rate):
        lr = ops.cast(learning_rate, variable.dtype)
        gradient = ops.cast(gradient, variable.dtype)
        accumulator = self._accumulators[self._get_variable_index(variable)]
        self.assign_add(accumulator, ops.square(gradient))
        self.assign_sub(
            variable,
            ops.divide(
                ops.multiply(lr, gradient),
                ops.add(ops.log(ops.add(accumulator, 1)), 1),  
            ),
        )
    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "initial_accumulator_value": self.initial_accumulator_value,
            }
        )
        return config