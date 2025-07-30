# bartz/src/bartz/jaxext.py
#
# Copyright (c) 2024-2025, Giacomo Petrillo
#
# This file is part of bartz.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Additions to jax."""

import functools
import math
import warnings

import jax
from jax import lax, random, tree_util
from jax import numpy as jnp
from scipy import special


def float_type(*args):
    """Determine the jax floating point result type given operands/types."""
    t = jnp.result_type(*args)
    return jnp.sin(jnp.empty(0, t)).dtype


def _castto(func, type):
    @functools.wraps(func)
    def newfunc(*args, **kw):
        return func(*args, **kw).astype(type)

    return newfunc


class scipy:
    """Mockup of the :external:py:mod:`scipy` module."""

    class special:
        """Mockup of the :external:py:mod:`scipy.special` module."""

        @staticmethod
        def gammainccinv(a, y):
            """Survival function inverse of the Gamma(a, 1) distribution."""
            a = jnp.asarray(a)
            y = jnp.asarray(y)
            shape = jnp.broadcast_shapes(a.shape, y.shape)
            dtype = float_type(a.dtype, y.dtype)
            dummy = jax.ShapeDtypeStruct(shape, dtype)
            ufunc = _castto(special.gammainccinv, dtype)
            return jax.pure_callback(ufunc, dummy, a, y, vmap_method='expand_dims')

    class stats:
        """Mockup of the :external:py:mod:`scipy.stats` module."""

        class invgamma:
            """Class that represents the distribution InvGamma(a, 1)."""

            @staticmethod
            def ppf(q, a):
                """Percentile point function."""
                return 1 / scipy.special.gammainccinv(a, q)


def vmap_nodoc(fun, *args, **kw):
    """
    Acts like `jax.vmap` but preserves the docstring of the function unchanged.

    This is useful if the docstring already takes into account that the
    arguments have additional axes due to vmap.
    """
    doc = fun.__doc__
    fun = jax.vmap(fun, *args, **kw)
    fun.__doc__ = doc
    return fun


def huge_value(x):
    """
    Return the maximum value that can be stored in `x`.

    Parameters
    ----------
    x : array
        A numerical numpy or jax array.

    Returns
    -------
    maxval : scalar
        The maximum value allowed by `x`'s type (+inf for floats).
    """
    if jnp.issubdtype(x.dtype, jnp.integer):
        return jnp.iinfo(x.dtype).max
    else:
        return jnp.inf


def minimal_unsigned_dtype(value):
    """Return the smallest unsigned integer dtype that can represent `value`."""
    if value < 2**8:
        return jnp.uint8
    if value < 2**16:
        return jnp.uint16
    if value < 2**32:
        return jnp.uint32
    return jnp.uint64


def signed_to_unsigned(int_dtype):
    """
    Map a signed integer type to its unsigned counterpart.

    Unsigned types are passed through.
    """
    assert jnp.issubdtype(int_dtype, jnp.integer)
    if jnp.issubdtype(int_dtype, jnp.unsignedinteger):
        return int_dtype
    if int_dtype == jnp.int8:
        return jnp.uint8
    if int_dtype == jnp.int16:
        return jnp.uint16
    if int_dtype == jnp.int32:
        return jnp.uint32
    if int_dtype == jnp.int64:
        return jnp.uint64


def ensure_unsigned(x):
    """If x has signed integer type, cast it to the unsigned dtype of the same size."""
    return x.astype(signed_to_unsigned(x.dtype))


@functools.partial(jax.jit, static_argnums=(1,))
def unique(x, size, fill_value):
    """
    Restricted version of `jax.numpy.unique` that uses less memory.

    Parameters
    ----------
    x : 1d array
        The input array.
    size : int
        The length of the output.
    fill_value : scalar
        The value to fill the output with if `size` is greater than the number
        of unique values in `x`.

    Returns
    -------
    out : array (size,)
        The unique values in `x`, sorted, and right-padded with `fill_value`.
    actual_length : int
        The number of used values in `out`.
    """
    if x.size == 0:
        return jnp.full(size, fill_value, x.dtype), 0
    if size == 0:
        return jnp.empty(0, x.dtype), 0
    x = jnp.sort(x)

    def loop(carry, x):
        i_out, i_in, last, out = carry
        i_out = jnp.where(x == last, i_out, i_out + 1)
        out = out.at[i_out].set(x)
        return (i_out, i_in + 1, x, out), None

    carry = 0, 0, x[0], jnp.full(size, fill_value, x.dtype)
    (actual_length, _, _, out), _ = jax.lax.scan(loop, carry, x[:size])
    return out, actual_length + 1


def autobatch(func, max_io_nbytes, in_axes=0, out_axes=0, return_nbatches=False):
    """
    Batch a function such that each batch is smaller than a threshold.

    Parameters
    ----------
    func : callable
        A jittable function with positional arguments only, with inputs and
        outputs pytrees of arrays.
    max_io_nbytes : int
        The maximum number of input + output bytes in each batch (excluding
        unbatched arguments.)
    in_axes : pytree of int or None, default 0
        A tree matching the structure of the function input, indicating along
        which axes each array should be batched. If a single integer, it is
        used for all arrays. A `None` axis indicates to not batch an argument.
    out_axes : pytree of ints, default 0
        The same for outputs (but non-batching is not allowed).
    return_nbatches : bool, default False
        If True, the number of batches is returned as a second output.

    Returns
    -------
    batched_func : callable
        A function with the same signature as `func`, but that processes the
        input and output in batches in a loop.
    """

    def expand_axes(axes, tree):
        if isinstance(axes, int):
            return tree_util.tree_map(lambda _: axes, tree)
        return tree_util.tree_map(lambda _, axis: axis, tree, axes)

    def check_no_nones(axes, tree):
        def check_not_none(_, axis):
            assert axis is not None

        tree_util.tree_map(check_not_none, tree, axes)

    def extract_size(axes, tree):
        def get_size(x, axis):
            if axis is None:
                return None
            else:
                return x.shape[axis]

        sizes = tree_util.tree_map(get_size, tree, axes)
        sizes, _ = tree_util.tree_flatten(sizes)
        assert all(s == sizes[0] for s in sizes)
        return sizes[0]

    def sum_nbytes(tree):
        def nbytes(x):
            return math.prod(x.shape) * x.dtype.itemsize

        return tree_util.tree_reduce(lambda size, x: size + nbytes(x), tree, 0)

    def next_divisor_small(dividend, min_divisor):
        for divisor in range(min_divisor, int(math.sqrt(dividend)) + 1):
            if dividend % divisor == 0:
                return divisor
        return dividend

    def next_divisor_large(dividend, min_divisor):
        max_inv_divisor = dividend // min_divisor
        for inv_divisor in range(max_inv_divisor, 0, -1):
            if dividend % inv_divisor == 0:
                return dividend // inv_divisor
        return dividend

    def next_divisor(dividend, min_divisor):
        if dividend == 0:
            return min_divisor
        if min_divisor * min_divisor <= dividend:
            return next_divisor_small(dividend, min_divisor)
        return next_divisor_large(dividend, min_divisor)

    def pull_nonbatched(axes, tree):
        def pull_nonbatched(x, axis):
            if axis is None:
                return None
            else:
                return x

        return tree_util.tree_map(pull_nonbatched, tree, axes), tree

    def push_nonbatched(axes, tree, original_tree):
        def push_nonbatched(original_x, x, axis):
            if axis is None:
                return original_x
            else:
                return x

        return tree_util.tree_map(push_nonbatched, original_tree, tree, axes)

    def move_axes_out(axes, tree):
        def move_axis_out(x, axis):
            return jnp.moveaxis(x, axis, 0)

        return tree_util.tree_map(move_axis_out, tree, axes)

    def move_axes_in(axes, tree):
        def move_axis_in(x, axis):
            return jnp.moveaxis(x, 0, axis)

        return tree_util.tree_map(move_axis_in, tree, axes)

    def batch(tree, nbatches):
        def batch(x):
            return x.reshape((nbatches, x.shape[0] // nbatches) + x.shape[1:])

        return tree_util.tree_map(batch, tree)

    def unbatch(tree):
        def unbatch(x):
            return x.reshape((x.shape[0] * x.shape[1],) + x.shape[2:])

        return tree_util.tree_map(unbatch, tree)

    def check_same(tree1, tree2):
        def check_same(x1, x2):
            assert x1.shape == x2.shape
            assert x1.dtype == x2.dtype

        tree_util.tree_map(check_same, tree1, tree2)

    initial_in_axes = in_axes
    initial_out_axes = out_axes

    @jax.jit
    @functools.wraps(func)
    def batched_func(*args):
        example_result = jax.eval_shape(func, *args)

        in_axes = expand_axes(initial_in_axes, args)
        out_axes = expand_axes(initial_out_axes, example_result)
        check_no_nones(out_axes, example_result)

        size = extract_size((in_axes, out_axes), (args, example_result))

        args, nonbatched_args = pull_nonbatched(in_axes, args)

        total_nbytes = sum_nbytes((args, example_result))
        min_nbatches = total_nbytes // max_io_nbytes + bool(
            total_nbytes % max_io_nbytes
        )
        min_nbatches = max(1, min_nbatches)
        nbatches = next_divisor(size, min_nbatches)
        assert 1 <= nbatches <= max(1, size)
        assert size % nbatches == 0
        assert total_nbytes % nbatches == 0

        batch_nbytes = total_nbytes // nbatches
        if batch_nbytes > max_io_nbytes:
            assert size == nbatches
            warnings.warn(
                f'batch_nbytes = {batch_nbytes} > max_io_nbytes = {max_io_nbytes}'
            )

        def loop(_, args):
            args = move_axes_in(in_axes, args)
            args = push_nonbatched(in_axes, args, nonbatched_args)
            result = func(*args)
            result = move_axes_out(out_axes, result)
            return None, result

        args = move_axes_out(in_axes, args)
        args = batch(args, nbatches)
        _, result = lax.scan(loop, None, args)
        result = unbatch(result)
        result = move_axes_in(out_axes, result)

        check_same(example_result, result)

        if return_nbatches:
            return result, nbatches
        return result

    return batched_func


class split:
    """
    Split a key into `num` keys.

    Parameters
    ----------
    key : jax.dtypes.prng_key array
        The key to split.
    num : int
        The number of keys to split into.
    """

    def __init__(self, key, num=2):
        self._keys = random.split(key, num)

    def __len__(self):
        return self._keys.size

    def pop(self, shape=None):
        """
        Pop one or more keys from the list.

        Parameters
        ----------
        shape : int or tuple of int, optional
            The shape of the keys to pop. If `None`, a single key is popped.
            If an integer, that many keys are popped. If a tuple, the keys are
            reshaped to that shape.

        Returns
        -------
        keys : jax.dtypes.prng_key array
            The popped keys.

        Raises
        ------
        IndexError
            If `shape` is larger than the number of keys left in the list.

        Notes
        -----
        The keys are popped from the beginning of the list, so for example
        ``list(keys.pop(2))`` is equivalent to ``[keys.pop(), keys.pop()]``.
        """
        if shape is None:
            shape = ()
        elif not isinstance(shape, tuple):
            shape = (shape,)
        size_to_pop = math.prod(shape)
        if size_to_pop > self._keys.size:
            raise IndexError(
                f'Cannot pop {size_to_pop} keys from {self._keys.size} keys'
            )
        popped_keys = self._keys[:size_to_pop]
        self._keys = self._keys[size_to_pop:]
        return popped_keys.reshape(shape)
