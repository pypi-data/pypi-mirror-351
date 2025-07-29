# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.
#
# chATLAS_Embed/__init__.py
"""A modular Python package for efficient embedding workflows and PostgreSQL-
based vector store management with parent-child relationships."""


from chATLAS_Embed.Base import Document
from chATLAS_Embed.VectorStoreCreators import (
    TWikiTextVectorStoreCreator,
    TWikiHTMLVectorStoreCreator,
    CDSTextVectorStoreCreator,
    IndicoTranscriptsVectorStoreCreator,
    syncedTwikiVectorStoreCreator,
)
from chATLAS_Embed.VectorStores import PostgresParentChildVectorStore
from chATLAS_Embed.TextSplitters import ParagraphTextSplitter, RecursiveTextSplitter
from chATLAS_Embed.LangChainVectorStore import LangChainVectorStore
