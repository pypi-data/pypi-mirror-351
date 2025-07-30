**zlib_into** allows Python code to compress & decompress data into a
preallocated buffer.

The `zlib module <https://docs.python.org/3/library/zlib.html>`_ in the Python
standard library provides an interface to zlib, a common library for Deflate
compression, but always automatically allocates memory for the output.

zlib_into defines two functions:

.. code-block:: python

    compress_into(data, output, level=-1, wbits=15)

    decompress_into(data, output, wbits=15)

In each case, ``output`` can be a ``bytearray``, ``memoryview``, Numpy array,
or anything else compatible with Python's buffer protocol exposing a contiguous,
writable chunk of memory.

The other parameters have the same meanings as in `zlib.compress
<https://docs.python.org/3/library/zlib.html#zlib.compress>`_ and
`zlib.decompress <https://docs.python.org/3/library/zlib.html#zlib.decompress>`_.

This can be useful for:

- Decompressing regular chunks of a known size: you can allocate a single
  output array and fill each chunk directly, avoiding an extra copy.
- Compressing chunks when you want to skip compression if it would make the data
  larger: use a fixed-size buffer matching the input chunk size. Again you can
  avoid unnecessary memory allocations by reusing the buffer.
- Imposing a size limit on decompressed data: it will stop decompressing (and
  throw an error) when the buffer is full, instead of decompressing the whole
  thing to see how big it is. But note that security on untrusted input is not
  the primary goal of this library.
