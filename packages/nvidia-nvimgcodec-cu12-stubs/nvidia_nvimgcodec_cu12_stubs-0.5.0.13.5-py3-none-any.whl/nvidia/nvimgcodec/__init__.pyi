"""


        nvImageCodec Python API reference

        This is the Python API reference for the NVIDIA® nvImageCodec library.
    
"""
from __future__ import annotations
from nvidia.nvimgcodec.nvimgcodec_impl import Backend
from nvidia.nvimgcodec.nvimgcodec_impl import BackendKind
from nvidia.nvimgcodec.nvimgcodec_impl import BackendParams
from nvidia.nvimgcodec.nvimgcodec_impl import ChromaSubsampling
from nvidia.nvimgcodec.nvimgcodec_impl import CodeStream
from nvidia.nvimgcodec.nvimgcodec_impl import ColorSpec
from nvidia.nvimgcodec.nvimgcodec_impl import DecodeParams
from nvidia.nvimgcodec.nvimgcodec_impl import DecodeSource
from nvidia.nvimgcodec.nvimgcodec_impl import Decoder
from nvidia.nvimgcodec.nvimgcodec_impl import EncodeParams
from nvidia.nvimgcodec.nvimgcodec_impl import Encoder
from nvidia.nvimgcodec.nvimgcodec_impl import Image
from nvidia.nvimgcodec.nvimgcodec_impl import ImageBufferKind
from nvidia.nvimgcodec.nvimgcodec_impl import Jpeg2kBitstreamType
from nvidia.nvimgcodec.nvimgcodec_impl import Jpeg2kEncodeParams
from nvidia.nvimgcodec.nvimgcodec_impl import Jpeg2kProgOrder
from nvidia.nvimgcodec.nvimgcodec_impl import JpegEncodeParams
from nvidia.nvimgcodec.nvimgcodec_impl import LoadHintPolicy
from nvidia.nvimgcodec.nvimgcodec_impl import Region
from nvidia.nvimgcodec.nvimgcodec_impl import as_image
from nvidia.nvimgcodec.nvimgcodec_impl import as_images
from nvidia.nvimgcodec.nvimgcodec_impl import from_dlpack
from . import nvimgcodec_impl
__all__ = ['ADAPTIVE_MINIMIZE_IDLE_TIME', 'Backend', 'BackendKind', 'BackendParams', 'CPRL', 'CPU_ONLY', 'CSS_410', 'CSS_410V', 'CSS_411', 'CSS_420', 'CSS_422', 'CSS_440', 'CSS_444', 'CSS_GRAY', 'ChromaSubsampling', 'CodeStream', 'ColorSpec', 'DecodeParams', 'DecodeSource', 'Decoder', 'EncodeParams', 'Encoder', 'FIXED', 'GPU_ONLY', 'GRAY', 'HW_GPU_ONLY', 'HYBRID_CPU_GPU', 'IGNORE', 'Image', 'ImageBufferKind', 'J2K', 'JP2', 'Jpeg2kBitstreamType', 'Jpeg2kEncodeParams', 'Jpeg2kProgOrder', 'JpegEncodeParams', 'LRCP', 'LoadHintPolicy', 'PCRL', 'RGB', 'RLCP', 'RPCL', 'Region', 'STRIDED_DEVICE', 'STRIDED_HOST', 'UNCHANGED', 'YCC', 'as_image', 'as_images', 'from_dlpack', 'nvimgcodec_impl']
ADAPTIVE_MINIMIZE_IDLE_TIME: nvimgcodec_impl.LoadHintPolicy  # value = <LoadHintPolicy.ADAPTIVE_MINIMIZE_IDLE_TIME: 3>
CPRL: nvimgcodec_impl.Jpeg2kProgOrder  # value = <Jpeg2kProgOrder.CPRL: 4>
CPU_ONLY: nvimgcodec_impl.BackendKind  # value = <BackendKind.CPU_ONLY: 1>
CSS_410: nvimgcodec_impl.ChromaSubsampling  # value = <ChromaSubsampling.CSS_410: 6>
CSS_410V: nvimgcodec_impl.ChromaSubsampling  # value = <ChromaSubsampling.CSS_410V: 8>
CSS_411: nvimgcodec_impl.ChromaSubsampling  # value = <ChromaSubsampling.CSS_411: 5>
CSS_420: nvimgcodec_impl.ChromaSubsampling  # value = <ChromaSubsampling.CSS_420: 3>
CSS_422: nvimgcodec_impl.ChromaSubsampling  # value = <ChromaSubsampling.CSS_422: 2>
CSS_440: nvimgcodec_impl.ChromaSubsampling  # value = <ChromaSubsampling.CSS_440: 4>
CSS_444: nvimgcodec_impl.ChromaSubsampling  # value = <ChromaSubsampling.CSS_444: 0>
CSS_GRAY: nvimgcodec_impl.ChromaSubsampling  # value = <ChromaSubsampling.CSS_GRAY: 7>
FIXED: nvimgcodec_impl.LoadHintPolicy  # value = <LoadHintPolicy.FIXED: 2>
GPU_ONLY: nvimgcodec_impl.BackendKind  # value = <BackendKind.GPU_ONLY: 2>
GRAY: nvimgcodec_impl.ColorSpec  # value = <ColorSpec.GRAY: 2>
HW_GPU_ONLY: nvimgcodec_impl.BackendKind  # value = <BackendKind.HW_GPU_ONLY: 4>
HYBRID_CPU_GPU: nvimgcodec_impl.BackendKind  # value = <BackendKind.HYBRID_CPU_GPU: 3>
IGNORE: nvimgcodec_impl.LoadHintPolicy  # value = <LoadHintPolicy.IGNORE: 1>
J2K: nvimgcodec_impl.Jpeg2kBitstreamType  # value = <Jpeg2kBitstreamType.J2K: 0>
JP2: nvimgcodec_impl.Jpeg2kBitstreamType  # value = <Jpeg2kBitstreamType.JP2: 1>
LRCP: nvimgcodec_impl.Jpeg2kProgOrder  # value = <Jpeg2kProgOrder.LRCP: 0>
PCRL: nvimgcodec_impl.Jpeg2kProgOrder  # value = <Jpeg2kProgOrder.PCRL: 3>
RGB: nvimgcodec_impl.ColorSpec  # value = <ColorSpec.RGB: 1>
RLCP: nvimgcodec_impl.Jpeg2kProgOrder  # value = <Jpeg2kProgOrder.RLCP: 1>
RPCL: nvimgcodec_impl.Jpeg2kProgOrder  # value = <Jpeg2kProgOrder.RPCL: 2>
STRIDED_DEVICE: nvimgcodec_impl.ImageBufferKind  # value = <ImageBufferKind.STRIDED_DEVICE: 1>
STRIDED_HOST: nvimgcodec_impl.ImageBufferKind  # value = <ImageBufferKind.STRIDED_HOST: 2>
UNCHANGED: nvimgcodec_impl.ColorSpec  # value = <ColorSpec.UNCHANGED: 0>
YCC: nvimgcodec_impl.ColorSpec  # value = <ColorSpec.YCC: 3>
__cuda_version__: int = 12080
__git_sha__: str = ''
__version__: str = '0.5.0'
