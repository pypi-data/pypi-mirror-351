# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.

"""A collection of different Text Splitters to use."""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from chATLAS_Embed.Base import TextSplitter


class ParagraphTextSplitter(TextSplitter):
    """Splits text based on paragraphs using spaCy."""

    def __init__(self, max_tokens: int = 512):
        import spacy

        self.nlp = spacy.load("en_core_web_sm")
        self.max_tokens = max_tokens

    def split(self, text: str) -> List[str]:
        doc = self.nlp(text)
        paragraphs = []
        current_para = []
        current_tokens = 0

        for sent in doc.sents:
            sent_tokens = len(sent)
            if current_tokens + sent_tokens > self.max_tokens:
                if current_para:
                    paragraphs.append(" ".join(current_para))
                current_para = [sent.text]
                current_tokens = sent_tokens
            else:
                current_para.append(sent.text)
                current_tokens += sent_tokens

        if current_para:
            paragraphs.append(" ".join(current_para))
        return paragraphs

    def count_tokens(self, text: str) -> int:
        return len(self.nlp(text))


class RecursiveTextSplitter(TextSplitter):
    """A standard langchain Recursive Text Splitter."""

    def __init__(self, chunk_size=2048, chunk_overlap=24):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def split(self, text: str) -> List[str]:
        return self.splitter.split_text(text)

    def count_tokens(self, text: str) -> int:
        # Not currently implemented or used
        raise NotImplementedError("Token counting is not implemented yet.")
