"""


        nvCOMP Python API reference

        This is the Python API reference for the NVIDIA® nvCOMP library.
    
"""
from __future__ import annotations
import typing
__all__ = ['Array', 'ArrayBufferKind', 'BitstreamKind', 'COMPUTE_AND_NO_VERIFY', 'COMPUTE_AND_VERIFY', 'COMPUTE_AND_VERIFY_IF_PRESENT', 'ChecksumPolicy', 'Codec', 'CudaStream', 'NO_COMPUTE_AND_VERIFY_IF_PRESENT', 'NO_COMPUTE_NO_VERIFY', 'STRIDED_DEVICE', 'STRIDED_HOST', 'as_array', 'as_arrays', 'from_dlpack', 'set_device_allocator', 'set_host_allocator', 'set_pinned_allocator']
class Array:
    """
    Class which wraps array. It can be decoded data or data to encode.
    """
    def __buffer__(self, flags):
        """
        Return a buffer object that exposes the underlying memory of the object.
        """
    def __dlpack__(self, stream: typing.Any = None) -> capsule:
        """
        Export the array as a DLPack tensor
        """
    def __dlpack_device__(self) -> tuple:
        """
        Get the device associated with the buffer
        """
    def __init__(self, src_object: typing.Any, cuda_stream: int = 0) -> None:
        """
                    Creates array from object with some standard interface. 
                    
                    Args:
                        src_object: Source object to create Array based on.
        
                        cuda_stream: An optional cudaStream_t represented as a Python integer, 
                                     upon which synchronization must take place in created Array.
        """
    def __release_buffer__(self, buffer):
        """
        Release the buffer object that exposes the underlying memory of the object.
        """
    def cpu(self) -> typing.Any:
        """
                    Returns a copy of this array in CPU memory. If this array is already in CPU memory, 
                    than no copy is performed and the original object is returned. 
                    
                    Returns:
                        Array object with content in CPU memory or None if copy could not be done.
        """
    def cuda(self, synchronize: bool = True, cuda_stream: int = 0) -> typing.Any:
        """
                    Returns a copy of this array in device memory. If this array is already in device memory, 
                    than no copy is performed and the original object is returned.  
                    
                    Args:
                        synchronize: If True (by default) it blocks and waits for copy from host to device to be finished, 
                                     else not synchronization is executed and further synchronization needs to be done using
                                     cuda stream provided by e.g. \\_\\_cuda_array_interface\\_\\_. 
                        cuda_stream: An optional cudaStream_t represented as a Python integer to copy host buffer to.
        
                    Returns:
                        Array object with content in device memory or None if copy could not be done.
        """
    def to_dlpack(self, cuda_stream: typing.Any = None) -> capsule:
        """
                    Export the array with zero-copy conversion to a DLPack tensor. 
                    
                    Args:
                        cuda_stream: An optional cudaStream_t represented as a Python integer, 
                                     upon which synchronization must take place in created Array.
        
                    Returns:
                        DLPack tensor which is encapsulated in a PyCapsule object.
        """
    @property
    def __array_interface__(self) -> dict:
        """
                    The array interchange interface compatible with Numba v0.39.0 or later (see 
                    `CUDA Array Interface <https://numba.readthedocs.io/en/stable/cuda/cuda_array_interface.html>`_ for details)
        """
    @property
    def __cuda_array_interface__(self) -> dict:
        """
                    The CUDA array interchange interface compatible with Numba v0.39.0 or later (see 
                    `CUDA Array Interface <https://numba.readthedocs.io/en/stable/cuda/cuda_array_interface.html>`_ for details)
        """
    @property
    def buffer_kind(self) -> ArrayBufferKind:
        """
        Buffer kind in which array data is stored.
        """
    @property
    def buffer_size(self) -> int:
        """
        The total number of bytes to store the array.
        """
    @property
    def dtype(self) -> numpy.dtype[typing.Any]:
        ...
    @property
    def item_size(self) -> int:
        """
        Size of each element in bytes.
        """
    @property
    def ndim(self) -> int:
        ...
    @property
    def precision(self) -> int:
        """
        Maximum number of significant bits in data type. Value 0 
                means that precision is equal to data type bit depth
        """
    @property
    def shape(self) -> tuple:
        ...
    @property
    def size(self) -> int:
        """
        Number of elements this array holds.
        """
    @property
    def strides(self) -> tuple:
        """
        Strides of axes in bytes
        """
class ArrayBufferKind:
    """
    Defines buffer kind in which array data is stored.
    
    Members:
    
      STRIDED_DEVICE : GPU-accessible in pitch-linear layout.
    
      STRIDED_HOST : Host-accessible in pitch-linear layout.
    """
    STRIDED_DEVICE: typing.ClassVar[ArrayBufferKind]  # value = <ArrayBufferKind.STRIDED_DEVICE: 1>
    STRIDED_HOST: typing.ClassVar[ArrayBufferKind]  # value = <ArrayBufferKind.STRIDED_HOST: 2>
    __members__: typing.ClassVar[dict[str, ArrayBufferKind]]  # value = {'STRIDED_DEVICE': <ArrayBufferKind.STRIDED_DEVICE: 1>, 'STRIDED_HOST': <ArrayBufferKind.STRIDED_HOST: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class BitstreamKind:
    """
    Defines how buffer will be compressed in nvcomp
    
    Members:
    
      NVCOMP_NATIVE : Each input buffer is chunked according to manager setting and compressed in parallel. Allows computation of checksums. Adds custom header with nvCOMP metadata at the beginning of the compressed data.
    
      RAW : Compresses input data as is, just using underlying compression algorithm. Does not add header with nvCOMP metadata.
    
      WITH_UNCOMPRESSED_SIZE : Similar to RAW, but adds custom header with just uncompressed size at the beginning of the compressed data.
    """
    NVCOMP_NATIVE: typing.ClassVar[BitstreamKind]  # value = <BitstreamKind.NVCOMP_NATIVE: 0>
    RAW: typing.ClassVar[BitstreamKind]  # value = <BitstreamKind.RAW: 1>
    WITH_UNCOMPRESSED_SIZE: typing.ClassVar[BitstreamKind]  # value = <BitstreamKind.WITH_UNCOMPRESSED_SIZE: 2>
    __members__: typing.ClassVar[dict[str, BitstreamKind]]  # value = {'NVCOMP_NATIVE': <BitstreamKind.NVCOMP_NATIVE: 0>, 'RAW': <BitstreamKind.RAW: 1>, 'WITH_UNCOMPRESSED_SIZE': <BitstreamKind.WITH_UNCOMPRESSED_SIZE: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class ChecksumPolicy:
    """
    Defines strategy to compute and verify checksum.
    
    Members:
    
      NO_COMPUTE_NO_VERIFY : During compression, do not compute checksums. During decompression, do not verify checksums
    
      COMPUTE_AND_NO_VERIFY : During compression, compute checksums. During decompression, do not attempt to verify checksums
    
      NO_COMPUTE_AND_VERIFY_IF_PRESENT : During compression, do not compute checksums. During decompression, verify checksums if they were included
    
      COMPUTE_AND_VERIFY_IF_PRESENT : During compression, compute checksums. During decompression, verify checksums if they were included
    
      COMPUTE_AND_VERIFY : During compression, compute checksums. During decompression, verify checksums. A runtime error will be thrown if checksums were not included in the compressed array
    """
    COMPUTE_AND_NO_VERIFY: typing.ClassVar[ChecksumPolicy]  # value = <ChecksumPolicy.COMPUTE_AND_NO_VERIFY: 1>
    COMPUTE_AND_VERIFY: typing.ClassVar[ChecksumPolicy]  # value = <ChecksumPolicy.COMPUTE_AND_VERIFY: 4>
    COMPUTE_AND_VERIFY_IF_PRESENT: typing.ClassVar[ChecksumPolicy]  # value = <ChecksumPolicy.COMPUTE_AND_VERIFY_IF_PRESENT: 3>
    NO_COMPUTE_AND_VERIFY_IF_PRESENT: typing.ClassVar[ChecksumPolicy]  # value = <ChecksumPolicy.NO_COMPUTE_AND_VERIFY_IF_PRESENT: 2>
    NO_COMPUTE_NO_VERIFY: typing.ClassVar[ChecksumPolicy]  # value = <ChecksumPolicy.NO_COMPUTE_NO_VERIFY: 0>
    __members__: typing.ClassVar[dict[str, ChecksumPolicy]]  # value = {'NO_COMPUTE_NO_VERIFY': <ChecksumPolicy.NO_COMPUTE_NO_VERIFY: 0>, 'COMPUTE_AND_NO_VERIFY': <ChecksumPolicy.COMPUTE_AND_NO_VERIFY: 1>, 'NO_COMPUTE_AND_VERIFY_IF_PRESENT': <ChecksumPolicy.NO_COMPUTE_AND_VERIFY_IF_PRESENT: 2>, 'COMPUTE_AND_VERIFY_IF_PRESENT': <ChecksumPolicy.COMPUTE_AND_VERIFY_IF_PRESENT: 3>, 'COMPUTE_AND_VERIFY': <ChecksumPolicy.COMPUTE_AND_VERIFY: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Codec:
    def __enter__(self) -> typing.Any:
        """
        Enter the runtime context related to this codec.
        """
    def __exit__(self, exc_type: type | None = None, exc_value: typing.Any | None = None, traceback: typing.Any | None = None) -> None:
        """
        Exit the runtime context related to this codec and releases allocated resources.
        """
    def __init__(self, **kwargs) -> None:
        """
                    Initialize codec.
        
                    Args:
                        algorithm: An optional name of compression algorithm to use. By default it is empty and algorithm can be deducted during decoding.
                        device_id: An optional device id to execute decoding/encoding on. If not specified default device will be used.
                        cuda_stream: An optional cudaStream_t represented as a Python integer. By default internal cuda stream is created for given device id.
                        uncomp_chunk_size: An optional uncompressed data chunk size. By default it is 65536.
                        checksum_policy: Defines strategy for computing and verification of checksum. By default ``NO_COMPUTE_NO_VERIFY`` is assumed.
        
                      LZ4 algorithm specific options:
                        data_type: An optional array-protocol type string for default data type to use.
        
                      GDeflate algorithm specific options:
                        algorithm_type: Compression algorithm type to use. Permitted values are:
                          * 0 : highest-throughput, entropy-only compression (use for symmetric compression/decompression performance)
                          * 1 : high-throughput, low compression ratio (default)
                          * 2 : medium-throughput, medium compression ratio, beat Zlib level 1 on the compression ratio
                          * 3 : placeholder for further compression level support, will fall into ``MEDIUM_COMPRESSION`` at this point
                          * 4 : lower-throughput, higher compression ratio, beat Zlib level 6 on the compression ratio
                          * 5 : lowest-throughput, highest compression ratio
        
                      Deflate algorithm specific options:
                        algorithm_type: Compression algorithm type to use. Permitted values are:
                          * 0 : highest-throughput, entropy-only compression (use for symmetric compression/decompression performance)
                          * 1 : high-throughput, low compression ratio (default)
                          * 2 : medium-throughput, medium compression ratio, beat Zlib level 1 on the compression ratio
                          * 3 : placeholder for further compression level support, will fall into ``MEDIUM_COMPRESSION`` at this point
                          * 4 : lower-throughput, higher compression ratio, beat Zlib level 6 on the compression ratio
                          * 5 : lowest-throughput, highest compression ratio
        
                      Bitcomp algorithm specific options:
                        algorithm_type: The type of Bitcomp algorithm used.
                          * 0 : Default algorithm, usually gives the best compression ratios
                          * 1 : "Sparse" algorithm, works well on sparse data (with lots of zeroes).
                            and is usually a faster than the default algorithm.
        
                        data_type: An optional array-protocol type string for default data type to use.
        
                      ANS algorithm specific options:
                        data_type: An optional array-protocol type string for default data type to use. Permitted values are:
                          * ``|u1`` : For unsigned 8-bit integer
                          * ``<f2`` : For 16-bit little-endian float. Requires uncomp_chunk_size to be multiple of 2
        
                      Cascaded algorithm specific options:
                        data_type: An optional array-protocol type string for default data type to use.
        
                        num_rles: The number of Run Length Encodings to perform. By default equal to 2
        
                        num_deltas: The number of Delta Encodings to perform. By default equal to 1
        
                        use_bitpack: Whether or not to bitpack the final layers. By default it is True.
        """
    @typing.overload
    def decode(self, src: Array, data_type: str = '') -> typing.Any:
        """
                    Executes decoding of data from a Array handle.
        
                    Args:
                        src: Decode source object.
        
                        data_type: An optional array-protocol type string for output data type. By default it is equal to ``|u1``.
        
                    Returns:
                        nvcomp.Array
        """
    @typing.overload
    def decode(self, srcs: list[Array], data_type: str = '') -> list[typing.Any]:
        """
                  Executes decoding from a batch of Array handles.
        
                  Args:
                      srcs: List of Array objects
        
                      data_type: An optional array-protocol type string for output data type.
        
                  Returns:
                      List of decoded nvcomp.Array's
        """
    @typing.overload
    def encode(self, array_s: Array) -> typing.Any:
        """
                    Encode array.
        
                    Args:
                        array: Array to encode
        
                    Returns:
                        Encoded nvcomp.Array
        """
    @typing.overload
    def encode(self, srcs: list[Array]) -> list[typing.Any]:
        """
                  Executes encoding from a batch of Array handles.
        
                  Args:
                      srcs: List of Array objects
        
                  Returns:
                      List of encoded nvcomp.Array's
        """
class CudaStream:
    """
    
          Wrapper around a CUDA stream.
          Provides either shared-ownership or view semantics, depending on whether it was constructed through `borrow` or `make_new`, respectively.
          
          `CudaStream` is the type of stream parameters passed to allocation functions that can be used with `set_*_allocator`.
          If the deallocation of such memory needs to access the stream passed to the allocation function,
          the allocation function should return an `ExternalMemory` instance wrapping the newly constructed memory object and the `CudaStream` argument.
          The memory object should, from then on, only be accessed through the `ExternalMemory` wrapper.
          This ensures that the stream is still alive when the memory is deallocated.
    
          It is not envisioned that `CudaStream` will be used outside allocation functions. Nevertheless, `borrow` and `make_new` are provided for completeness.
        
    """
    @staticmethod
    def borrow(cuda_stream: int, device_idx: int = -1) -> CudaStream:
        """
                Create a stream view.
        
                The device index is primarily intended for special CUDA streams (i.e., the default, legacy, and per-thread streams) whose device cannot be inferred from the stream value itself. By default, it is equal to -1, a special value whose meaning depends on whether `stream` is special or not. If `stream` is special, the default value associates the shared stream with the current device. Otherwise, the `CudaStream` will always be associated with the stream's actual device. In this case, passing a `device_idx` that is neither the default value nor the stream's actual device will raise an exception.
                
                Args:
                    cuda_stream: The `cudaStream_t` to wrap, represented as a Python integer.
                    device_idx: Optional index of the device with which to associate the borrowed stream. See function description for details. Equal to -1 by default.
        """
    @staticmethod
    def make_new(device_idx: int = -1) -> CudaStream:
        """
                Create a new stream with shared ownership.
                
                Args:
                    device_idx: Optional index of the device with which to associate the newly created stream. By default equal to -1, a special value that represents the current device.
        """
    @property
    def device(self) -> int:
        """
                The device index associated with the stream.
        """
    @property
    def is_special(self) -> bool:
        """
                Whether the underlying stream is one of the special streams (default, legacy, or per-thread).
        
                Note that passing a special stream to any CUDA API call will actually pass the current device's corresponding special stream. It must therefore be ensured that the stream's associated device, as given by `device`, is selected before using the stream. This is currently entirely the user's responsibility.
        """
    @property
    def ptr(self) -> int:
        """
                The underlying `cudaStream_t` represented as a Python integer.
        
                The property name follows the convention of `cupy.Stream` and reflects the fact that a `cudaStream_t` is internally a pointer.
        """
def as_array(source: typing.Any, cuda_stream: int = 0) -> Array:
    """
            Wraps an external buffer as an array and ties the buffer lifetime to the array
    
            Args:
                source: Input DLPack tensor which is encapsulated in a PyCapsule object or other object 
                        with __cuda_array_interface__, __array_interface__ or __dlpack__ and __dlpack_device__ methods.
                
                cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place in the created Array.
    
            Returns:
                nvcomp.Array
    """
def as_arrays(sources: list[typing.Any], cuda_stream: int = 0) -> list[typing.Any]:
    """
                Wraps all an external buffers as an arrays and ties the buffers lifetime to the arrays
    
                Args:
                    sources: List of input DLPack tensors which is encapsulated in a PyCapsule objects or other objects 
                             with __cuda_array_interface__, __array_interface__ or __dlpack__ and __dlpack_device__ methods.
                    
                    cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place in created Array.
    
                Returns:
                    List of nvcomp.Array's
    """
def from_dlpack(source: typing.Any, cuda_stream: int = 0) -> Array:
    """
                Zero-copy conversion from a DLPack tensor to a array. 
    
                Args:
                    source: Input DLPack tensor which is encapsulated in a PyCapsule object or other (array) object 
                            with __dlpack__  and __dlpack_device__ methods.
                    
                    cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place in created Array.
                
                Returns:
                    nvcomp.Array
    """
def set_device_allocator(allocator: typing.Any = None) -> None:
    """
                Sets a new allocator to be used for future device allocations.
    
                The signature of the allocator should be like in the following example::
    
                    def my_allocator(nbytes: int, stream: nvcomp.Stream) -> PtrProtocol:
                        return MyBuffer(nbytes, stream)
                
                `PtrProtocol` denotes any object that has a `ptr` attribute of integral type.
                This should be the pointer to the allocated buffer (represented as an integer).
                
                In the signature, `nbytes` is the number of bytes in the requested buffer.
                `stream` is the CUDA stream on which to perform the allocation and/or deallocation
                if the allocator is stream-ordered. Non-stream-ordered allocators may ignore
                `stream` or may synchronize with it before deallocation, depending on the desired
                behavior. A separate allocation and deallocation stream are currently not supported.
    
                The returned object should be such that, when it is deleted, either on account of there
                being no more valid Python references to it or because it was garbage collected, the
                memory gets deallocated. In a custom Python class, this may be achieved through
                the `__del__` method. This is considered an advanced usage pattern, so
                the recommended approach is to compose pre-existing solutions from other
                libraries, such as cupy's `Memory` classes and rmm's `DeviceBuffer`.
    
                It is generally allowed to set a new allocator while one or more buffers
                allocated by the previous allocator are still active. Individual allocator
                implementations may, however, choose to prohibit this.
    
                If the deallocation requires accessing `stream`, the allocator should return
                an `ExternalMemory` instance wrapping the newly constructed memory object and the `CudaStream` argument.
                The memory object should, from then on, only be accessed through the `ExternalMemory` wrapper.
                This ensures that the stream is still alive when the memory is deallocated.
    
                A simple but versatile example of a custom allocator is given by `rmm_nvcomp_allocator`.
    
                The allocated memory must be device-accessible.
    
                Args:
                    allocator: Callable satisfying the conditions above.
    """
def set_host_allocator(allocator: typing.Any = None) -> None:
    """
                Sets a new allocator to be used for future non-pinned host allocations.
    
                This is primarily intended for potentially large allocations,
                such as those backing CPU Array instances. Moderately-sized internal
                host allocations may still use System Allocated Memory.
    
                This should allocate non-pinned host memory. For pinned host memory,
                use `set_pinned_allocator`. It is not an error to allocate pinned
                host memory with this allocator but may lead to performance degradation.
    
                The allocator must allocate host accessible memory. Other than that, the conditions on
                `allocator` are the same as in `set_device_allocator`, including stream semantics.
    
                Args:
                    allocator: Callable satisfying the conditions above.
    """
def set_pinned_allocator(allocator: typing.Any = None) -> None:
    """
                Sets a new allocator to be used for future pinned host allocations.
    
                Note that his should allocate pinned host memory. For non-pinned host memory,
                use `set_host_allocator`. It is not an error to allocate non-pinned
                host memory with this allocator but may lead to performance degradation.
    
                The allocator must allocate host accessible memory. Other than that, the conditions on
                `allocator` are the same as in `set_device_allocator`, including stream semantics.
    
                Args:
                    allocator: Callable satisfying the conditions above.
    """
COMPUTE_AND_NO_VERIFY: ChecksumPolicy  # value = <ChecksumPolicy.COMPUTE_AND_NO_VERIFY: 1>
COMPUTE_AND_VERIFY: ChecksumPolicy  # value = <ChecksumPolicy.COMPUTE_AND_VERIFY: 4>
COMPUTE_AND_VERIFY_IF_PRESENT: ChecksumPolicy  # value = <ChecksumPolicy.COMPUTE_AND_VERIFY_IF_PRESENT: 3>
NO_COMPUTE_AND_VERIFY_IF_PRESENT: ChecksumPolicy  # value = <ChecksumPolicy.NO_COMPUTE_AND_VERIFY_IF_PRESENT: 2>
NO_COMPUTE_NO_VERIFY: ChecksumPolicy  # value = <ChecksumPolicy.NO_COMPUTE_NO_VERIFY: 0>
STRIDED_DEVICE: ArrayBufferKind  # value = <ArrayBufferKind.STRIDED_DEVICE: 1>
STRIDED_HOST: ArrayBufferKind  # value = <ArrayBufferKind.STRIDED_HOST: 2>
__cuda_version__: int = 12080
__version__: str = '4.2.0'
