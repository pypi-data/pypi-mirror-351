from typing import Union

from quark.types.registry.quark.ai import (
    OpenAIEmbeddingRunParams as OpenAIEmbeddingsInput,
    OpenAICompletionBaseRunParams as OpenAICompletionsInput,
)
from quark.types.registry.quark.files import (
    S3ReadFilesBinaryRunParams as S3ReadCSVQuarkInput,
    S3ReadFilesBinaryRunParams as S3ReadWholeFileQuarkInput,
)
from quark.types.registry.quark.vector import (
    LancedbIngestRunParams as VectorDBIngestInput,
    LancedbSearchRunParams as VectorDBSearchInput,
)
from quark.types.registry.quark.databases import SnowflakeReadRunParams as SnowflakeReadInput
from quark.types.registry.quark.extractor import DoclingExtractorRunParams as DocExtractQuarkInput
from quark.types.registry.quark.transformer import (
    DoclingChunkerRunParams as DocChunkerQuarkInput,
    HandlebarsBaseRunParams as TextTemplateInput,
)

QuarkInput = Union[
    S3ReadCSVQuarkInput,
    S3ReadWholeFileQuarkInput,
    DocExtractQuarkInput,
    TextTemplateInput,
    OpenAIEmbeddingsInput,
    OpenAICompletionsInput,
    DocChunkerQuarkInput,
    SnowflakeReadInput,
    VectorDBIngestInput,
    VectorDBSearchInput,
    None,
]

__all__ = [
    "QuarkInput",
    "S3ReadCSVQuarkInput",
    "S3ReadWholeFileQuarkInput",
    "DocExtractQuarkInput",
    "TextTemplateInput",
    "OpenAIEmbeddingsInput",
    "OpenAICompletionsInput",
    "DocChunkerQuarkInput",
    "SnowflakeReadInput",
    "VectorDBIngestInput",
    "VectorDBSearchInput",
]
