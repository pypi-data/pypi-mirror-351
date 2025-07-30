"""


        nvCOMP Python API reference

        This is the Python API reference for the NVIDIA® nvCOMP library.
    
"""
from __future__ import annotations
from nvidia.nvcomp.nvcomp_impl import Array
from nvidia.nvcomp.nvcomp_impl import ArrayBufferKind
from nvidia.nvcomp.nvcomp_impl import BitstreamKind
from nvidia.nvcomp.nvcomp_impl import ChecksumPolicy
from nvidia.nvcomp.nvcomp_impl import Codec
from nvidia.nvcomp.nvcomp_impl import CudaStream
from nvidia.nvcomp.nvcomp_impl import as_array
from nvidia.nvcomp.nvcomp_impl import as_arrays
from nvidia.nvcomp.nvcomp_impl import from_dlpack
from nvidia.nvcomp.nvcomp_impl import set_device_allocator
from nvidia.nvcomp.nvcomp_impl import set_host_allocator
from nvidia.nvcomp.nvcomp_impl import set_pinned_allocator
from . import nvcomp_impl
__all__ = ['Array', 'ArrayBufferKind', 'BitstreamKind', 'COMPUTE_AND_NO_VERIFY', 'COMPUTE_AND_VERIFY', 'COMPUTE_AND_VERIFY_IF_PRESENT', 'ChecksumPolicy', 'Codec', 'CudaStream', 'NO_COMPUTE_AND_VERIFY_IF_PRESENT', 'NO_COMPUTE_NO_VERIFY', 'STRIDED_DEVICE', 'STRIDED_HOST', 'as_array', 'as_arrays', 'from_dlpack', 'nvcomp_impl', 'set_device_allocator', 'set_host_allocator', 'set_pinned_allocator']
COMPUTE_AND_NO_VERIFY: nvcomp_impl.ChecksumPolicy  # value = <ChecksumPolicy.COMPUTE_AND_NO_VERIFY: 1>
COMPUTE_AND_VERIFY: nvcomp_impl.ChecksumPolicy  # value = <ChecksumPolicy.COMPUTE_AND_VERIFY: 4>
COMPUTE_AND_VERIFY_IF_PRESENT: nvcomp_impl.ChecksumPolicy  # value = <ChecksumPolicy.COMPUTE_AND_VERIFY_IF_PRESENT: 3>
NO_COMPUTE_AND_VERIFY_IF_PRESENT: nvcomp_impl.ChecksumPolicy  # value = <ChecksumPolicy.NO_COMPUTE_AND_VERIFY_IF_PRESENT: 2>
NO_COMPUTE_NO_VERIFY: nvcomp_impl.ChecksumPolicy  # value = <ChecksumPolicy.NO_COMPUTE_NO_VERIFY: 0>
STRIDED_DEVICE: nvcomp_impl.ArrayBufferKind  # value = <ArrayBufferKind.STRIDED_DEVICE: 1>
STRIDED_HOST: nvcomp_impl.ArrayBufferKind  # value = <ArrayBufferKind.STRIDED_HOST: 2>
__cuda_version__: int = 11080
__git_sha__: str = ''
__version__: str = '4.2.0'
