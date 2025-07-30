import numpy as np
import tensorflow as tf
from elvet import Minimizer


class ControlLossSTD:
    def __init__(
        self,
        check_every_iteration: int = 10000,
        rtol_min: float = 0.1,
        scale: float = 0.5,
        store_lr: bool = False,
    ):
        """
        Control the standard deviation of the loss values

        Parameters
        ----------
        check_every_iteration : int, optional
            Updates the learning rate according every such epoch. 
            The default is 10000.
        rtol_min : float, optional
            Minumum alowed ratio of loss std over minimum loss. 
            The default is 0.1.
        scale : float, optional
            Scale of the lr decay. The default is 0.5.
        store_lr : bool, optional
            store lr updates. The default is False.
        """
        self.check_every_iteration = check_every_iteration
        self.rtol_min = rtol_min
        self.scale = scale
        self.store_lr = store_lr
        self.lr = []

    def __call__(self, minimizer: Minimizer):
        if self.store_lr:
            self.lr.append(minimizer.optimizer.lr.numpy())

        if minimizer.epoch % self.check_every_iteration == 0:
            losses = np.array(minimizer.losses[-self.check_every_iteration :])

            if losses.std() / losses.min() > self.rtol_min:
                lr = minimizer.optimizer.lr.numpy()
                tf.keras.backend.set_value(minimizer.optimizer.lr, lr * self.scale)


class ExponentialLRDecay:
    def __init__(
        self,
        decay_rate: float = 0.06,
        decay_steps: int = 10000,
        min_lr: float = 1e-5,
        store_lr: bool = False,
    ):
        """
        Exponential decay for learning rate

        Parameters
        ----------
        decay_rate : float, optional
            The default is 0.06.
        decay_steps : int, optional
            The default is 10000.
        min_lr : float, optional
            Minimum value that learning rate can take. The default is 1e-5.
        store_lr : bool, optional
            Store lr updates. The default is False.
        """
        self.min_lr = min_lr
        self.initial_lr = -1
        self.decay_rate = decay_rate
        self.decay_steps = decay_steps
        self.store_lr = store_lr
        self.lr = []

    def __call__(self, minimizer: Minimizer):
        current_lr = minimizer.optimizer.lr.numpy()
        if self.store_lr:
            self.lr.append(current_lr)

        if self.initial_lr == -1:
            self.initial_lr = current_lr

        lr = lambda step: self.initial_lr * self.decay_rate ** (step / self.decay_steps)

        if minimizer.optimizer.lr >= self.min_lr:
            new_lr = lr(minimizer.epoch)
            new_lr = new_lr if new_lr >= self.min_lr else self.min_lr
            tf.keras.backend.set_value(minimizer.optimizer.lr, new_lr)


class ReduceLROnPlateau:
    def __init__(
        self,
        check_every: int = 20,
        min_lr: float = 1e-5,
        scale: float = 0.5,
        min_improvement_rate: float = 0.01,
        store_lr=False,
    ):
        """
        Reduce learning rate on plateau

        Parameters
        ----------
        check_every : int, optional
            check every such epoch. The default is 20.
        min_lr : float, optional
            Min value that lr can take. The default is 1e-5.
        scale : float, optional
            LR scale factor. The default is 0.5.
        min_improvement_rate : float, optional
            Minimum amount of improvement which does not require lr update.
            The default is 0.01.
        store_lr : TYPE, optional
            Store lr updates. The default is False.
        """
        self.min_lr = min_lr
        self.scale = scale
        self.check_every = check_every
        self.min_improvement_rate = min_improvement_rate
        self.min_loss = 1e99
        self.store_lr = store_lr
        self.lr = []

    def __call__(self, minimizer: Minimizer):
        current_lr = minimizer.optimizer.lr.numpy()
        if self.store_lr:
            self.lr.append(current_lr)

        if current_lr > self.min_lr and minimizer.epoch % self.check_every == 0:

            min_loss = min(minimizer.losses[-self.check_every :])
            if abs(min_loss - self.min_loss) >= self.min_improvement_rate:
                new_lr = current_lr * self.scale
                new_lr = new_lr if new_lr >= self.min_lr else self.min_lr
                tf.keras.backend.set_value(minimizer.optimizer.lr, new_lr)


class InverseTimeDecay:
    def __init__(
        self,
        decay_rate: float = 0.06,
        decay_steps: int = 10000,
        min_lr: float = 1e-5,
        staircase: bool = False,
        store_lr: bool = False,
    ) -> None:
        """
        Inverse time decay for learning rate

        Parameters
        ----------
        decay_rate : float, optional
            The default is 0.06.
        decay_steps : int, optional
            The default is 10000.
        min_lr : float, optional
            Min value that lr can take. The default is 1e-5.
        staircase : bool, optional
            if the function to applied as continuous or staircase.
            The default is False.
        store_lr : bool, optional
            Store lr updates. The default is False.
        """
        self.min_lr = min_lr
        self.initial_lr = -1
        self.decay_rate = decay_rate
        self.decay_steps = decay_steps
        self.staircase = staircase
        self.store_lr = store_lr
        self.lr = []

    def __call__(self, minimizer: Minimizer):
        current_lr = minimizer.optimizer.lr.numpy()
        if self.store_lr:
            self.lr.append(current_lr)

        if self.initial_lr == -1:
            self.initial_lr = current_lr

        if self.staircase:
            lr = lambda step: self.initial_lr / (
                1.0 + self.decay_rate * np.floor(step / self.decay_steps)
            )
        else:
            lr = lambda step: self.initial_lr / (
                1.0 + self.decay_rate * step / self.decay_steps
            )

        if current_lr > self.min_lr:
            tf.keras.backend.set_value(minimizer.optimizer.lr, lr(minimizer.epoch))


class PolynomialDecay:
    def __init__(
        self,
        decay_rate: float =0.06,
        decay_steps: int =10000,
        min_lr : float =1e-5,
        power: float =0.6,
        cycle: bool =False,
        store_lr: bool =False,
    ) -> None:
        """
        Polynomial decay for learning rate

        Parameters
        ----------
        decay_rate : float, optional
            The default is 0.06.
        decay_steps : int, optional
            The default is 10000.
        min_lr : float, optional
            The default is 1e-5.
        power : float, optional
            The default is 0.6.
        cycle : bool, optional
            The default is False.
        store_lr : bool, optional
            store lr updates. The default is False.
        """
        self.min_lr = min_lr
        self.initial_lr = -1
        self.decay_rate = decay_rate
        self.decay_steps = decay_steps
        self.power = power
        self.cycle = cycle
        self.store_lr = store_lr
        self.lr = []

    def __call__(self, minimizer: Minimizer):
        current_lr = minimizer.optimizer.lr.numpy()
        if self.store_lr:
            self.lr.append(current_lr)

        if self.initial_lr == -1:
            self.initial_lr = current_lr

        step = minimizer.epoch

        if not self.cycle:
            lr = (
                (self.initial_lr - self.min_lr)
                * (1.0 - step / self.decay_steps) ** (self.power)
            ) + self.min_lr
        else:
            decay_steps = self.decay_steps * np.ceil(step / self.decay_steps)
            lr = (
                (self.initial_lr - self.min_lr)
                * (1 - step / decay_steps) ** (self.power)
            ) + self.min_lr

        if current_lr > self.min_lr:
            tf.keras.backend.set_value(minimizer.optimizer.lr, tf.abs(tf.math.real(lr)))
