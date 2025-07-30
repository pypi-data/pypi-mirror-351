import tensorflow as tf
import logging
from elvet import Minimizer

log = logging.getLogger("Elvet")


class SaveModel:
    def __init__(
        self,
        filepath: str = "dennsolver_model.h5",
        save_min_only: bool = True,
        watch_freq: int = 10000,
    ) -> None:
        """
        Save model weights

        Parameters
        ----------
        filepath : str, optional
            File path and name. The default is "dennsolver_model.h5".
        save_min_only : bool, optional
            What to save, every epoch or the min loss values only.
            The default is True.
        watch_freq : int, optional
            Frequency of the checks to be made on the loss. 
            The default is 10000.

        Returns
        -------
        None
        """
        self.filepath = filepath
        self.save_min_only = save_min_only
        self._min_loss = 1e99
        self.watch_freq = watch_freq

    def __call__(self, minimizer: Minimizer) -> bool:
        save = not self.save_min_only
        if minimizer.losses[-1] < self._min_loss and self.save_min_only:
            self._min_loss = minimizer.losses[-1]
            save = True
        if minimizer.epoch % self.watch_freq == 0 and save:
            minimizer.model.save_weights(self.filepath)
            log.info("Model saved in " + self.filepath)
        return False


class EarlyStopping:
    def __init__(self, patience: int = None, min_loss: float = -1) -> None:
        """
        Early stopping

        Parameters
        ----------
        patience : int, optional
            How often should the loss values to be checked. 
            The default is None.
        min_loss : float, optional
            Minimum value that loss can take. The default is -1.

        Returns
        -------
        None
        """
        def _is_greater(patience):
            def is_greater(epoch):
                if patience is None:
                    return False
                return epoch > patience

            return is_greater

        self.patience = _is_greater(patience)
        self.min_loss = min_loss

    def __call__(self, minimizer: Minimizer):
        if self.patience(minimizer.epoch) and tf.math.is_non_decreasing(
            minimizer.losses[-self.patience :]
        ):
            log.warning(
                f"Loss value did not improve in last {self.patience}"
                + " epochs. Terminating."
            )
            return True
        if minimizer.losses[-1] < self.min_loss:
            log.warning(f"Loss is less than {self.min_loss}. Terminating.")
            return True
        return False


class TerminateIf:
    def __init__(
        self, NaN: bool = True, Inf: bool = True, strictly_increasing: bool = True
    ) -> None:
        """
        Terminate if given conditions are satisfied

        Parameters
        ----------
        NaN : bool, optional
            Terminate if loss is NaN. The default is True.
        Inf : bool, optional
            Terminate if loss is inf. The default is True.
        strictly_increasing : bool, optional
            Terminate if loss is increasing. The default is True.

        Returns
        -------
        None
        """
        self.nan = NaN
        self.inf = Inf
        self.strictly_increasing = strictly_increasing

    def __call__(self, minimizer: Minimizer):
        if (
            (tf.math.is_nan(minimizer.losses[-1]) and self.nan)
            or (tf.math.is_inf(minimizer.losses[-1]) and self.inf)
            or (
                tf.math.is_strictly_increasing(minimizer.losses)
                and self.strictly_increasing
            )
        ):
            log.warning("Terminating.")
            return True
        return False
