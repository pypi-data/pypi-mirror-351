"""


        nvImageCodec Python API reference

        This is the Python API reference for the NVIDIA® nvImageCodec library.
    
"""
from __future__ import annotations
import os
import typing
__all__ = ['ADAPTIVE_MINIMIZE_IDLE_TIME', 'Backend', 'BackendKind', 'BackendParams', 'CPRL', 'CPU_ONLY', 'CSS_410', 'CSS_410V', 'CSS_411', 'CSS_420', 'CSS_422', 'CSS_440', 'CSS_444', 'CSS_GRAY', 'ChromaSubsampling', 'CodeStream', 'ColorSpec', 'DecodeParams', 'DecodeSource', 'Decoder', 'EncodeParams', 'Encoder', 'FIXED', 'GPU_ONLY', 'GRAY', 'HW_GPU_ONLY', 'HYBRID_CPU_GPU', 'IGNORE', 'Image', 'ImageBufferKind', 'J2K', 'JP2', 'Jpeg2kBitstreamType', 'Jpeg2kEncodeParams', 'Jpeg2kProgOrder', 'JpegEncodeParams', 'LRCP', 'LoadHintPolicy', 'PCRL', 'RGB', 'RLCP', 'RPCL', 'Region', 'STRIDED_DEVICE', 'STRIDED_HOST', 'UNCHANGED', 'YCC', 'as_image', 'as_images', 'from_dlpack']
class Backend:
    """
    Class representing the backend configuration for image processing tasks.
    """
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor initializes the backend with GPU_ONLY backend kind and default parameters.
        """
    @typing.overload
    def __init__(self, backend_kind: BackendKind, load_hint: float = 1.0, load_hint_policy: LoadHintPolicy = ...) -> None:
        """
                    Constructor with parameters.
                    
                    Args:
                        backend_kind: Specifies the type of backend (e.g., GPU_ONLY, CPU_ONLY).
        
                        load_hint: Fraction of the batch samples that will be processed by this backend (default is 1.0).
                        This is just a hint for performance balancing, so particular extension can ignore it and work on all images it recognizes.
                        
                        load_hint_policy: Policy for using the load hint, affecting how processing is distributed.
        """
    @typing.overload
    def __init__(self, backend_kind: BackendKind, backend_params: BackendParams) -> None:
        """
                    Constructor with backend parameters.
                    
                    Args:
                        backend_kind: Type of backend (e.g., GPU_ONLY, CPU_ONLY).
                        
                        backend_params: Additional parameters that define how the backend should operate.
        """
    @property
    def backend_kind(self) -> BackendKind:
        """
                    The backend kind determines whether processing is done on GPU, CPU, or a hybrid of both.
        """
    @backend_kind.setter
    def backend_kind(self, arg1: BackendKind) -> None:
        ...
    @property
    def backend_params(self) -> BackendParams:
        """
                    Backend parameters include detailed configurations that control backend behavior and performance.
        """
    @backend_params.setter
    def backend_params(self, arg1: BackendParams) -> None:
        ...
    @property
    def load_hint(self) -> float:
        """
                    Load hint is a fraction representing the portion of the workload assigned to this backend. 
                    Adjusting this may optimize resource use across available backends.
        """
    @load_hint.setter
    def load_hint(self, arg1: float) -> None:
        ...
    @property
    def load_hint_policy(self) -> LoadHintPolicy:
        """
                    The load hint policy defines how the load hint is interpreted, affecting dynamic load distribution.
        """
    @load_hint_policy.setter
    def load_hint_policy(self, arg1: LoadHintPolicy) -> None:
        ...
class BackendKind:
    """
    
                Enum representing backend kinds used in nvImageCodec for decoding/encoding operations.
    
                This enum helps specify where (CPU, GPU, both, or GPU hardware engine) the image processing tasks are executed.
            
    
    Members:
    
      CPU_ONLY : 
                    Backend kind specifying that decoding/encoding is executed only on CPU.
                
    
      GPU_ONLY : 
                    Backend kind specifying that decoding/encoding is executed only on GPU.
                
    
      HYBRID_CPU_GPU : 
                    Backend kind specifying that decoding/encoding is executed on both CPU and GPU.
                
    
      HW_GPU_ONLY : 
                    Backend kind specifying that decoding/encoding is executed on GPU dedicated hardware engine.
                
    """
    CPU_ONLY: typing.ClassVar[BackendKind]  # value = <BackendKind.CPU_ONLY: 1>
    GPU_ONLY: typing.ClassVar[BackendKind]  # value = <BackendKind.GPU_ONLY: 2>
    HW_GPU_ONLY: typing.ClassVar[BackendKind]  # value = <BackendKind.HW_GPU_ONLY: 4>
    HYBRID_CPU_GPU: typing.ClassVar[BackendKind]  # value = <BackendKind.HYBRID_CPU_GPU: 3>
    __members__: typing.ClassVar[dict[str, BackendKind]]  # value = {'CPU_ONLY': <BackendKind.CPU_ONLY: 1>, 'GPU_ONLY': <BackendKind.GPU_ONLY: 2>, 'HYBRID_CPU_GPU': <BackendKind.HYBRID_CPU_GPU: 3>, 'HW_GPU_ONLY': <BackendKind.HW_GPU_ONLY: 4>}
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
class BackendParams:
    """
    Class for configuring backend parameters like load hint and load hint policy.
    """
    @typing.overload
    def __init__(self) -> None:
        """
                    Creates a BackendParams object with default settings.
        
                    By default, the load hint is set to 1.0 and the load hint policy is set to a fixed value.
        """
    @typing.overload
    def __init__(self, load_hint: float = 1.0, load_hint_policy: LoadHintPolicy = ...) -> None:
        """
                    Creates a BackendParams object with specified load parameters.
        
                    Args:
                        load_hint: A float representing the fraction of the batch samples that will be picked by this backend.
                        The remaining samples will be picked by the next lower priority backend.
                        This is just a hint for performance balancing, so particular extension can ignore it and work on all images it recognizes.
        
                        load_hint_policy: Defines how the load hint is used. Different policies can dictate whether to ignore,
                        fix, or adaptively change the load hint.
        """
    @property
    def load_hint(self) -> float:
        """
                    Fraction of the batch samples that will be picked by this backend.
        
                    The remaining samples will be picked by the next lower priority backend.
                    This is just a hint for performance balancing, so particular extension can ignore it and work on all images it recognizes.
        """
    @load_hint.setter
    def load_hint(self, arg1: float) -> None:
        ...
    @property
    def load_hint_policy(self) -> bool:
        """
                    Defines how to use the load hint.
        
                    This property controls the interpretation of load hints, with options to ignore,
                    use as fixed or adaptively alter the hint according to workload.
        """
    @load_hint_policy.setter
    def load_hint_policy(self, arg1: LoadHintPolicy) -> None:
        ...
class ChromaSubsampling:
    """
    
                Enum representing different types of chroma subsampling.
    
                Chroma subsampling is the practice of encoding images by implementing less resolution for chroma information than for luma information. 
                This is based on the fact that the human eye is more sensitive to changes in brightness than color.
            
    
    Members:
    
      CSS_444 : 
                No chroma subsampling. Each pixel has a corresponding chroma value (full color resolution).
                
    
      CSS_422 : 
                Chroma is subsampled by a factor of 2 in the horizontal direction. Each line has its chroma sampled at half the horizontal resolution of luma.
                
    
      CSS_420 : 
                Chroma is subsampled by a factor of 2 both horizontally and vertically. Each block of 2x2 pixels shares a single chroma sample.
                
    
      CSS_440 : 
                Chroma is subsampled by a factor of 2 in the vertical direction. Each column has its chroma sampled at half the vertical resolution of luma.
                
    
      CSS_411 : 
                Chroma is subsampled by a factor of 4 in the horizontal direction. Each line has its chroma sampled at quarter the horizontal resolution of luma.
                
    
      CSS_410 : 
                Chroma is subsampled by a factor of 4 horizontally and a factor of 2 vertically. Each line has its chroma sampled at quarter the horizontal and half of the vertical resolution of luma.
                
    
      CSS_GRAY : 
                Grayscale image. No chroma information is present.
                
    
      CSS_410V : 
                Chroma is subsampled by a factor of 4 horizontally and a factor of 2 vertically. Each line has its chroma sampled at quarter the horizontal and half of the vertical resolution of luma.
                Comparing to 4:1:0,  this variation modifies how vertical sampling is handled. While it also has one chroma sample for every four luma samples horizontally,
                it introduces a vertical alternation in how chroma samples are placed between rows. 
                
    """
    CSS_410: typing.ClassVar[ChromaSubsampling]  # value = <ChromaSubsampling.CSS_410: 6>
    CSS_410V: typing.ClassVar[ChromaSubsampling]  # value = <ChromaSubsampling.CSS_410V: 8>
    CSS_411: typing.ClassVar[ChromaSubsampling]  # value = <ChromaSubsampling.CSS_411: 5>
    CSS_420: typing.ClassVar[ChromaSubsampling]  # value = <ChromaSubsampling.CSS_420: 3>
    CSS_422: typing.ClassVar[ChromaSubsampling]  # value = <ChromaSubsampling.CSS_422: 2>
    CSS_440: typing.ClassVar[ChromaSubsampling]  # value = <ChromaSubsampling.CSS_440: 4>
    CSS_444: typing.ClassVar[ChromaSubsampling]  # value = <ChromaSubsampling.CSS_444: 0>
    CSS_GRAY: typing.ClassVar[ChromaSubsampling]  # value = <ChromaSubsampling.CSS_GRAY: 7>
    __members__: typing.ClassVar[dict[str, ChromaSubsampling]]  # value = {'CSS_444': <ChromaSubsampling.CSS_444: 0>, 'CSS_422': <ChromaSubsampling.CSS_422: 2>, 'CSS_420': <ChromaSubsampling.CSS_420: 3>, 'CSS_440': <ChromaSubsampling.CSS_440: 4>, 'CSS_411': <ChromaSubsampling.CSS_411: 5>, 'CSS_410': <ChromaSubsampling.CSS_410: 6>, 'CSS_GRAY': <ChromaSubsampling.CSS_GRAY: 7>, 'CSS_410V': <ChromaSubsampling.CSS_410V: 8>}
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
class CodeStream:
    """
    
            Class representing a coded stream of image data.
    
            This class provides access to image informations such as dimensions, codec,
            and tiling details. It supports initialization from bytes, numpy arrays, or file path.
            
    """
    @typing.overload
    def __init__(self, bytes: bytes) -> None:
        """
                    Initialize a CodeStream using bytes as input.
        
                    Args:
                        bytes: The byte data representing the encoded stream.
        """
    @typing.overload
    def __init__(self, array: numpy.ndarray[numpy.uint8]) -> None:
        """
                    Initialize a CodeStream using a numpy array of uint8 as input.
        
                    Args:
                        array: The numpy array containing the encoded stream.
        """
    @typing.overload
    def __init__(self, filename: os.PathLike) -> None:
        """
                    Initialize a CodeStream using a file path as input.
        
                    Args:
                        filename: The file path to the encoded stream data.
        """
    def __repr__(self) -> str:
        """
                Returns a string representation of the CodeStream object, displaying core attributes.
        """
    @property
    def channels(self) -> int:
        """
                    The number of channels in the image.
        """
    @property
    def codec_name(self) -> str:
        """
                    Image format.
        """
    @property
    def dtype(self) -> numpy.dtype[typing.Any]:
        """
                    Data type of samples.
        """
    @property
    def height(self) -> int:
        """
                    The vertical dimension of the entire image in pixels.
        """
    @property
    def num_tiles_x(self) -> int | None:
        """
                    The number of tiles arranged along the horizontal axis of the image.
        """
    @property
    def num_tiles_y(self) -> int | None:
        """
                    The number of tiles arranged along the vertical axis of the image.
        """
    @property
    def precision(self) -> int:
        """
                    Maximum number of significant bits in data type. Value 0 
                    means that precision is equal to data type bit depth.
        """
    @property
    def tile_height(self) -> int | None:
        """
                    The vertical dimension of each individual tile within the image.
        """
    @property
    def tile_width(self) -> int | None:
        """
                    The horizontal dimension of each individual tile within the image.
        """
    @property
    def width(self) -> int:
        """
                    The horizontal dimension of the entire image in pixels.
        """
class ColorSpec:
    """
    Enum representing color specification for image.
    
    Members:
    
      UNCHANGED : Use the color specification unchanged from the source.
    
      YCC : Use the YCBCr color space.
    
      RGB : Use the standard RGB color space.
    
      GRAY : Use the grayscale color space.
    """
    GRAY: typing.ClassVar[ColorSpec]  # value = <ColorSpec.GRAY: 2>
    RGB: typing.ClassVar[ColorSpec]  # value = <ColorSpec.RGB: 1>
    UNCHANGED: typing.ClassVar[ColorSpec]  # value = <ColorSpec.UNCHANGED: 0>
    YCC: typing.ClassVar[ColorSpec]  # value = <ColorSpec.YCC: 3>
    __members__: typing.ClassVar[dict[str, ColorSpec]]  # value = {'UNCHANGED': <ColorSpec.UNCHANGED: 0>, 'YCC': <ColorSpec.YCC: 3>, 'RGB': <ColorSpec.RGB: 1>, 'GRAY': <ColorSpec.GRAY: 2>}
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
class DecodeParams:
    """
    Class to define parameters for image decoding operations.
    """
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor that initializes the DecodeParams object with default settings.
        """
    @typing.overload
    def __init__(self, apply_exif_orientation: bool = True, color_spec: ColorSpec = ..., allow_any_depth: bool = False) -> None:
        """
                    Constructor with parameters to control the decoding process.
        
                    Args:
                        apply_exif_orientation: Boolean flag to apply EXIF orientation if available. Defaults to True.
        
                        color_spec: Desired color specification for decoding. Defaults to sRGB.
                        
                        allow_any_depth: Boolean flag to allow any native bit depth. If not enabled, the 
                        dynamic range is scaled to uint8. Defaults to False.
        """
    @property
    def allow_any_depth(self) -> bool:
        """
                    Boolean property to permit any native bit depth during decoding.
        
                    When set to True, it allows decoding of images with their native bit depth. 
                    If False, the pixel values are scaled to the 8-bit range (0-255). Defaults to False.
        """
    @allow_any_depth.setter
    def allow_any_depth(self, arg1: bool) -> None:
        ...
    @property
    def apply_exif_orientation(self) -> bool:
        """
                    Boolean property to enable or disable applying EXIF orientation during decoding.
        
                    When set to True, the image is rotated and/or flipped according to its EXIF orientation 
                    metadata if present. Defaults to True.
        """
    @apply_exif_orientation.setter
    def apply_exif_orientation(self, arg1: bool) -> None:
        ...
    @property
    def color_spec(self) -> ColorSpec:
        """
                    Property to get or set the color specification for the decoding process.
        
                    This determines the color space or color profile to use during decoding. 
                    For instance, sRGB is a common color specification. Defaults to sRGB.
        """
    @color_spec.setter
    def color_spec(self, arg1: ColorSpec) -> None:
        ...
class DecodeSource:
    """
    Class representing a source for decoding, which includes the image code stream to decode and an optional region within the image.
    """
    @typing.overload
    def __init__(self, code_stream: CodeStream, region: Region | None = None) -> None:
        """
        Constructor initializing DecodeSource with a code stream and an optional region to specify a subsection of the image to decode.
        """
    @typing.overload
    def __init__(self, array: numpy.ndarray[numpy.uint8], region: Region | None = None) -> None:
        """
        Constructor initializing DecodeSource with a numpy array and an optional region to decode specific parts of the image.
        """
    @typing.overload
    def __init__(self, bytes: bytes, region: Region | None = None) -> None:
        """
        Constructor initializing DecodeSource with byte data and an optional region to decode specific parts of the image.
        """
    @typing.overload
    def __init__(self, filename: os.PathLike, region: Region | None = None) -> None:
        """
        Constructor initializing DecodeSource with filename pointing to the file with image and an optionally region to decode specific parts of the image.
        """
    def __repr__(self) -> str:
        """
        Returns a string representation of the DecodeSource object.
        """
    @property
    def code_stream(self) -> CodeStream:
        """
        Returns the code stream to be decoded into an image.
        """
    @property
    def region(self) -> Region | None:
        """
        Returns the region of the image that will be decoded, if specified; otherwise, returns None.
        """
class Decoder:
    """
    Decoder for image decoding operations. It provides methods to decode images from various sources such as files or data streams. The decoding process can be configured with parameters like the applied backend or execution settings.
    """
    def __enter__(self) -> typing.Any:
        """
        Enter the runtime context related to this decoder.
        """
    def __exit__(self, exc_type: type | None = None, exc_value: typing.Any | None = None, traceback: typing.Any | None = None) -> None:
        """
        Exit the runtime context related to this decoder and releases allocated resources.
        """
    @typing.overload
    def __init__(self, device_id: int = -1, max_num_cpu_threads: int = 0, backends: list[Backend] | None = None, options: str = ':fancy_upsampling=0') -> None:
        """
                    Initialize decoder.
        
                    Args:
                        device_id: Device id to execute decoding on.
        
                        max_num_cpu_threads: Max number of CPU threads in default executor (0 means default value equal to number of cpu cores).
        
                        backends: List of allowed backends. If empty, all backends are allowed with default parameters.
                        
                        options: Decoder specific options e.g.: "nvjpeg:fancy_upsampling=1"
        """
    @typing.overload
    def __init__(self, device_id: int = -1, max_num_cpu_threads: int = 0, backend_kinds: list[BackendKind] | None = None, options: str = ':fancy_upsampling=0') -> None:
        """
                    Initialize decoder.
        
                    Args:
                        device_id: Device id to execute decoding on.
        
                        max_num_cpu_threads: Max number of CPU threads in default executor (0 means default value equal to number of cpu cores).
        
                        backend_kinds: List of allowed backend kinds. If empty or None, all backends are allowed with default parameters.
        
                        options: Decoder specific options e.g.: "nvjpeg:fancy_upsampling=1"
        """
    @typing.overload
    def decode(self, src: DecodeSource, params: DecodeParams | None = None, cuda_stream: int = 0) -> typing.Any:
        """
                    Executes decoding of data from a DecodeSource handle (code stream handle and an optional region of interest).
        
                    Args:
                        src: decode source object.
        
                        params: Decode parameters.
        
                        cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place.
        
                    Returns:
                        nvimgcodec.Image or None if the image cannot be decoded because of any reason.
        """
    @typing.overload
    def decode(self, srcs: list[DecodeSource], params: DecodeParams | None = None, cuda_stream: int = 0) -> list[typing.Any]:
        """
                    Executes decoding from a batch of DecodeSource handles (code stream handle and an optional region of interest).
        
                    Args:
                        srcs: List of DecodeSource objects
        
                        params: Decode parameters.
        
                        cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place.
        
                    Returns:
                        List of decoded nvimgcodec.Image's. There is None in returned list on positions which could not be decoded.
        """
    @typing.overload
    def read(self, path: DecodeSource, params: DecodeParams | None = None, cuda_stream: int = 0) -> typing.Any:
        """
                    Executes decoding from a filename.
        
                    Args:
                        path: File path to decode.
        
                        params: Decode parameters.
        
                        cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place.
        
                    Returns:
                        nvimgcodec.Image or None if the image cannot be decoded because of any reason.
        """
    @typing.overload
    def read(self, paths: list[DecodeSource], params: DecodeParams | None = None, cuda_stream: int = 0) -> list[typing.Any]:
        """
                    Executes decoding from a batch of file paths.
        
                    Args:
                        path: List of file paths to decode.
        
                        params: Decode parameters.
        
                        cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place.
        
                    Returns:
                        List of decoded nvimgcodec.Image's. There is None in returned list on positions which could not be decoded.
        """
class EncodeParams:
    """
    Class to define parameters for image encoding operations.
    """
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor that initializes the EncodeParams object with default settings.
        """
    @typing.overload
    def __init__(self, quality: float = 95, target_psnr: float = 50, color_spec: ColorSpec = ..., chroma_subsampling: ChromaSubsampling = ..., jpeg_encode_params: JpegEncodeParams | None = None, jpeg2k_encode_params: Jpeg2kEncodeParams | None = None) -> None:
        """
                    Constructor with parameters to control the encoding process.
        
                    Args:
                        quality (float): Compression quality, 0-100. Defaults to 95. For WebP, values >100 indicate lossless compression.
        
                        target_psnr (float): Target Peak Signal-to-Noise Ratio for encoding, applicable to some codecs (At present, JPEG2000 only). Defaults to 50.
        
                        color_spec (ColorSpec): Output color specification. Defaults to UNCHANGED.
        
                        chroma_subsampling (ChromaSubsampling): Chroma subsampling format. Defaults to CSS_444.
        
                        jpeg_encode_params (JpegEncodeParams): Optional JPEG specific encoding parameters.
                        
                        jpeg2k_encode_params (Jpeg2kEncodeParams): Optional JPEG2000 specific encoding parameters.
        """
    @property
    def chroma_subsampling(self) -> ChromaSubsampling:
        """
                    Specifies the chroma subsampling format for encoding. Defaults to CSS_444 so not chroma subsampling.
        """
    @chroma_subsampling.setter
    def chroma_subsampling(self, arg1: ChromaSubsampling) -> None:
        ...
    @property
    def color_spec(self) -> ColorSpec:
        """
                    Defines the expected color specification for the output. Defaults to ColorSpec.UNCHANGED.
        """
    @color_spec.setter
    def color_spec(self, arg1: ColorSpec) -> None:
        ...
    @property
    def jpeg2k_params(self) -> Jpeg2kEncodeParams:
        """
                    Optional, additional JPEG2000-specific encoding parameters.
        """
    @jpeg2k_params.setter
    def jpeg2k_params(self, arg1: Jpeg2kEncodeParams) -> None:
        ...
    @property
    def jpeg_params(self) -> JpegEncodeParams:
        """
                    Optional, additional JPEG-specific encoding parameters.
        """
    @jpeg_params.setter
    def jpeg_params(self, arg1: JpegEncodeParams) -> None:
        ...
    @property
    def quality(self) -> float:
        """
                    Quality value for encoding, ranging from 0 to 100. Defaults to 95.
        
                    For WebP, a value greater than 100 signifies lossless compression.
        """
    @quality.setter
    def quality(self, arg1: float) -> None:
        ...
    @property
    def target_psnr(self) -> float:
        """
                    Desired Peak Signal-to-Noise Ratio (PSNR) target for the encoded image. Defaults to 50.
        """
    @target_psnr.setter
    def target_psnr(self, arg1: float) -> None:
        ...
class Encoder:
    """
    Encoder for image encoding operations. It allows converting images to various compressed formats or save them to files. The encoding process can be customized with different parameters and options.
    """
    def __enter__(self) -> typing.Any:
        """
        Enter the runtime context related to this encoder.
        """
    def __exit__(self, exc_type: type | None = None, exc_value: typing.Any | None = None, traceback: typing.Any | None = None) -> None:
        """
        Exit the runtime context related to this encoder and releases allocated resources.
        """
    @typing.overload
    def __init__(self, device_id: int = -1, max_num_cpu_threads: int = 0, backends: list[Backend] | None = None, options: str = '') -> None:
        """
                    Initialize encoder.
        
                    Args:
                        device_id: Device id to execute encoding on.
        
                        max_num_cpu_threads: Max number of CPU threads in default executor (0 means default value equal to number of cpu cores)
                        
                        backends: List of allowed backends. If empty, all backends are allowed with default parameters.
                        
                        options: Encoder specific options.
        """
    @typing.overload
    def __init__(self, device_id: int = -1, max_num_cpu_threads: int = 0, backend_kinds: list[BackendKind] | None = None, options: str = ':fancy_upsampling=0') -> None:
        """
                    Initialize encoder.
        
                    Args:
                        device_id: Device id to execute encoding on.
        
                        max_num_cpu_threads: Max number of CPU threads in default executor (0 means default value equal to number of cpu cores)
                        
                        backend_kinds: List of allowed backend kinds. If empty or None, all backends are allowed with default parameters.
                        
                        options: Encoder specific options.
        """
    def encode(self, image_s: typing.Any, codec: str, params: EncodeParams | None = None, cuda_stream: int = 0) -> typing.Any:
        """
                    Encode image(s) to buffer(s).
        
                    Args:
                        image_s: Image or list of images to encode
                        
                        codec: String that defines the output format e.g.'jpeg2k'. When it is file extension it must include a leading period e.g. '.jp2'.
                        
                        params: Encode parameters.
                        
                        cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place.
        
                    Returns:
                        Buffer or list of buffers with compressed code stream(s). None if the image(s) cannot be encoded because of any reason.
        """
    @typing.overload
    def write(self, file_name: str, image: typing.Any, codec: str = '', params: EncodeParams | None = None, cuda_stream: int = 0) -> typing.Any:
        """
                    Encode image to file.
        
                    Args:
                        file_name: File name to save encoded code stream.
        
                        image: Image to encode
        
                        codec: String that defines the output format e.g.'jpeg2k'. When it is file extension it must include a 
                        leading period e.g. '.jp2'. If codec is not specified, it is deducted based on file extension. 
                        If there is no extension by default 'jpeg' is choosen. 
        
                        params: Encode parameters.
        
                        cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place.
        
                    Returns: 
                        Encoded file name, or None if the input image could not be encoded for any reason. 
        """
    @typing.overload
    def write(self, file_names: list[str], images: list[typing.Any], codec: str = '', params: EncodeParams | None = None, cuda_stream: int = 0) -> list[typing.Any]:
        """
                    Encode batch of images to files.
        
                    Args:
                        file_names: List of file names to save encoded code streams.
        
                        images: List of images to encode.
        
                        codec: String that defines the output format e.g.'jpeg2k'. When it is file extension it must include a 
                        leading period e.g. '.jp2'. If codec is not specified, it is deducted based on file extension. 
                        If there is no extension by default 'jpeg' is choosen. (optional)
                        
                        params: Encode parameters.
                        
                        cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place.
        
                    Returns:
                        List of encoded file names. If an image could not be encoded for any reason, the corresponding position in the list will contain None.
        """
class Image:
    """
    Class which wraps buffer with pixels. It can be decoded pixels or pixels to encode.
    
                At present, the image must always have a three-dimensional shape in the HWC layout (height, width, channels), 
                which is also known as the interleaved format, and be stored as a contiguous array in C-style.
                
    """
    def __dlpack__(self, stream: typing.Any = None) -> capsule:
        """
        Export the image as a DLPack tensor
        """
    def __dlpack_device__(self) -> tuple:
        """
        Get the device associated with the buffer
        """
    def cpu(self) -> typing.Any:
        """
                    Returns a copy of this image in CPU memory. If this image is already in CPU memory, 
                    than no copy is performed and the original object is returned. 
                    
                    Returns:
                        Image object with content in CPU memory or None if copy could not be done.
        """
    def cuda(self, synchronize: bool = True) -> typing.Any:
        """
                    Returns a copy of this image in device memory. If this image is already in device memory, 
                    than no copy is performed and the original object is returned.  
                    
                    Args:
                        synchronize: If True (by default) it blocks and waits for copy from host to device to be finished, 
                                     else no synchronization is executed and further synchronization needs to be done using
                                     cuda stream provided by e.g. \\_\\_cuda_array_interface\\_\\_. 
        
                    Returns:
                        Image object with content in device memory or None if copy could not be done.
        """
    def to_dlpack(self, cuda_stream: typing.Any = None) -> capsule:
        """
                    Export the image with zero-copy conversion to a DLPack tensor. 
                    
                    Args:
                        cuda_stream: An optional cudaStream_t represented as a Python integer, 
                        upon which synchronization must take place in created Image.
        
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
    def buffer_kind(self) -> ImageBufferKind:
        """
                    Buffer kind in which image data is stored. This indicates whether the data is stored as strided device or host memory.
        """
    @property
    def dtype(self) -> typing.Any:
        """
                    The data type (dtype) of the image samples.
        """
    @property
    def height(self) -> int:
        """
                    The height of the image in pixels.
        """
    @property
    def ndim(self) -> int:
        """
                    The number of dimensions in the image.
        """
    @property
    def precision(self) -> int:
        """
                    Maximum number of significant bits in data type. Value 0 means that precision is equal to data type bit depth.
        """
    @property
    def shape(self) -> tuple:
        """
                    The shape of the image.
        """
    @property
    def strides(self) -> tuple:
        """
                    Strides of axes in bytes.
        """
    @property
    def width(self) -> int:
        """
                    The width of the image in pixels.
        """
class ImageBufferKind:
    """
    Enum representing buffer kind in which image data is stored.
    
    Members:
    
      STRIDED_DEVICE : 
                GPU-accessible with planes in pitch-linear layout.
                
    
      STRIDED_HOST : 
                Host-accessible with planes in pitch-linear layout.
                
    """
    STRIDED_DEVICE: typing.ClassVar[ImageBufferKind]  # value = <ImageBufferKind.STRIDED_DEVICE: 1>
    STRIDED_HOST: typing.ClassVar[ImageBufferKind]  # value = <ImageBufferKind.STRIDED_HOST: 2>
    __members__: typing.ClassVar[dict[str, ImageBufferKind]]  # value = {'STRIDED_DEVICE': <ImageBufferKind.STRIDED_DEVICE: 1>, 'STRIDED_HOST': <ImageBufferKind.STRIDED_HOST: 2>}
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
class Jpeg2kBitstreamType:
    """
    
                Enum to define JPEG2000 bitstream types.
    
                This enum identifies the bitstream type for JPEG2000, which may be either a raw J2K codestream
                or a JP2 container format that can include additional metadata.
            
    
    Members:
    
      J2K : JPEG2000 codestream format
    
      JP2 : JPEG2000 JP2 container format
    """
    J2K: typing.ClassVar[Jpeg2kBitstreamType]  # value = <Jpeg2kBitstreamType.J2K: 0>
    JP2: typing.ClassVar[Jpeg2kBitstreamType]  # value = <Jpeg2kBitstreamType.JP2: 1>
    __members__: typing.ClassVar[dict[str, Jpeg2kBitstreamType]]  # value = {'J2K': <Jpeg2kBitstreamType.J2K: 0>, 'JP2': <Jpeg2kBitstreamType.JP2: 1>}
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
class Jpeg2kEncodeParams:
    """
    Class to define parameters for JPEG2000 image encoding operations.
    """
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor that initializes the Jpeg2kEncodeParams object with default settings.
        """
    @typing.overload
    def __init__(self, reversible: bool = False, code_block_size: tuple[int, int] = (64, 64), num_resolutions: int = 6, bitstream_type: Jpeg2kBitstreamType = ..., prog_order: Jpeg2kProgOrder = ...) -> None:
        """
                    Constructor with parameters to control the JPEG2000 encoding process.
        
                    Args:
                        reversible: Boolean flag to use reversible JPEG2000 transform. Defaults to False (irreversible).
        
                        code_block_size: Tuple representing the height and width of code blocks in the encoding. Defaults to (64, 64).
                        
                        num_resolutions: Number of resolution levels for the image. Defaults to 6.
                        
                        bitstream_type: Type of JPEG2000 bitstream, either raw codestream or JP2 container. Defaults to JP2.
                        
                        prog_order: Progression order for the JPEG2000 encoding. Defaults to RPCL (Resolution-Position-Component-Layer).
        """
    @property
    def bitstream_type(self) -> Jpeg2kBitstreamType:
        """
                    Property to get or set the JPEG2000 bitstream type.
        
                    Determines the type of container or codestream for the encoded image. Defaults to JP2.
        """
    @bitstream_type.setter
    def bitstream_type(self, arg1: Jpeg2kBitstreamType) -> None:
        ...
    @property
    def code_block_size(self) -> tuple[int, int]:
        """
                    Property to get or set the code block width and height for encoding.
        
                    Defines the size of code blocks used in JPEG2000 encoding. Defaults to (64, 64).
        """
    @code_block_size.setter
    def code_block_size(self, arg1: tuple[int, int]) -> None:
        ...
    @property
    def num_resolutions(self) -> int:
        """
                    Property to get or set the number of resolution levels.
        
                    Determines the number of levels for the image's resolution pyramid. Each additional level represents a halving of the resolution.
                    Defaults to 6.
        """
    @num_resolutions.setter
    def num_resolutions(self, arg1: int) -> None:
        ...
    @property
    def prog_order(self) -> Jpeg2kProgOrder:
        """
                    Property to get or set the progression order for the JPEG2000 encoding.
        
                    Specifies the order in which the encoded data is organized. It can affect decoding performance and streaming. Defaults to RPCL.
        """
    @prog_order.setter
    def prog_order(self, arg1: Jpeg2kProgOrder) -> None:
        ...
    @property
    def reversible(self) -> bool:
        """
                    Boolean property to enable or disable the reversible JPEG2000 transform.
        
                    When set to True, uses a reversible transform ensuring lossless compression. Defaults to False (irreversible).
        """
    @reversible.setter
    def reversible(self, arg1: bool) -> None:
        ...
class Jpeg2kProgOrder:
    """
    Enum representing progression orders in the JPEG2000 standard.
    
    Members:
    
      LRCP : 
                Layer-Resolution-Component-Position progression order.
    
                This progression order encodes data by layer first, then by resolution, 
                component, and position, optimizing for scalability in quality.
                
    
      RLCP : 
                Resolution-Layer-Component-Position progression order.
    
                This progression order encodes data by resolution first, followed by layer,
                component, and position, optimizing for scalability in resolution.
                
    
      RPCL : 
                Resolution-Position-Component-Layer progression order.
    
                This progression order encodes data by resolution first, then by position,
                component, and layer, which is useful for progressive transmission by 
                resolution.
                
    
      PCRL : 
                Position-Component-Resolution-Layer progression order.
    
                This progression order encodes data by position first, followed by component,
                resolution, and layer. It is beneficial for progressive transmission by spatial area.
                
    
      CPRL : 
                Component-Position-Resolution-Layer progression order.
    
                This progression order encodes data by component first, then by position,
                resolution, and layer, optimizing for scalability in component access.
                
    """
    CPRL: typing.ClassVar[Jpeg2kProgOrder]  # value = <Jpeg2kProgOrder.CPRL: 4>
    LRCP: typing.ClassVar[Jpeg2kProgOrder]  # value = <Jpeg2kProgOrder.LRCP: 0>
    PCRL: typing.ClassVar[Jpeg2kProgOrder]  # value = <Jpeg2kProgOrder.PCRL: 3>
    RLCP: typing.ClassVar[Jpeg2kProgOrder]  # value = <Jpeg2kProgOrder.RLCP: 1>
    RPCL: typing.ClassVar[Jpeg2kProgOrder]  # value = <Jpeg2kProgOrder.RPCL: 2>
    __members__: typing.ClassVar[dict[str, Jpeg2kProgOrder]]  # value = {'LRCP': <Jpeg2kProgOrder.LRCP: 0>, 'RLCP': <Jpeg2kProgOrder.RLCP: 1>, 'RPCL': <Jpeg2kProgOrder.RPCL: 2>, 'PCRL': <Jpeg2kProgOrder.PCRL: 3>, 'CPRL': <Jpeg2kProgOrder.CPRL: 4>}
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
class JpegEncodeParams:
    """
    Class to define parameters for JPEG image encoding operations. It provides settings to configure JPEG encoding such as enabling progressive encoding and optimizing Huffman tables.
    """
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor that initializes the JpegEncodeParams object with default settings.
        """
    @typing.overload
    def __init__(self, progressive: bool = False, optimized_huffman: bool = False) -> None:
        """
                    Constructor with parameters to control the JPEG encoding process.
        
                    Args:
                        progressive: Boolean flag to use progressive JPEG encoding. Defaults to False.
                        
                        optimized_huffman: Boolean flag to use optimized Huffman tables for JPEG encoding. Defaults to False.
        """
    @property
    def optimized_huffman(self) -> bool:
        """
                    Boolean property to enable or disable the use of optimized Huffman tables in JPEG encoding.
        
                    When set to True, the JPEG encoding process will use optimized Huffman tables which produce smaller file sizes but may require more processing time. Defaults to False.
        """
    @optimized_huffman.setter
    def optimized_huffman(self, arg1: bool) -> None:
        ...
    @property
    def progressive(self) -> bool:
        """
                    Boolean property to enable or disable progressive JPEG encoding.
        
                    When set to True, the encoded JPEG will be progressive, meaning it can be rendered in successive waves of detail. Defaults to False.
        """
    @progressive.setter
    def progressive(self, arg1: bool) -> None:
        ...
class LoadHintPolicy:
    """
    
                Enum representing load hint policies for backend batch processing.
    
                Load hint is used to calculate the fraction of the batch items that will be picked by
                this backend and the rest of the batch items would be passed to fallback codec.
                This is just a hint and a particular implementation can choose to ignore it.
                
    
    Members:
    
      IGNORE : 
                Ignore the load hint.
    
                In this policy, the backend does not take the load hint into account when 
                determining batch processing. It functions as if no hint was provided.
                
    
      FIXED : 
                Use the load hint to determine a fixed batch size.
    
                This policy calculates the backend batch size based on the provided load hint 
                once, and uses this fixed batch size for processing.  
                
    
      ADAPTIVE_MINIMIZE_IDLE_TIME : 
                Adaptively use the load hint to minimize idle time.
    
                This policy uses the load hint as an initial starting point and recalculates 
                on each iteration to dynamically adjust and reduce the idle time of threads, 
                optimizing overall resource utilization.
                
    """
    ADAPTIVE_MINIMIZE_IDLE_TIME: typing.ClassVar[LoadHintPolicy]  # value = <LoadHintPolicy.ADAPTIVE_MINIMIZE_IDLE_TIME: 3>
    FIXED: typing.ClassVar[LoadHintPolicy]  # value = <LoadHintPolicy.FIXED: 2>
    IGNORE: typing.ClassVar[LoadHintPolicy]  # value = <LoadHintPolicy.IGNORE: 1>
    __members__: typing.ClassVar[dict[str, LoadHintPolicy]]  # value = {'IGNORE': <LoadHintPolicy.IGNORE: 1>, 'FIXED': <LoadHintPolicy.FIXED: 2>, 'ADAPTIVE_MINIMIZE_IDLE_TIME': <LoadHintPolicy.ADAPTIVE_MINIMIZE_IDLE_TIME: 3>}
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
class Region:
    """
    
                Class representing a region of interest within an image.
    
                The dimensions are oriented such that the top-left corner is (0,0).
                
    """
    @typing.overload
    def __init__(self) -> None:
        """
        Default constructor that initializes an empty Region object.
        """
    @typing.overload
    def __init__(self, start_y: int, start_x: int, end_y: int, end_x: int) -> None:
        """
                    Constructor that initializes a Region with specified start and end coordinates.
        
                    Args:
                        start_y: Starting Y coordinate.
        
                        start_x: Starting X coordinate.
                        
                        end_y: Ending Y coordinate.
                        
                        end_x: Ending X coordinate.
        """
    @typing.overload
    def __init__(self, start: list[int], end: list[int]) -> None:
        """
                    Constructor that initializes a Region with start and end coordinate lists.
        
                    Args:
                        start: List of starting coordinates.
        
                        end: List of ending coordinates.
        """
    @typing.overload
    def __init__(self, start: tuple, end: tuple) -> None:
        """
                    Constructor that initializes a Region with start and end coordinate tuples.
        
                    Args:
                        start: Tuple of starting coordinates.
                        
                        end: Tuple of ending coordinates.
        """
    def __repr__(self) -> str:
        """
                    String representation of the Region object.
        
                    Returns:
                        A string representing the Region.
        """
    @property
    def end(self) -> tuple:
        """
                    Property to get the end coordinates of the Region.
        
                    Returns:
                        A list of ending coordinates.
        """
    @property
    def ndim(self) -> int:
        """
                    Property to get the number of dimensions in the Region.
        
                    Returns:
                        The number of dimensions.
        """
    @property
    def start(self) -> tuple:
        """
                    Property to get the start coordinates of the Region.
        
                    Returns:
                        A list of starting coordinates.
        """
def as_image(source: typing.Any, cuda_stream: int = 0) -> Image:
    """
            Wraps an external buffer as an image and ties the buffer lifetime to the image.
            
            At present, the image must always have a three-dimensional shape in the HWC layout (height, width, channels), 
            which is also known as the interleaved format, and be stored as a contiguous array in C-style.
    
            Args:
                source: Input DLPack tensor which is encapsulated in a PyCapsule object or other object 
                        with __cuda_array_interface__, __array_interface__ or __dlpack__ and __dlpack_device__ methods.
                
                cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place in the created Image.
    
            Returns:
                nvimgcodec.Image
    """
def as_images(sources: list[typing.Any], cuda_stream: int = 0) -> list[typing.Any]:
    """
                Wraps all an external buffers as an images and ties the buffers lifetime to the images.
                
                At present, the image must always have a three-dimensional shape in the HWC layout (height, width, channels), 
                which is also known as the interleaved format, and be stored as a contiguous array in C-style.
    
                Args:
                    sources: List of input DLPack tensors which is encapsulated in a PyCapsule objects or other objects 
                             with __cuda_array_interface__, __array_interface__ or __dlpack__ and __dlpack_device__ methods.
                    
                    cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place in created Image.
    
                Returns:
                    List of nvimgcodec.Image's
    """
def from_dlpack(source: typing.Any, cuda_stream: int = 0) -> Image:
    """
                Zero-copy conversion from a DLPack tensor to a image. 
    
                Args:
                    source: Input DLPack tensor which is encapsulated in a PyCapsule object or other (array) object 
                            with __dlpack__  and __dlpack_device__ methods.
                    
                    cuda_stream: An optional cudaStream_t represented as a Python integer, upon which synchronization must take place in created Image.
                
                Returns:
                    nvimgcodec.Image
    """
ADAPTIVE_MINIMIZE_IDLE_TIME: LoadHintPolicy  # value = <LoadHintPolicy.ADAPTIVE_MINIMIZE_IDLE_TIME: 3>
CPRL: Jpeg2kProgOrder  # value = <Jpeg2kProgOrder.CPRL: 4>
CPU_ONLY: BackendKind  # value = <BackendKind.CPU_ONLY: 1>
CSS_410: ChromaSubsampling  # value = <ChromaSubsampling.CSS_410: 6>
CSS_410V: ChromaSubsampling  # value = <ChromaSubsampling.CSS_410V: 8>
CSS_411: ChromaSubsampling  # value = <ChromaSubsampling.CSS_411: 5>
CSS_420: ChromaSubsampling  # value = <ChromaSubsampling.CSS_420: 3>
CSS_422: ChromaSubsampling  # value = <ChromaSubsampling.CSS_422: 2>
CSS_440: ChromaSubsampling  # value = <ChromaSubsampling.CSS_440: 4>
CSS_444: ChromaSubsampling  # value = <ChromaSubsampling.CSS_444: 0>
CSS_GRAY: ChromaSubsampling  # value = <ChromaSubsampling.CSS_GRAY: 7>
FIXED: LoadHintPolicy  # value = <LoadHintPolicy.FIXED: 2>
GPU_ONLY: BackendKind  # value = <BackendKind.GPU_ONLY: 2>
GRAY: ColorSpec  # value = <ColorSpec.GRAY: 2>
HW_GPU_ONLY: BackendKind  # value = <BackendKind.HW_GPU_ONLY: 4>
HYBRID_CPU_GPU: BackendKind  # value = <BackendKind.HYBRID_CPU_GPU: 3>
IGNORE: LoadHintPolicy  # value = <LoadHintPolicy.IGNORE: 1>
J2K: Jpeg2kBitstreamType  # value = <Jpeg2kBitstreamType.J2K: 0>
JP2: Jpeg2kBitstreamType  # value = <Jpeg2kBitstreamType.JP2: 1>
LRCP: Jpeg2kProgOrder  # value = <Jpeg2kProgOrder.LRCP: 0>
PCRL: Jpeg2kProgOrder  # value = <Jpeg2kProgOrder.PCRL: 3>
RGB: ColorSpec  # value = <ColorSpec.RGB: 1>
RLCP: Jpeg2kProgOrder  # value = <Jpeg2kProgOrder.RLCP: 1>
RPCL: Jpeg2kProgOrder  # value = <Jpeg2kProgOrder.RPCL: 2>
STRIDED_DEVICE: ImageBufferKind  # value = <ImageBufferKind.STRIDED_DEVICE: 1>
STRIDED_HOST: ImageBufferKind  # value = <ImageBufferKind.STRIDED_HOST: 2>
UNCHANGED: ColorSpec  # value = <ColorSpec.UNCHANGED: 0>
YCC: ColorSpec  # value = <ColorSpec.YCC: 3>
__cuda_version__: int = 11080
__version__: str = '0.5.0'
