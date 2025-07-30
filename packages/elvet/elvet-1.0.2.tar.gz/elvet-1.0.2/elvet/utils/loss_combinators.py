import tensorflow as tf

"""
This module contains various possible loss function calculation methods
for differential equations, to be supplied to the Solver constructor
through the combinator argument.

Custom combinators must satisfy the following:

The argument of the combinator is a tuple containing equations and boundary
conditions. These are iterables of tensors. Each of these tensors has the
same shape as the domain. The combinator is expected to return a scalar.
"""


def weighted_sum_combinator(equations_bcs):
    """
    Calculates sum of:
    * The mean of the square of the equations.
    * The sum of the square of the boundaries.

    Using the mean for equations makes the combination more stable against
    changes in the number of points in the domain.

    (see elvet.utils.loss_combinator module documentation for a specifications of
    the arguments and return values of a combinator)
    """
    equations, bcs = equations_bcs

    loss_equations = sum(tf.reduce_mean(equation ** 2) for equation in equations)
    loss_bcs = sum(tf.reduce_sum(bc ** 2) for bc in bcs)

    return loss_equations + loss_bcs


def sum_combinator(equations_bcs):
    """
    Calculates the sum of the squares of the arguments.

    (see elvet.utils.loss_combinator module documentation for a specifications of
    the arguments and return values of a combinator)
    """
    equations, bcs = equations_bcs

    loss_equations = sum(tf.reduce_sum(equation ** 2) for equation in equations)
    loss_bcs = sum(tf.reduce_sum(bc ** 2) for bc in bcs)

    return loss_equations + loss_bcs


def one_to_one_combinator(combinator=tf.reduce_mean):
    """
    Calculates the loss of each input, then takes the mean.
    combinator: tf.reduce_mean, tf.reduce_sum.

    (see elvet.utils.loss_combinator module documentation for a specifications of
    the arguments and return values of a combinator)
    """

    def loss(equations_bcs):
        equations, bcs = equations_bcs

        loss_equations = sum(equation ** 2 for equation in equations)
        loss_bcs = sum(bc ** 2 for bc in bcs)
        return combinator(loss_equations + loss_bcs)

    return loss
