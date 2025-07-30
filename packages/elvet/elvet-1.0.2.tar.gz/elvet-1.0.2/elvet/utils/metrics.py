import elvet
import tensorflow as tf


class WatchLR:
    def __init__(self, store_lr: bool = False):
        self.store_lr = store_lr
        self.history = {}
        self.lr = []

    def __call__(self, minimizer: elvet.Minimizer):
        lr = minimizer.optimizer.learning_rate.numpy()
        if self.store_lr:
            self.lr.append(lr)
        return {"lr": lr}


class MSE:
    """
    Mean Square Error
    """

    def __init__(self, y_truth, store_mse: bool = False):
        self.y_truth = y_truth
        self.store_mse = store_mse
        self.mse = []

    def __call__(self, minimizer: elvet.Minimizer):
        yhat = minimizer.model(minimizer.domain)
        mse = tf.reduce_mean((yhat - self.y_truth) ** 2)
        if self.store_mse:
            self.mse.append(mse)
        return {"mse": mse}
