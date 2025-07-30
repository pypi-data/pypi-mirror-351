from __future__ import annotations, absolute_import

from quark.types.history import LatticeHistoryItem
from quark.types.registry import QuarkRegistryItem
from quark.types.registry.quark.files import QuarkHistoryItem

from .driver import *
from .inputs import *
from .quarks import *

LatticeStatus = Literal["New", "Scheduled", "Running", "Completed", "Failed"]
QuarkStatus = Literal["New", "Scheduled", "Running", "OutputStaged", "Completed", "Failed"]

__banner__ = f"""
                                                              ________    
     ____                   __   __          __             /\        \  
    / __ \__  ______ ______/ /__/ /   ____ _/ /_  _____    /  \        \ 
   / / / / / / / __ `/ ___/ //_/ /   / __ `/ __ \/ ___/   /    \________\ 
  / /_/ / /_/ / /_/ / /  / ,< / /___/ /_/ / /_/ (__  )    \    /        /  
  \___\_\__,_/\__,_/_/  /_/|_/_____/\__,_/_.___/____/      \  /        / 
                                                            \/________/   
   (c)1985 Quark Labs, Inc. All rights reserved.                       

   Quarkupy 1.0.0
   """

__all__ = [
    "__banner__",
    "QuarkRemoteDriver",
    "LatticeStatus",
    "QuarkStatus",
    "QuarkInput",
    "QuarkHistoryItem",
    "QuarkRegistryItem",
    "LatticeHistoryItem",
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
    "OpenAICompletionBaseQuark",
    "OpenAIEmbeddingsQuark",
    "DocExtractQuark",
    "DocChunkerQuark",
    "VectorDBIngestQuark",
    "VectorDBSearchQuark",
    "S3ReadCSVQuark",
    "S3ReadWholeFileQuark",
    "TextTemplateBaseQuark",
    "DocChunkerQuark",
]
