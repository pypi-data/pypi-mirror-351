# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 CERN.
#
# chATLAS_Embed is free software; you can redistribute it and/or modify
# it under the terms of the Apache 2.0 license; see LICENSE file for more details.
# `chATLAS_Embed/EmbeddingModels.py`

"""Collection of Embedding models to use."""

from typing import List

from sentence_transformers import SentenceTransformer

from chATLAS_Embed.Base import EmbeddingModel


class SentenceTransformerEmbedding(EmbeddingModel):
    """Implements embedding using sentence-transformers."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        batch_size: int = 64,
    ):
        """
        :param str model_name: HuggingFace sentence transformer embedding model to use
        :param batch_size: Batch size for parralel processing
        :type batch_size: int
        """
        self.model: SentenceTransformer = SentenceTransformer(model_name)
        self.vector_size: int = (
            self.model.get_sentence_embedding_dimension()
        )  # Get vector size
        self.batch_size = batch_size

    def embed(
        self, texts: List[str] | str, show_progress_bar: bool = None
    ) -> List[List[float]]:
        """Embed documents or queries using the embeding model.


        :param texts: (List[str] | str) - Text(s) to embed
        :param show_progress_bar: (bool) - Show tqdm progress bar of embedding

        :return:
        Vector Embedding: (List[List[float]])
        """
        return self.model.encode(
            texts, show_progress_bar=show_progress_bar, batch_size=self.batch_size
        ).tolist()
