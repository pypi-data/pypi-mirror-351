import json
import pickle
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import torch
from scipy import linalg
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils import as_float_array, check_array
from sklearn.utils.validation import check_is_fitted
from tqdm.auto import tqdm
from transformers import AutoModel, AutoTokenizer


class ZCA(BaseEstimator, TransformerMixin):
    """ZCA whitening transform.

    Transforms data to have zero mean and identity covariance.

    Args:
        regularization (float): Regularization parameter for ZCA. Defaults to 1e-6.
        copy (bool): If True, a copy of X will be created. If False, X may be
            overwritten. Defaults to False.
    """

    def __init__(self, regularization: float = 1e-6, copy: bool = False):
        self.regularization = regularization
        self.copy = copy

    def fit(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> "ZCA":
        """Compute the mean, whitening and dewhitening matrices.

        Args:
            X (np.ndarray): Array-like with shape [n_samples, n_features].
                The data used to compute the mean, whitening and dewhitening matrices.
            y (Optional[np.ndarray]): Ignored. Present for API consistency.

        Returns:
            ZCA: The fitted ZCA transformer.
        """
        X = check_array(X, accept_sparse=None, copy=self.copy, ensure_2d=True)
        X = as_float_array(X, copy=self.copy)
        self.mean_ = X.mean(axis=0)
        X_ = X - self.mean_
        cov = np.dot(X_.T, X_) / (X_.shape[0] - 1)
        U, S, _ = linalg.svd(cov)
        s_val = np.sqrt(S.clip(self.regularization))
        s_inv = np.diag(1.0 / s_val)
        s_diag = np.diag(s_val)
        self.whiten_ = np.dot(np.dot(U, s_inv), U.T)
        self.dewhiten_ = np.dot(np.dot(U, s_diag), U.T)
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X: np.ndarray, y: Optional[np.ndarray] = None) -> np.ndarray:
        """Perform ZCA whitening.

        Args:
            X (np.ndarray): Array-like with shape [n_samples, n_features].
                The data to whiten along the features axis.
            y (Optional[np.ndarray]): Ignored. Present for API consistency.

        Returns:
            np.ndarray: The whitened data.
        """
        check_is_fitted(self, "mean_")
        X = as_float_array(X, copy=self.copy)
        return np.dot(X - self.mean_, self.whiten_.T)

    def inverse_transform(
        self, X: np.ndarray, copy: Optional[bool] = None
    ) -> np.ndarray:
        """Undo the ZCA transform and rotate back to the original representation.

        Args:
            X (np.ndarray): Array-like with shape [n_samples, n_features].
                The data to rotate back.
            copy (Optional[bool]): Whether to copy X before transforming.
                If None, uses self.copy. Defaults to None.

        Returns:
            np.ndarray: The original data representation.
        """
        check_is_fitted(self, "mean_")
        X = as_float_array(X, copy=copy if copy is not None else self.copy)
        return np.dot(X, self.dewhiten_) + self.mean_


class MarketingEmphasisScorer:
    """Scores texts on marketing emphasis dimensions across multiple constructs.

    This class measures marketing emphasis in text data using Hugging Face transformers
    and mean pooling for three predefined constructs: 'orientation', 'capabilities', and 'excellence'.
    It loads keywords and pre-trained ZCA transformations for each construct
    and provides aggregated scores.
    """

    CONSTRUCT_NAMES = [
        "marketing_orientation",
        "marketing_capabilities",
        "marketing_excellence",
    ]

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-mpnet-base-v2",
        max_length: int = 512,
        chunk_overlap: int = 0,
        device: Optional[str] = None,
        keywords_path_overrides: Optional[Dict[str, str]] = None,
        zca_path_overrides: Optional[Dict[str, str]] = None,
    ) -> None:
        """Initializes the MarketingEmphasisScorer for all constructs.

        Args:
            model_name (str): Name of the Hugging Face transformer model.
                Defaults to "sentence-transformers/all-mpnet-base-v2".
            max_length (int): Maximum sequence length for tokenization. Defaults to 512.
            chunk_overlap (int): Number of tokens to overlap between chunks. Defaults to 0.
            device (Optional[str]): Device to run the model on. If None, auto-detects.
                Defaults to None.
            keywords_path_overrides (Optional[Dict[str, str]]): Dictionary mapping
                construct names (e.g., "orientation") to specific keyword JSON file paths.
                If a construct is not in this dict, its default path will be used.
                The specified files must exist. Defaults to None.
            zca_path_overrides (Optional[Dict[str, str]]): Dictionary mapping
                construct names to specific pre-trained ZCA transformer files (.pkl or .npz).
                If a construct is not in this dict, its default path will be used if found.
                Defaults to None.

        Raises:
            FileNotFoundError: If a required keyword file (either from override or default)
                cannot be found for any construct.
            ValueError: If an override path is invalid.
        """
        self.model_name = model_name
        self.max_length = max_length
        self.chunk_overlap = chunk_overlap

        # Set device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Get the package directory for resolving data file paths
        self._package_dir = Path(__file__).parent

        self.keywords_by_construct: Dict[str, Dict[str, List[str]]] = {}
        self.dimension_embeddings_by_construct: Dict[str, Dict[str, np.ndarray]] = {}
        self.zca_transformers: Dict[str, Optional[ZCA]] = {}
        self.keywords_sources: Dict[str, str] = {}
        self.all_dimension_names: List[str] = []  # To store all 19 dimension names

        if keywords_path_overrides is None:
            keywords_path_overrides = {}
        if zca_path_overrides is None:
            zca_path_overrides = {}

        for construct_name in self.CONSTRUCT_NAMES:
            # Load Keywords for the construct
            actual_keywords_file: Optional[str] = None
            keywords_source: str = "unknown"

            override_path = keywords_path_overrides.get(construct_name)
            if override_path:
                path_obj = Path(override_path)
                if path_obj.exists() and path_obj.is_file():
                    actual_keywords_file = str(path_obj)
                    keywords_source = f"override_file: {actual_keywords_file}"
                else:
                    raise FileNotFoundError(
                        f"Provided keywords override file for construct '{construct_name}' ('{override_path}') not found or is not a file."
                    )
            else:
                default_keywords_path = (
                    self._package_dir / "seeds" / f"{construct_name.lower()}.json"
                )
                if default_keywords_path.exists() and default_keywords_path.is_file():
                    actual_keywords_file = str(default_keywords_path)
                    keywords_source = f"construct_default_seed: {actual_keywords_file}"
                else:
                    raise FileNotFoundError(
                        f"Default keywords file for construct '{construct_name}' ('{default_keywords_path}') not found. "
                        "Please ensure the file exists or provide a 'keywords_path_override'."
                    )

            current_keywords = self._load_local_keywords(actual_keywords_file)
            self.keywords_by_construct[construct_name] = current_keywords
            self.keywords_sources[construct_name] = keywords_source

            # Create and store dimension embeddings
            current_dim_embeddings = self._create_dimension_embeddings_for_construct(
                current_keywords
            )
            self.dimension_embeddings_by_construct[construct_name] = (
                current_dim_embeddings
            )

            # Store all dimension names, ensure uniqueness if necessary (though should be unique by design of keyword files)
            for dim_name in current_keywords.keys():
                if dim_name not in self.all_dimension_names:
                    self.all_dimension_names.append(dim_name)
                else:
                    # This case should ideally not happen if keyword files are well-designed.
                    # If it does, we might need a prefixing strategy, but for 19 unique dims, it's unlikely.
                    warnings.warn(
                        f"Dimension name '{dim_name}' from construct '{construct_name}' is a duplicate. This might lead to issues in combined scores if not handled."
                    )

            # Load ZCA Transformer for the construct
            zca_transformer: Optional[ZCA] = None
            actual_zca_file: Optional[str] = None
            zca_override = zca_path_overrides.get(construct_name)

            if zca_override:
                path_zca_override = Path(zca_override)
                if path_zca_override.exists() and path_zca_override.is_file():
                    actual_zca_file = str(path_zca_override)
                else:
                    warnings.warn(
                        f"Provided ZCA override file for construct '{construct_name}' ('{zca_override}') not found or is not a file. "
                        "Proceeding without this ZCA override for the construct."
                    )
            else:
                default_zca_path_npz = (
                    self._package_dir
                    / "data"
                    / f"{construct_name.lower()}_presentation_zca.npz"
                )
                default_zca_path_pkl = (
                    self._package_dir
                    / "data"
                    / f"{construct_name.lower()}_presentation_zca.pkl"
                )

                if default_zca_path_npz.exists() and default_zca_path_npz.is_file():
                    actual_zca_file = str(default_zca_path_npz)
                elif default_zca_path_pkl.exists() and default_zca_path_pkl.is_file():
                    actual_zca_file = str(default_zca_path_pkl)

            if actual_zca_file:
                loaded_zca = ZCA()  # Create a new ZCA instance for each construct

                # Temporarily assign to self for _load_zca_transformer_npz to access model attributes if needed
                # This is a bit of a workaround for _load_zca_transformer_npz's original design
                # A better refactor might pass model embedding dim directly to _load_zca_transformer_npz
                original_temp_zca = getattr(
                    self, "zca_transformer_temp_for_loading", None
                )
                self.zca_transformer_temp_for_loading = loaded_zca

                if actual_zca_file.endswith(".pkl"):
                    try:
                        with open(actual_zca_file, "rb") as f:
                            zca_transformer = pickle.load(f)
                        if not isinstance(zca_transformer, ZCA):
                            warnings.warn(
                                f"Loaded object from {actual_zca_file} for construct '{construct_name}' is not a ZCA instance. Using new ZCA."
                            )
                            zca_transformer = None  # Reset if not a ZCA instance
                    except Exception as e:
                        warnings.warn(
                            f"Could not load ZCA transformer for construct '{construct_name}' from pickle '{actual_zca_file}': {e}"
                        )
                        zca_transformer = None
                elif actual_zca_file.endswith(".npz"):
                    try:
                        zca_data = np.load(actual_zca_file)
                        loaded_zca.mean_ = zca_data["mean"]
                        loaded_zca.whiten_ = zca_data["whiten"]
                        if (
                            "dewhiten" in zca_data
                        ):  # dewhiten is optional in original implementation
                            loaded_zca.dewhiten_ = zca_data["dewhiten"]
                        else:  # Reconstruct dewhiten if not present
                            U, S_values, _ = linalg.svd(
                                np.cov(loaded_zca.whiten_.T, rowvar=False)
                            )
                            s_diag_sqrt = np.diag(
                                np.sqrt(S_values.clip(loaded_zca.regularization))
                            )
                            loaded_zca.dewhiten_ = np.dot(np.dot(U, s_diag_sqrt), U.T)

                        # Set the correct number of features based on the ZCA matrix dimensions
                        # The ZCA was trained on dimension scores, not model embeddings
                        loaded_zca.n_features_in_ = loaded_zca.whiten_.shape[0]

                        zca_transformer = loaded_zca
                        print(
                            f"Loaded pre-trained ZCA transformer for construct '{construct_name}' from {actual_zca_file}"
                        )
                    except Exception as e:
                        warnings.warn(
                            f"Could not load ZCA transformer for construct '{construct_name}' from npz '{actual_zca_file}': {e}"
                        )
                        zca_transformer = None
                else:
                    warnings.warn(
                        f"Unknown ZCA file format for construct '{construct_name}': {actual_zca_file}. Please use .pkl or .npz."
                    )
                # Restore or clear the temporary attribute
                if original_temp_zca is not None:
                    self.zca_transformer_temp_for_loading = original_temp_zca
                else:
                    del self.zca_transformer_temp_for_loading

            self.zca_transformers[construct_name] = zca_transformer

    def _encode_texts(
        self,
        texts: List[str],
        normalize: bool = True,
        batch_size: int = 32,
        show_progress: bool = True,
    ) -> np.ndarray:
        """Encodes texts using Hugging Face transformer with batching, chunking and pooling.

        Args:
            texts (List[str]): List of texts to encode.
            normalize (bool): Whether to normalize the final embeddings. Defaults to True.
            batch_size (int): Number of texts to process in each batch. Defaults to 32.
            show_progress (bool): Whether to show progress bar. Defaults to True.

        Returns:
            np.ndarray: Array of text embeddings with shape (len(texts), hidden_size).
        """
        if not texts:
            return np.array([])

        all_embeddings = []

        with torch.no_grad():
            # Process texts in batches
            for batch_start in tqdm(
                range(0, len(texts), batch_size),
                desc="Encoding text batches",
                disable=not show_progress or len(texts) < 2,
            ):
                batch_end = min(batch_start + batch_size, len(texts))
                batch_texts = texts[batch_start:batch_end]

                # Separate texts that fit vs need chunking
                fit_texts = []
                fit_indices = []
                chunk_texts = []
                chunk_indices = []

                for i, text in enumerate(batch_texts):
                    # Quick tokenization to check length
                    tokens = self.tokenizer(
                        text, truncation=False, add_special_tokens=True
                    )
                    if len(tokens["input_ids"]) <= self.max_length:
                        fit_texts.append(text)
                        fit_indices.append(batch_start + i)
                    else:
                        chunk_texts.append(text)
                        chunk_indices.append(batch_start + i)

                batch_embeddings = [None] * len(batch_texts)

                # Process texts that fit in one go (batch processing)
                if fit_texts:
                    fit_embeddings = self._encode_batch_texts(
                        fit_texts, normalize=False
                    )
                    for emb_idx, orig_idx in enumerate(fit_indices):
                        batch_embeddings[orig_idx - batch_start] = fit_embeddings[
                            emb_idx
                        ]

                # Process texts that need chunking (one by one)
                for i, text in enumerate(chunk_texts):
                    orig_idx = chunk_indices[i]
                    chunk_embedding = self._encode_chunked_text(text, normalize=False)
                    batch_embeddings[orig_idx - batch_start] = chunk_embedding

                all_embeddings.extend(batch_embeddings)

        embeddings_array = np.array(all_embeddings)

        # Normalize if requested
        if normalize:
            norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
            embeddings_array = np.divide(
                embeddings_array,
                norms,
                out=np.zeros_like(embeddings_array),
                where=norms != 0,
            )

        return embeddings_array

    def _encode_batch_texts(
        self, texts: List[str], normalize: bool = True
    ) -> np.ndarray:
        """Encodes a batch of texts that all fit within max_length.

        Args:
            texts (List[str]): List of texts to encode (all must fit in max_length).
            normalize (bool): Whether to normalize embeddings. Defaults to True.

        Returns:
            np.ndarray: Array of text embeddings.
        """
        # Tokenize all texts in the batch
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
            add_special_tokens=True,
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Forward pass
        outputs = self.model(**inputs)

        # Mean pooling for all texts in batch
        embeddings = self._mean_pool(
            outputs.last_hidden_state, inputs["attention_mask"]
        )

        embeddings_np = embeddings.cpu().numpy()

        if normalize:
            norms = np.linalg.norm(embeddings_np, axis=1, keepdims=True)
            embeddings_np = np.divide(
                embeddings_np,
                norms,
                out=np.zeros_like(embeddings_np),
                where=norms != 0,
            )

        return embeddings_np

    def _encode_chunked_text(self, text: str, normalize: bool = True) -> np.ndarray:
        """Encodes a single text that needs chunking.

        Args:
            text (str): Text to encode (longer than max_length).
            normalize (bool): Whether to normalize embedding. Defaults to True.

        Returns:
            np.ndarray: Text embedding.
        """
        # Tokenize the text
        tokens = self.tokenizer(
            text, truncation=False, return_tensors="pt", add_special_tokens=True
        )

        input_ids = tokens["input_ids"].squeeze(0)  # Remove batch dimension
        attention_mask = tokens["attention_mask"].squeeze(0)

        chunk_embeddings = []
        start_idx = 0

        while start_idx < len(input_ids):
            end_idx = min(start_idx + self.max_length, len(input_ids))

            # Extract chunk
            chunk_input_ids = input_ids[start_idx:end_idx]
            chunk_attention_mask = attention_mask[start_idx:end_idx]

            # Process chunk
            inputs = {
                "input_ids": chunk_input_ids.unsqueeze(0).to(self.device),
                "attention_mask": chunk_attention_mask.unsqueeze(0).to(self.device),
            }
            outputs = self.model(**inputs)

            # Mean pooling for this chunk
            chunk_emb = (
                self._mean_pool(outputs.last_hidden_state, inputs["attention_mask"])
                .cpu()
                .numpy()
            )
            chunk_embeddings.append(chunk_emb)

            # Move to next chunk with overlap
            if end_idx >= len(input_ids):
                break
            start_idx = end_idx - self.chunk_overlap

        # Pool chunk embeddings (mean across chunks)
        text_embedding = np.mean(chunk_embeddings, axis=0).squeeze()

        if normalize:
            norm = np.linalg.norm(text_embedding)
            if norm > 0:
                text_embedding = text_embedding / norm

        return text_embedding

    def _mean_pool(
        self, last_hidden_state: torch.Tensor, attention_mask: torch.Tensor
    ) -> torch.Tensor:
        """Performs mean pooling on the last hidden state using attention mask.

        Args:
            last_hidden_state (torch.Tensor): Last hidden state from transformer.
            attention_mask (torch.Tensor): Attention mask.

        Returns:
            torch.Tensor: Mean pooled embedding.
        """
        # Expand attention mask to match hidden state dimensions
        expanded_mask = (
            attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
        )

        # Apply mask and sum
        sum_embeddings = torch.sum(last_hidden_state * expanded_mask, dim=1)

        # Calculate the mean
        sum_mask = torch.clamp(expanded_mask.sum(dim=1), min=1e-9)
        return sum_embeddings / sum_mask

    def _load_local_keywords(self, keywords_file: str) -> Dict[str, List[str]]:
        """Loads keywords from a local JSON file.

        Args:
            keywords_file (str): Path to the keywords JSON file.

        Returns:
            Dict[str, List[str]]: Dictionary of keywords.
        """
        with open(keywords_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def _create_dimension_embeddings_for_construct(
        self, construct_keywords: Dict[str, List[str]]
    ) -> Dict[str, np.ndarray]:
        """Creates representative embedding vectors for each dimension of a given construct.

        Args:
            construct_keywords (Dict[str, List[str]]): Keywords for the specific construct.

        Returns:
            Dict[str, np.ndarray]: Dictionary of dimension embeddings for the construct.
        """
        dimension_embeddings = {}
        for dimension, keywords_list in tqdm(
            construct_keywords.items(),
            desc="Creating dimension embeddings",
            disable=len(construct_keywords) < 2,
        ):
            embeddings = self._encode_texts(
                keywords_list, normalize=False, batch_size=128, show_progress=False
            )
            dimension_embedding = np.mean(embeddings, axis=0)
            dimension_embedding /= np.linalg.norm(dimension_embedding)  # Normalize
            dimension_embeddings[dimension] = dimension_embedding
        return dimension_embeddings

    def _calculate_raw_scores_for_construct(
        self,
        text_embeddings: np.ndarray,
        construct_dim_embeddings: Dict[str, np.ndarray],
    ) -> List[Dict[str, float]]:
        """Calculates raw cosine similarity scores for texts against a construct's dimensions.

        Args:
            text_embeddings (np.ndarray): Normalized embeddings of the input texts.
            construct_dim_embeddings (Dict[str, np.ndarray]): Normalized dimension embeddings for the specific construct.

        Returns:
            List[Dict[str, float]]: List of dictionaries, each with raw scores for the construct's dimensions.
        """
        scores_list = []
        for text_embedding in tqdm(
            text_embeddings,
            desc="Calculating similarity scores",
            disable=len(text_embeddings) < 10,
        ):  # text_embedding is already normalized if done centrally
            score_dict = {}
            for dimension, dim_embedding in construct_dim_embeddings.items():
                # dim_embedding is already normalized during its creation
                cos_similarity = np.dot(text_embedding, dim_embedding)
                score_dict[dimension] = float(cos_similarity)
            scores_list.append(score_dict)
        return scores_list

    def score_texts(
        self,
        texts: List[str],
        zca_transform: str = "pre-trained",
        normalize_text_embeddings: bool = True,
        return_zca_model: bool = False,
        batch_size: int = 32,
    ) -> Union[List[Dict[str, float]], Tuple[List[Dict[str, float]], Dict[str, ZCA]]]:
        """Calculates marketing emphasis scores for a list of texts across all constructs.

        Args:
            texts (List[str]): A list of text strings to be scored.
            zca_transform (str): ZCA transformation method. Options:
                - "pre-trained": Apply pre-loaded ZCA transformer if available.
                - "estimate": Estimate ZCA transformation from input data.
                - "none": No ZCA transformation applied.
                Defaults to "pre-trained".
            normalize_text_embeddings (bool): Whether to normalize text embeddings before
                calculating cosine similarity. Defaults to True.
            return_zca_model (bool): If True and zca_transform is "estimate", returns
                the fitted ZCA transformers along with scores. Defaults to False.
            batch_size (int): Number of texts to process in each batch for encoding.
                Defaults to 32.

        Returns:
            Union[List[Dict[str, float]], Tuple[List[Dict[str, float]], Dict[str, ZCA]]]:
                If return_zca_model is False: A list of dictionaries containing all
                dimension scores for each text.
                If return_zca_model is True and zca_transform is "estimate": A tuple
                containing (scores, zca_models_dict) where zca_models_dict maps
                construct names to fitted ZCA transformers.

        Raises:
            ValueError: If zca_transform is not one of the valid options.
        """
        if zca_transform not in ["pre-trained", "estimate", "none"]:
            raise ValueError(
                f"zca_transform must be one of ['pre-trained', 'estimate', 'none'], got '{zca_transform}'"
            )

        if not texts:
            if return_zca_model and zca_transform == "estimate":
                return [], {}
            return []

        # Embed all texts once using the new encoding method
        text_embeddings_processed = self._encode_texts(
            texts,
            normalize=normalize_text_embeddings,
            batch_size=batch_size,
            show_progress=True,
        )

        # Initialize a list of empty dictionaries for aggregated results, one for each text
        aggregated_scores_list: List[Dict[str, float]] = [{} for _ in range(len(texts))]

        # Store estimated ZCA models if requested
        estimated_zca_models: Dict[str, ZCA] = {}

        for construct_name in tqdm(
            self.CONSTRUCT_NAMES,
            desc="Processing constructs",
            disable=len(self.CONSTRUCT_NAMES) < 2,
        ):
            construct_dim_embeddings = self.dimension_embeddings_by_construct[
                construct_name
            ]
            construct_keywords = self.keywords_by_construct[construct_name]

            # Calculate raw scores for the current construct
            raw_scores_for_construct_list = self._calculate_raw_scores_for_construct(
                text_embeddings_processed, construct_dim_embeddings
            )

            output_scores_df = pd.DataFrame(raw_scores_for_construct_list)
            score_columns = list(construct_keywords.keys())  # Order matters for ZCA

            # Apply ZCA transformation based on the specified method
            if zca_transform == "pre-trained":
                zca_transformer = self.zca_transformers.get(construct_name)
                if zca_transformer:
                    output_scores_df = self._apply_zca_transformation(
                        output_scores_df, score_columns, zca_transformer, construct_name
                    )
                else:
                    warnings.warn(
                        f"No pre-trained ZCA transformer available for construct '{construct_name}'. Using raw scores."
                    )
            elif zca_transform == "estimate":
                if len(texts) < 2:
                    warnings.warn(
                        f"Cannot estimate ZCA for construct '{construct_name}' with fewer than 2 texts. Using raw scores."
                    )
                else:
                    estimated_zca = self._estimate_zca_from_scores(
                        output_scores_df, score_columns, construct_name
                    )
                    if estimated_zca:
                        estimated_zca_models[construct_name] = estimated_zca
                        output_scores_df = self._apply_zca_transformation(
                            output_scores_df,
                            score_columns,
                            estimated_zca,
                            construct_name,
                        )
            # For zca_transform == "none", no transformation is applied

            # Aggregate scores into the final list
            for i, text_idx in enumerate(
                output_scores_df.index
            ):  # text_idx should correspond to original text index
                for dim_name in score_columns:
                    aggregated_scores_list[text_idx][dim_name] = output_scores_df.loc[
                        text_idx, dim_name
                    ]

        if return_zca_model and zca_transform == "estimate":
            return aggregated_scores_list, estimated_zca_models
        return aggregated_scores_list

    def _apply_zca_transformation(
        self,
        scores_df: pd.DataFrame,
        score_columns: List[str],
        zca_transformer: ZCA,
        construct_name: str,
    ) -> pd.DataFrame:
        """Applies ZCA transformation to scores DataFrame.

        Args:
            scores_df (pd.DataFrame): DataFrame containing the scores.
            score_columns (List[str]): List of score column names.
            zca_transformer (ZCA): The ZCA transformer to apply.
            construct_name (str): Name of the construct for error reporting.

        Returns:
            pd.DataFrame: DataFrame with ZCA-transformed scores.
        """
        if not score_columns:
            warnings.warn(
                f"No score columns for construct '{construct_name}', skipping ZCA."
            )
            return scores_df

        try:
            score_matrix = scores_df[score_columns].values
            # Ensure ZCA is fitted
            if not hasattr(zca_transformer, "mean_") or not hasattr(
                zca_transformer, "whiten_"
            ):
                warnings.warn(
                    f"ZCA for construct '{construct_name}' seems not properly fitted/loaded. Skipping ZCA."
                )
                return scores_df
            elif score_matrix.shape[1] != zca_transformer.n_features_in_:
                warnings.warn(
                    f"Dimension mismatch for ZCA on construct '{construct_name}'. "
                    f"Expected {zca_transformer.n_features_in_} features, got {score_matrix.shape[1]}. Skipping ZCA."
                )
                return scores_df

            transformed_scores = zca_transformer.transform(score_matrix)
            # Create a new DataFrame for transformed scores
            transformed_scores_df = pd.DataFrame(
                transformed_scores,
                columns=score_columns,
                index=scores_df.index,
            )
            scores_df_copy = scores_df.copy()
            scores_df_copy[score_columns] = transformed_scores_df[score_columns]
            return scores_df_copy

        except Exception as e:
            warnings.warn(
                f"Error applying ZCA for construct '{construct_name}': {e}. Using raw scores for this construct."
            )
            return scores_df

    def _estimate_zca_from_scores(
        self,
        scores_df: pd.DataFrame,
        score_columns: List[str],
        construct_name: str,
    ) -> Optional[ZCA]:
        """Estimates ZCA transformation from the provided scores.

        Args:
            scores_df (pd.DataFrame): DataFrame containing the scores.
            score_columns (List[str]): List of score column names.
            construct_name (str): Name of the construct for error reporting.

        Returns:
            Optional[ZCA]: Fitted ZCA transformer or None if estimation failed.
        """
        if not score_columns:
            warnings.warn(
                f"No score columns for construct '{construct_name}', cannot estimate ZCA."
            )
            return None

        try:
            score_matrix = scores_df[score_columns].values
            if score_matrix.shape[0] < 2:
                warnings.warn(
                    f"Need at least 2 samples to estimate ZCA for construct '{construct_name}'."
                )
                return None

            zca_transformer = ZCA()
            zca_transformer.fit(score_matrix)
            print(
                f"Estimated ZCA transformer for construct '{construct_name}' from {score_matrix.shape[0]} samples"
            )
            return zca_transformer

        except Exception as e:
            warnings.warn(
                f"Error estimating ZCA for construct '{construct_name}': {e}."
            )
            return None

    def save_zca_transformer(
        self, zca_transformer: ZCA, file_path: str, format: str = "pkl"
    ) -> None:
        """Saves a ZCA transformer to a file.

        Args:
            zca_transformer (ZCA): The ZCA transformer to save.
            file_path (str): Path where to save the transformer.
            format (str): Format to save in. Options: "pkl", "npz". Defaults to "pkl".

        Raises:
            ValueError: If format is not supported.
            Exception: If saving fails.
        """
        if format not in ["pkl", "npz"]:
            raise ValueError(f"Format must be 'pkl' or 'npz', got '{format}'")

        try:
            if format == "pkl":
                with open(file_path, "wb") as f:
                    pickle.dump(zca_transformer, f)
            elif format == "npz":
                np.savez(
                    file_path,
                    mean=zca_transformer.mean_,
                    whiten=zca_transformer.whiten_,
                    dewhiten=zca_transformer.dewhiten_,
                )
            print(f"ZCA transformer saved to {file_path}")
        except Exception as e:
            raise Exception(f"Failed to save ZCA transformer: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """Gets information about the current model and setup for all constructs.

        Returns:
            Dict[str, Any]: Dictionary containing model and setup information.
        """
        construct_details = {}
        total_keywords_count = 0
        for construct_name in self.CONSTRUCT_NAMES:
            keywords = self.keywords_by_construct.get(construct_name, {})
            num_dims = len(keywords)
            dims = list(keywords.keys())
            kw_count = sum(len(words) for words in keywords.values())
            total_keywords_count += kw_count

            construct_details[construct_name] = {
                "num_dimensions": num_dims,
                "dimension_names": dims,
                "keywords_count": kw_count,
                "has_zca_transformer_loaded": self.zca_transformers.get(construct_name)
                is not None,
                "keywords_source": self.keywords_sources.get(construct_name, "N/A"),
            }

        return {
            "global_model_name": self.model_name,
            "global_model_max_seq_length": self.max_length,
            "global_embedding_dimension": self.model.config.hidden_size,
            "total_managed_dimensions": len(self.all_dimension_names),
            "all_dimension_names_in_order": self.all_dimension_names,
            "total_keywords_across_constructs": total_keywords_count,
            "constructs_info": construct_details,
        }
