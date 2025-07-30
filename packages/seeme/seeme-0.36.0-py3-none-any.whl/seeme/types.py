from pydantic import BaseModel, NonNegativeInt
from typing import List, Optional, Union
from enum import Enum
from enum import Enum as BaseEnum
from enum import EnumMeta as BaseEnumMeta

# -- Base Classes --

class EnumMeta(BaseEnumMeta):
    # https://stackoverflow.com/questions/43634618/how-do-i-test-if-int-value-exists-in-python-enum-without-using-try-catch
    def __contains__(self, item):
        return isinstance(item, self) or item in {
            v.value for v in self.__members__.values()
        }

    # https://stackoverflow.com/questions/29503339/how-to-get-all-values-from-python-enum-class
    def __str__(self):
        return ", ".join(c.value for c in self)

    def __repr__(self):
        return self.__str__()

class Enum(BaseEnum, metaclass=EnumMeta):
    def __str__(self):
        return str(self.value)

class Base(BaseModel):
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # model_config = ConfigDict(
    #         protected_namespaces=(),
    #         extra="ignore",
    #         arbitrary_types_allowed=False,
    # )
    class Config:  
        use_enum_values = True
        protected_namespaces=()
        extra="ignore"
        arbitrary_types_allowed=False


class NameBase(Base):
    name: str = None
    description: Optional[str] = ""


class Metric(NameBase):
    model_version_id: Optional[str] = None
    value: float = 0.0

# -- Enums --

class JobType(str, Enum):
    TRAINING    = "training"
    VALIDATION  = "validation"
    CONVERSION  = "conversion"

class JobStatus(str, Enum):
    WAITING     = "waiting"
    STARTED     = "started"
    FINISHED    = "finished"
    ERROR       = "error"

class ValueType(str, Enum):
    FLOAT              = 'float'
    INT                = 'int'
    TEXT               = 'text'
    STRING_ARRAY       = 'string_array'
    BOOL               = 'boolean'
    NUMBER             = 'number' # will be deprecated
    MULTI              = 'multi'

class DatasetFormat(str, Enum):
    FOLDERS     = "folders"
    YOLO        = "yolo"
    CSV         = "csv"
    SPACY_NER   = "spacy-ner"

class DatasetContentType(str, Enum):
    IMAGES      = "images"
    TEXT        = "text"
    TABULAR     = "tabular"
    NER         = "ner"
    DOCUMENTS   = "documents"

class AssetType(str, Enum):
    PKL             = "pkl"
    PT              = "pt"
    MLMODEL         = "mlmodel"
    TFLITE          = "tflite"
    ONNX            = "onnx"
    ONNX_INT8       = "onnx_int8"
    LABELS          = "labels"
    NAMES           = "names"
    WEIGHTS         = "weights"
    CFG             = "cfg"
    CONVERSION_CFG  = "conversion_cfg"
    LOGO            = "logo"

class ApplicationType(str, Enum):
    IMAGE_CLASSIFICATION    = "image_classification"
    OBJECT_DETECTION        = "object_detection"
    TEXT_CLASSIFICATION     = "text_classification"
    LANGUAGE_MODEL          = "language_model"
    LLM                     = "llm"
    STRUCTURED              = "structured"
    NER                     = "ner"
    OCR                     = "ocr"
    SPEECH_TO_TEXT          = "speech_to_text"
    SEARCH                  = "search"

class Framework(str, Enum):
    PYTORCH                 = "pytorch"
    FASTAI                  = "fastai"
    YOLO                    = "yolo"
    XGBOOST                 = "xgboost"
    CATBOOST                = "catboost"
    LIGHTGBM                = "lightgbm"
    SPACY                   = "spacy"
    TESSERACT               = "tesseract"
    ONNX                    = "onnx"
    COREML                  = "coreml"
    TFLITE                  = "tflite"
    LLAMA_CPP_PYTHON        = "llama-cpp-python"
    WHISPER                 = "whisper"
    #PARAKEET                = "parakeet"
    INSANELY_FAST_WHISPER   = "insanely-fast-whisper"
    BM25S                   = "bm25s"

# -- Shares --

class Shareable(NameBase):
    user_id: Optional[str] = None
    notes: Optional[str] = None
    has_logo: Optional[bool] = False
    logo: Optional[str] = ""
    public: Optional[bool] = False
    shared_with_me: Optional[bool] = False


class Share(Base):
    email: str
    entity_type: str
    entity_id: str
    without_invite: Optional[bool] = True

# -- Models --

class Model(Shareable):
    active_version_id: Optional[str] = ""
    can_inference: Optional[bool] = False
    kind: Optional[str] = ""
    config: Optional[str] = ""
    application_id: Optional[str] = ""
    has_ml_model: Optional[bool] = False
    has_onnx_model: Optional[bool] = False
    has_onnx_int8_model: Optional[bool] = False
    has_tflite_model: Optional[bool] = False
    has_labels_file: Optional[bool] = False
    auto_convert: Optional[bool] = True
    privacy_enabled: Optional[bool] = False


class ModelVersion(NameBase):
    model_id: Optional[str] = None
    user_id: Optional[str] = ""
    can_inference: Optional[bool] = False
    has_logo: Optional[bool] = False
    config: Optional[str] = ""
    application_id: str
    version: Optional[str] = ""
    version_number: Optional[int] = None
    has_ml_model: Optional[bool] = False
    has_onnx_model: Optional[bool] = False
    has_onnx_int8_model: Optional[bool] = False
    has_tflite_model: Optional[bool] = False
    has_labels_file: Optional[bool]= False
    dataset_id: Optional[str] = ""
    dataset_version_id: Optional[str] = ""
    job_id: Optional[str] = ""
    metrics: Optional[List[Metric]] = []


# -- Datasets --

class Label(NameBase):
    user_id: Optional[str] = ""
    version_id: str
    color: Optional[str] = ""
    index: Optional[int] = 0
    shortcut: Optional[str] = ""


class LabelStat(Base):
    label_id: str
    split_id: str
    count: Optional[NonNegativeInt] = 0
    annotation_count: Optional[NonNegativeInt] = 0
    item_count: Optional[NonNegativeInt] = 0


class Annotation(Base):
    label_id: str
    item_id: str
    split_id: str
    coordinates: Optional[str] = ""
    user_id: Optional[str] = ""


class DatasetSplit(NameBase):
    user_id: Optional[str] = ""
    version_id: str


class DatasetItem(NameBase):
    user_id: Optional[str] = ""
    text: Optional[str] = ""
    splits: Optional[List[DatasetSplit]] = []
    annotations: Optional[List[Annotation]] = []
    extension: Optional[str] = ""


class DatasetVersion(NameBase):
    labels: Optional[List[Label]] = []
    user_id: Optional[str] = ""
    dataset_id: str
    splits: Optional[List[DatasetSplit]] = []
    default_split: Optional[str] = ""
    config: Optional[str] = ""


class Dataset(Shareable):
    versions: Optional[List[DatasetVersion]] = []
    multi_label: bool = False
    default_splits: bool = False
    content_type: Union[str,DatasetContentType]

# -- Workflows --

class WorkflowEdge(NameBase):
    user_id: Optional[str] = ""
    version_id: str

class WorkflowNode(NameBase):
    user_id: Optional[str] = ""
    version_id: str

class WorkflowVersion(NameBase):
    user_id: Optional[str] = ""
    workflow_id: str
    nodes: Optional[List[WorkflowNode]] = []
    edges: Optional[List[WorkflowEdge]] = []

class Workflow(Shareable):
    versions: Optional[List[WorkflowVersion]] = []

# -- Jobs --

class JobItem(NameBase):
    job_id: Optional[str] = None
    default_value: Optional[str] = ""
    value_type: Union[ValueType, str]
    label: str
    value: Optional[str] = ""

class Job(NameBase):
    job_type: Optional[JobType] 
    application_id: Optional[str] = ""
    status: Optional[JobStatus] 
    status_message: Optional[str] = ""
    user_id: Optional[str] = ""
    cpu_start_time: Optional[str] = ""
    cpu_end_time: Optional[str] = ""
    gpu_start_time: Optional[str] = ""
    gpu_end_time: Optional[str] = ""
    agent_name: Optional[str] = ""
    dataset_id: Optional[str] = ""
    dataset_version_id: Optional[str] = ""
    model_id: Optional[str] = ""
    model_version_id: Optional[str] = ""
    start_model_id: Optional[str] = ""
    start_model_version_id: Optional[str] = ""
    items: Optional[List[JobItem]] = []


# -- Login --

class Registration(BaseModel):
    username: str
    email: str
    name: Optional[str]
    firstname: Optional[str]
    password: str


class Credentials(BaseModel):
    username: str
    password: str


class LoginReply(BaseModel):
    id: str
    username: str
    name: str
    email: str
    firstname: str
    apikey: str


class RegistrationError(BaseModel):
    message: Optional[str]
    severity: Optional[str]
    registration: Optional[Registration]


class User(Base):
    username: Optional[str]
    email: Optional[str]
    name: Optional[str]
    firstname: Optional[str]
    apikey: Optional[str]

# -- Inferences --

class TextInput(BaseModel):
    input_text: Optional[str]

class InferenceItem(Base):
    prediction: Optional[str]  = ""
    confidence: Optional[float] = 0.0
    inference_id: Optional[str] = ""
    coordinates: Optional[str] = ""


class Inference(NameBase):
    prediction: Optional[str] = "" # deprecated
    confidence: Optional[float] = 0.0# deprecated
    model_id: Optional[str] = ""
    model_version_id: Optional[str] = ""
    extension: Optional[str] = ""
    user_id: Optional[str] = ""
    error_reported: Optional[bool] = False
    error: Optional[str] = ""
    application_id: Optional[str] = ""
    inference_host: Optional[str] = ""
    inference_time: Optional[str] = ""
    end_to_end_time: Optional[str] = ""
    dataset_item_id: Optional[str] = ""
    result: Optional[str] = ""
    inference_items: Optional[List[InferenceItem]] = []
    hidden: Optional[bool] = False
    privacy_enabled: Optional[bool] = False
    config: Optional[str] = ""


class AddInferences(BaseModel):
    keep_annotations: bool = True
    inferences: List[Inference] = []

# -- Applications --


class Application(NameBase):
    base_framework: Optional[str]
    base_framework_version: Optional[str]
    framework: Optional[str]
    framework_version: Optional[str]
    application: Optional[str]
    inference_host: Optional[str]
    can_convert_to_onnx: Optional[bool]
    can_convert_to_tensorflow: Optional[bool]
    can_convert_to_tflite: Optional[bool]
    continual_training: Optional[bool]
    has_embedding_support: Optional[bool]
    has_labels_file: Optional[bool]
    inference_extensions: Optional[str]