from enum import Enum, auto
from functools import reduce
from itertools import product, chain

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

from elvet.minimizer.minimizer import Minimizer
from elvet.system.exceptions import InvalidInput


class _Plotter:
    """
    Private helper class for plotting 1D and 2D sections of functions
    with multi-dimensional inputs and multi-dimensional outputs.

    * 1D sections are codimension-1 hyperplanes (1 free coordinate) in the
      domain. A plot of the function values as a function of the only free
      coordinate is to be done.

    * 2D sections are codimension-2 hyperplanes (2 free coordinates) in the
      domain. A plot of the space of the 2 free coordinates, coloring each
      point according to the value of the function at it is to be done.

    The user interface for plotting is given by the ``plot_prediction`` and
    ``plot_loss_density`` functions below.

    Parameters
    ----------
    x : np.ndarray
        Of shape (size, dim_x), with ``dim_x = 1`` (for 1D section) or
        ``dim_x = 2`` (for 2D section).

    y : np.ndarray
        Of shape ``(size, dim_y)``. For 1D sections, ``dim_y`` is arbitrary: a graph
        of each component of y will be included in the plot. For 2D sections, ``dim_y``
        must be one.

    y_true : np.ndarray of the same shape as y

    mode : whether to plot 1D sections or 2D sections.
    """

    class Mode(Enum):
        """
        Specifies which section is to be plotted.
        """

        _1D = auto()
        _2D = auto()

    def __init__(self, x, y, y_true, mode):
        self.x = x
        self.y = y
        self.y_true = y_true
        self.mode = mode

    @staticmethod
    def from_minimizer(
        minimizer,
        true_function=None,
        section=(None,),
        section_atol=1e-3,
        component=None,
    ):
        """
        Create a _Plotter object for the prediction of a Minimizer.

        Parameters
        ----------
        minimizer : Minimizer
            the minimizer from which the prediction are to be computed

        true_function : np.ndarray or callable returning np.ndarray
            true values of the output. Must be of the same shape as
            minimizer.prediction() or reshapeable into it.

        section : tuple of ints and Nones
            specifies the hyperplane in domain space to be plotted.
            The number of Nones must be either 1 (for 1D sections)
            or 2 (for 2D sections).

        section_atol : float
            absolute tolerance for a value of x to be picked as part
            of the section. Effectively this makes the section hyperplane
            have some small thickness.

        component : None or int
            specifies which component of the prediction to plot.
            - If prediction.shape == (size, 1), this has no effect.
            - If prediction.shape == (size, dim):
                1. For 1D sections, a None value of components will cause
                   the plot to contain a graph for each component.
                2. For 2D sections, a None value is not allowed, a component
                   of prediction must be picked.
        """

        # Compute the domain, predictions and true values of the output
        domain = minimizer.domain.numpy()
        prediction = minimizer.prediction()
        y_true = _Plotter._prepare_y_true(true_function, domain, prediction.shape)

        # Compute the indices of the x coordinates in the domain that belong
        # to the section
        conditions = (
            np.isclose(domain[:, i], value, atol=section_atol)
            if value is not None
            else np.full(domain.shape[0], True)
            for i, value in enumerate(section)
        )
        section_indices = np.nonzero(reduce(np.logical_and, conditions))

        # Indices of the free x coordinates
        free_index_pos = [i for i, val in enumerate(section) if val is None]

        # Decide whether to plot 1D sections or 2D sections from the number
        # of None values in section, and compute the corresponding x
        if len(free_index_pos) == 1:
            x = domain[section_indices][:, free_index_pos[0]]
            mode = _Plotter.Mode._1D
        elif len(free_index_pos) == 2:
            x = domain[section_indices][:, free_index_pos]
            mode = _Plotter.Mode._2D
        else:
            # @Juan: TODO: log or raise a more concrete Exception
            raise InvalidInput

        # Compute the y for the specified section
        y = prediction[section_indices]
        if component is not None:
            y = prediction[:, [component]]

        # Compute the true values of y for the specified section
        if y_true is not None:
            y_true = y_true[section_indices]
            if component is not None:
                y_true = y_true[:, [component]]

        return _Plotter(x, y, y_true, mode)

    @staticmethod
    def _prepare_y_true(true_function, domain, shape):
        """
        Standardize y_true to a numpy tensor with the same shape as y.

        Parameters
        ----------
        true_function : np.ndarray or callable returning np.ndarray
            true values of the output. Must be of the same shape as
            minimizer.prediction() or reshapeable into it.

        domain : np.ndarray

        shape : tuple of ints
            shape of y, into which y_true must be casted
        """

        if true_function is None:
            return None

        elif isinstance(true_function, np.ndarray):
            return np.reshape(true_function, shape)

        elif isinstance(true_function, tf.Tensor):
            return _Plotter._prepare_y_true(true_function.numpy(), domain, shape)

        elif hasattr(true_function, "__call__"):
            return _Plotter._prepare_y_true(true_function(domain), domain, shape)

        else:
            raise InvalidInput

    def _plot_sections_1d(self, ys, linestyle, label):
        """
        Plot 1D sections.

        Parameters
        ----------
        ys : np.ndarray of shape (size, dim_y) where size == self.x.shape[0]
            values of y to be plotted. If dim_y > 1, a graph for each ys[:, i]
            is included in the same plot.

        linestyle : str

        label : str
        """

        for y_index in range(ys.shape[1]):
            # Included the component number if dim_y > 1
            pre_label = "" if ys.shape[1] == 1 else f"Component {y_index}: "

            plt.plot(
                self.x,
                ys[:, y_index],
                linestyle=linestyle,
                label=(pre_label + label),
            )

    def _as_rectangle(self, ys):
        """
        Reshape ys into a matrix to be fed to plt.imshow
        """
        if ys.shape[1] > 1:
            # @Juan: TODO: log or raise a more concrete Exception
            raise InvalidInput

        xs_0 = np.unique(self.x[:, 0])
        xs_1 = np.unique(self.x[:, 1])

        out = np.zeros((xs_0.shape[0], xs_1.shape[0]))

        for i, x_0 in enumerate(xs_0):
            for j, x_1 in enumerate(xs_1):
                occurrences = np.all(self.x == (x_0, x_1), axis=1)
                if np.any(occurrences):
                    index = np.argmax(occurrences)
                    out[i, j] = ys[index]

        return out

    def _plot_section_2d(self, ys, label):
        """
        Plot 2D sections.

        Parameters
        ----------
        ys : np.ndarray of shape (size, 1)
            values of y to be plotted as the coloring of each point in a 2D
            section of the domain.

        label : str
        """

        ys = self._as_rectangle(ys)

        # left, right, bottom, top of the 2D section
        extent = (
            np.min(self.x[:, 0]),
            np.max(self.x[:, 0]),
            np.min(self.x[:, 1]),
            np.max(self.x[:, 1]),
        )

        a = plt.imshow(
            ys, extent=extent, interpolation="gaussian", norm=plt.Normalize()
        )
        plt.set_cmap("seismic")
        cbar = plt.colorbar(a)
        cbar.set_label(label, fontsize=15)
        plt.xlabel("first coordinate")
        plt.ylabel("second coordinate")

    def plot(self, prediction_label="prediction"):
        """
        Plot the data contained in self.

        Will plot 1D or 2D sections depending on self.mode. If y_true
        is None, just plot the predictions, if it is None:
        - For 1D sections, plot the prediction and the true values.
        - For 2D sections, plot the difference between the predictions
          and the true values.

        Parameters
        ----------
        prediction_label : str
        """

        if self.mode == _Plotter.Mode._1D:
            self._plot_sections_1d(
                ys=self.y,
                linestyle="dashed",
                label=prediction_label,
            )

            if self.y_true is not None:
                self._plot_sections_1d(
                    ys=self.y_true,
                    linestyle="dotted",
                    label="true values",
                )

            plt.legend()

        else:
            if self.y_true is None:
                ys = self.y
                label = prediction_label
            else:
                ys = self.y - self.y_true
                label = "prediction - true values"

            self._plot_section_2d(ys, label)

        plt.show()


def plot_prediction(
    minimizer,
    true_function=None,
    component=None,
    section=(None,),
    section_atol=1e-5,
):
    """
    Plot a 1D or 2D section of the predictions given by a minimizer object.

    For problems with a 1-dimensional domain, this works as expected without
    tuning the optional arguments. That is, one-dimensional plots of the
    predictions will be done.

    For more the more complicated problems, with a higher dimension of the
    domain, one needs to know the following:

    * 1D sections are codimension-1 hyperplanes (1 free coordinate) in the
      domain. A plot of the function values as a function of the only free
      coordinate is to be done.

    * 2D sections are codimension-2 hyperplanes (2 free coordinates) in the
      domain. A plot of the space of the 2 free coordinates, coloring each
      point according to the value of the function at it is to be done.

    This function will plot 1D or 2D sections depending on the number of None
    values in section. 1 None corresponds to 1D sections and 2 to 2D sections.
    Other numbers of None values are not allowed.

    A true_function argument can be passed and then:

    * For 1D sections, will plot the prediction and the true values.

    * For 2D sections, will plot the difference between the predictions and
      the true values.

    If the predictions are multidimensional (that is, of shape (size, dim_y)),
    with dim_y > 1, then a component argument can be passed to specify which
    component of the predictions is to be plotted:

    * For 1D sections, will plot the specified component, or, if not specified,
      all the predictions in the same plot.

    * For 2D sections, the component must be specified.

    Parameters
    ----------
    minimizer : elvet.minimizer.minimizer.Minimizer
        The minimizer from which the prediction are to be computed

    true_function : np.ndarray or callable returning np.ndarray
        True values of the output. Must be of the same shape as
        minimizer.prediction() or reshapeable into it.

    section : tuple of ints and Nones
        Specifies the hyperplane in domain space to be plotted.
        The number of Nones must be either 1 (for 1D sections)
        or 2 (for 2D sections).

    section_atol : float
        Absolute tolerance for a value of x to be picked as part
        of the section. Effectively this makes the section hyperplane
        have some small thickness.

    component : None or int
        specifies which component of the prediction to plot.

        * If prediction.shape == (size, 1), this has no effect.

        * If prediction.shape == (size, dim): for 1D sections, a None value of
          components will cause; for 2D sections, a None value is not allowed, a
          component of prediction must be picked.
    """

    if not isinstance(minimizer, Minimizer):
        raise InvalidInput

    _Plotter.from_minimizer(
        minimizer=minimizer,
        true_function=true_function,
        component=component,
        section=section,
        section_atol=section_atol,
    ).plot()


def plot_losses(minimizer, log=True):
    """
    Plot the loss history.

    Parameters
    ----------
    log : bool
        scale of the yaxis
    """
    plt.plot(minimizer.losses)

    if log:
        plt.yscale("log")

    plt.xlabel("epoch")
    plt.ylabel("loss")
    plt.show()


def plot_loss_density(solver, axis=0):
    """
    Plot 1D or 2D projections of the loss density to assess the quality of the
    fit.

    For problems with a 1-dimensional domain, this works as expected without
    tuning the optional arguments. That is, a one-dimensional plot of the
    loss density will be done.

    For more the more complicated problems, with a higher dimension of the
    domain, one needs to know the following:

    - 1D projections have one free coordinate. A plot of the loss density
      as a function of the only free coordinate is to be done, where at each
      point, the plotted value of the loss density is computed as the sum of
      the loss density over all the remaining coordinates.

    - 2D projections have two free coordinates. A plot of the loss density
      as a function of the two free coordinates is to be done, with the value
      of the loss density at each point given by the coloring. The plotted
      value of the loss density is computed as the sum of the loss density
      over all the remaining coordinates.

    This function will plot 1D or 2D projection depending on the length of
    the axis argument. If axis is a single int or a tuple of length 1, then
    1D projection will be plotted. If it is a tuple of length 2, a 2D
    projection will be plotted. Other lengths of axis are not allowed.

    Parameters
    ----------
    solver : elvet.solver.solver.Solver
        The solver whose loss density is to be plotted.

    axis : int or tuple of ints, default=0
        Specifies the free coordinates of the projection.
    """

    domain = solver.domain.numpy()
    loss_density = solver.loss_density()

    # Reshape the loss density to (size_0, size_1, ...)
    # where size_0 * size_1 * ... = domain.shape[0]
    # and size_i = np.unique(x[:, i]).shape[0]
    uniques = [np.unique(domain[:, i]) for i in range(domain.shape[1])]
    shape = tuple(unique.shape[0] for unique in uniques)
    new_loss_density = np.zeros(shape)

    enumerated_uniques = map(enumerate, uniques)
    for indices_coords in product(*enumerated_uniques):
        indices_coords = list(chain(*indices_coords))
        indices = tuple(indices_coords[::2])
        coords = indices_coords[1::2]

        occurrences = np.all(domain == coords, axis=1)
        if np.any(occurrences):
            index = np.argmax(occurrences)
            new_loss_density.__setitem__(indices, loss_density[index])

    loss_density = new_loss_density

    # Axes over which the loss density is to be summed
    summed_axes = tuple(
        i
        for i in range(domain.shape[1])
        if (
            (isinstance(axis, int) and i != axis)
            or (not isinstance(axis, int) and i not in axis)
        )
    )

    # x and y of the projection, to construct a _Plotter object out of
    if isinstance(axis, int) or len(axis) == 1:
        mode = _Plotter.Mode._1D
        x = uniques[axis]
        y = np.sum(loss_density, axis=summed_axes)
        y = np.reshape(y, (x.shape[0], 1))

    elif len(axis) == 2:
        x = np.stack(
            [x.flatten() for x in np.meshgrid(uniques[axis[0]], uniques[axis[1]])],
            axis=1,
        )
        y = np.sum(loss_density, axis=summed_axes)
        y = np.reshape(y, (x.shape[0], 1))
        mode = _Plotter.Mode._2D

    else:
        # @Juan: TODO: log or raise a more concrete Exception
        raise InvalidInput

    # Use _Plotter to plot the projection as a 'section'
    _Plotter(x, y, y_true=None, mode=mode).plot(prediction_label="loss density")
