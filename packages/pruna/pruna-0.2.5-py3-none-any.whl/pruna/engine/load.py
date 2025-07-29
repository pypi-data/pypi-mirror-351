# Copyright 2025 - Pruna AI GmbH. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import inspect
import json
import os
import sys
from copy import deepcopy
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Union

import diffusers
import torch
import transformers
from huggingface_hub import constants, snapshot_download
from tqdm.auto import tqdm as base_tqdm
from transformers import pipeline

from pruna import SmashConfig
from pruna.engine.utils import load_json_config, move_to_device
from pruna.logging.logger import pruna_logger

PICKLED_FILE_NAME = "optimized_model.pt"
SAVE_BEFORE_SMASH_CACHE_DIR = "save_before_smash"
PIPELINE_INFO_FILE_NAME = "pipeline_info.json"


def load_pruna_model(model_path: str, **kwargs) -> tuple[Any, SmashConfig]:
    """
    Load a Pruna model from the given model path.

    Parameters
    ----------
    model_path : str
        The path to the model directory.
    **kwargs : Any
        Additional keyword arguments to pass to the model loading function.

    Returns
    -------
    Any, SmashConfig
        The loaded model and its SmashConfig.
    """
    smash_config = SmashConfig()
    smash_config.load_from_json(model_path)
    # since the model was just loaded from a file, we do not need to prepare saving anymore
    smash_config._prepare_saving = False

    resmash_fn = kwargs.pop("resmash_fn", resmash)

    if len(smash_config.load_fns) == 0:
        raise ValueError("Load function has not been set.")

    # load torch artifacts if they exist
    if LOAD_FUNCTIONS.torch_artifacts.name in smash_config.load_fns:
        load_torch_artifacts(model_path, **kwargs)
        smash_config.load_fns.remove(LOAD_FUNCTIONS.torch_artifacts.name)

    if len(smash_config.load_fns) > 1:
        pruna_logger.error(f"Load functions not used: {smash_config.load_fns[1:]}")

    model = LOAD_FUNCTIONS[smash_config.load_fns[0]](model_path, **kwargs)

    if "device_map" not in kwargs and "device" not in kwargs:
        move_to_device(model, smash_config.device)

    # check if there are any algorithms to reapply
    if any(algorithm is not None for algorithm in smash_config.reapply_after_load.values()):
        model = resmash_fn(model, smash_config)

    return model, smash_config


def load_pruna_model_from_hub(
    repo_id: str,
    revision: Optional[str] = None,
    cache_dir: Union[str, Path, None] = None,
    local_dir: Union[str, Path, None] = None,
    library_name: Optional[str] = None,
    library_version: Optional[str] = None,
    user_agent: Optional[Union[Dict, str]] = None,
    proxies: Optional[Dict] = None,
    etag_timeout: float = constants.DEFAULT_ETAG_TIMEOUT,
    force_download: bool = False,
    token: Optional[Union[bool, str]] = None,
    local_files_only: bool = False,
    allow_patterns: Optional[Union[List[str], str]] = None,
    ignore_patterns: Optional[Union[List[str], str]] = None,
    max_workers: int = 8,
    tqdm_class: Optional[base_tqdm] = None,
    headers: Optional[Dict[str, str]] = None,
    endpoint: Optional[str] = None,
    # Deprecated args
    local_dir_use_symlinks: Union[bool, Literal["auto"]] = "auto",
    resume_download: Optional[bool] = None,
    **kwargs,
) -> tuple[Any, SmashConfig]:
    """
    Load a Pruna model from the Hugging Face Hub.

    Parameters
    ----------
    repo_id : str
        The repository ID of the model.
    revision : str | None, optional
        The revision of the model.
    cache_dir : str | Path | None, optional
        The cache directory.
    local_dir : str | Path | None, optional
        The local directory.
    library_name : str | None, optional
        The library name.
    library_version : str | None, optional
        The library version.
    user_agent : str | Dict | None, optional
        The user agent.
    proxies : Dict | None, optional
        The proxies.
    etag_timeout : float, optional
        The etag timeout.
    force_download : bool, optional
        The force download.
    token : str | bool | None, optional
        The Hugging Face token.
    local_files_only : bool, optional
        The local files only.
    allow_patterns : List[str] | str | None, optional
        The allow patterns.
    ignore_patterns : List[str] | str | None, optional
        The ignore patterns.
    max_workers : int, optional
        The max workers.
    tqdm_class : tqdm | None, optional
        The tqdm class.
    headers : Dict[str, str] | None, optional
        The headers.
    endpoint : str | None, optional
        The endpoint.
    local_dir_use_symlinks : bool | Literal["auto"], optional
        The local dir use symlinks.
    resume_download : bool | None, optional
        The resume download.
    **kwargs : Any
        Additional keyword arguments to pass to the model loading function of Pruna.

    Returns
    -------
    tuple[Any, SmashConfig]
        The loaded model and its SmashConfig.
    """
    path = snapshot_download(
        repo_id=repo_id,
        repo_type="model",
        token=token,
        revision=revision,
        cache_dir=cache_dir,
        local_dir=local_dir,
        library_name=library_name,
        library_version=library_version,
        user_agent=user_agent,
        proxies=proxies,
        etag_timeout=etag_timeout,
        force_download=force_download,
        local_files_only=local_files_only,
        allow_patterns=allow_patterns,
        ignore_patterns=ignore_patterns,
        max_workers=max_workers,
        tqdm_class=tqdm_class,
        headers=headers,
        endpoint=endpoint,
        local_dir_use_symlinks=local_dir_use_symlinks,
        resume_download=resume_download,
    )
    return load_pruna_model(model_path=path, **kwargs)


def resmash(model: Any, smash_config: SmashConfig) -> Any:
    """
    Resmash a model after loading it.

    Parameters
    ----------
    model : Any
        The model to resmash.
    smash_config : SmashConfig
        The SmashConfig object containing the reapply_after_load algorithms.

    Returns
    -------
    Any
        The resmashed model.
    """
    # determine algorithms to reapply
    smash_config_subset = deepcopy(smash_config)
    for algorithm_group, algorithm in smash_config.reapply_after_load.items():
        # hyperparameters for algorithms were copied or discarded upon setting to None
        smash_config_subset[algorithm_group] = algorithm

    # if it isnt already imported, import smash
    if "pruna.smash" not in sys.modules:
        from pruna.smash import smash
    else:
        smash = sys.modules["pruna.smash"].smash

    return smash(model=model, smash_config=smash_config_subset)


def load_transformers_model(path: str, **kwargs) -> Any:
    """
    Load a transformers model or pipeline from the given model path.

    Parameters
    ----------
    path : str
        The path to the model directory.
    **kwargs : Any
        Additional keyword arguments to pass to the model loading function.

    Returns
    -------
    AutoModel | pipeline
        The loaded model or pipeline.
    """
    if "torch_dtype" not in kwargs:
        # unless specified by the user, load the model in the same dtype as the base model
        kwargs["torch_dtype"] = "auto"

    if os.path.exists(os.path.join(path, PIPELINE_INFO_FILE_NAME)):
        with open(os.path.join(path, PIPELINE_INFO_FILE_NAME), "r") as f:
            pipeline_info = json.load(f)
        # transformers discards kwargs automatically, no need for filtering
        return pipeline(pipeline_info["task"], path, **kwargs)
    else:
        with open(os.path.join(path, "config.json"), "r") as f:
            config = json.load(f)
        architecture = config["architectures"][0]
        cls = getattr(transformers, architecture)
        # transformers discards kwargs automatically, no need for filtering
        return cls.from_pretrained(path, **kwargs)


def load_diffusers_model(path: str, **kwargs) -> Any:
    """
    Load a diffusers model from the given model path.

    Parameters
    ----------
    path : str
        The path to the model directory.
    **kwargs : Any
        Additional keyword arguments to pass to the model loading function.

    Returns
    -------
    Any
        The loaded diffusers model.
    """
    if os.path.exists(os.path.join(path, "model_index.json")):
        # if it is a diffusers pipeline, it saves the model_index.json file
        model_index = load_json_config(path, "model_index.json")
    else:
        # individual components like the unet or the vae are saved with a config.json file
        model_index = load_json_config(path, "config.json")

    # make loading of model backward compatible with older versions
    # in newer versions the dtype is always saved in the model_config.json file
    dtype_info = load_json_config(path, "dtype_info.json")
    try:
        dtype = dtype_info["dtype"]
        dtype = getattr(torch, dtype)
    except KeyError:
        dtype = torch.float32

    # do not override user specified dtype
    if "torch_dtype" not in kwargs:
        kwargs["torch_dtype"] = dtype

    cls = getattr(diffusers, model_index["_class_name"])
    # transformers discards kwargs automatically, no need for filtering
    return cls.from_pretrained(path, **kwargs)


def load_pickled(path: str, **kwargs) -> Any:
    """
    Load a pickled model from the given model path.

    Parameters
    ----------
    path : str
        The path to the model directory.
    **kwargs : Any
        Additional keyword arguments to pass to the model loading function.

    Returns
    -------
    Any
        The loaded pickled model.
    """
    return torch.load(
        os.path.join(path, PICKLED_FILE_NAME), weights_only=False, **filter_load_kwargs(torch.load, kwargs)
    )


def load_hqq(model_path: str, **kwargs) -> Any:
    """
    Load a model quantized with HQQ from the given model path.

    Parameters
    ----------
    model_path : str
        The path to the model directory.
    **kwargs : Any
        Additional keyword arguments to pass to the model loading function.

    Returns
    -------
    Any
        The loaded model.
    """
    try:
        from hqq.engine.hf import HQQModelForCausalLM
        from hqq.models.hf.base import AutoHQQHFModel
    except ImportError:
        pruna_logger.error(
            "HQQ is not installed. Please install the full version of pruna with `pip install pruna[full] "
            " --extra-index-url https://prunaai.pythonanywhere.com/`."
        )
        raise

    try:  # Try to use pipeline for HF specific HQQ quantization
        model = HQQModelForCausalLM.from_quantized(
            model_path, **filter_load_kwargs(HQQModelForCausalLM.from_quantized, kwargs)
        )
    except Exception as e:  # Default to generic HQQ pipeline if it fails
        pruna_logger.error(f"Error loading model using HQQ: {e}")
        model = AutoHQQHFModel.from_quantized(model_path, **filter_load_kwargs(AutoHQQHFModel.from_quantized, kwargs))

    return model


def load_torch_artifacts(model_path: str, **kwargs) -> None:
    """
    Load a torch artifacts from the given model path.

    Parameters
    ----------
    model_path : str
        The path to the model directory.
    **kwargs : Any
        Additional keyword arguments to pass to the model loading function.
    """
    with open(os.path.join(model_path, "artifact_bytes.bin"), "rb") as f:
        artifact_bytes = f.read()

    torch.compiler.load_cache_artifacts(artifact_bytes)


def load_hqq_diffusers(path: str, **kwargs) -> Any:
    """
    Load a diffusers model from the given model path.

    Parameters
    ----------
    path : str
        The path to the model directory.
    **kwargs : Any
        Additional keyword arguments to pass to the model loading function.

    Returns
    -------
    Any
        The loaded diffusers model.
    """
    from pruna.algorithms.quantization.hqq_diffusers import (
        HQQDiffusersQuantizer,
        construct_base_class,
    )

    hf_quantizer = HQQDiffusersQuantizer()
    auto_hqq_hf_diffusers_model = construct_base_class(hf_quantizer.import_algorithm_packages())

    # If a pipeline was saved, load the backbone and the rest of the pipeline separately
    if os.path.exists(os.path.join(path, "backbone_quantized")):
        # load the backbone
        loaded_backbone = auto_hqq_hf_diffusers_model.from_quantized(
            os.path.join(path, "backbone_quantized"),
            **filter_load_kwargs(auto_hqq_hf_diffusers_model.from_quantized, kwargs),
        )
        # Get the pipeline class name
        model_index = load_json_config(path, "model_index.json")
        cls = getattr(diffusers, model_index["_class_name"])
        # If the pipeline has a transformer, load the transformer
        if "transformer" in model_index:
            model = cls.from_pretrained(path, transformer=loaded_backbone, **kwargs)
        # If the pipeline has a unet, load the unet
        elif "unet" in model_index:
            model = cls.from_pretrained(path, unet=loaded_backbone, **kwargs)
            # If the unet has up_blocks, we need to change the upsampler name to conv
            for layer in model.unet.up_blocks:
                if layer.upsamplers is not None:
                    layer.upsamplers[0].name = "conv"
    else:
        # load the whole model if a pipeline wasn't saved
        model = auto_hqq_hf_diffusers_model.from_quantized(path, **kwargs)
    return model


class LOAD_FUNCTIONS(Enum):  # noqa: N801
    """
    Enumeration of load functions for different model types.

    This enum provides callable functions for loading different types of models,
    including transformers, diffusers, pickled models, IPEX LLM models, and HQQ models.

    Parameters
    ----------
    value : callable
        The load function to be called.
    names : str
        The name of the enum member.
    module : str
        The module where the enum is defined.
    qualname : str
        The qualified name of the enum.
    type : type
        The type of the enum.
    start : int
        The start index for auto-numbering enum values.

    Examples
    --------
    >>> LOAD_FUNCTIONS.transformers(model_path, smash_config)
    <Loaded transformer model>
    """

    transformers = partial(load_transformers_model)
    diffusers = partial(load_diffusers_model)
    pickled = partial(load_pickled)
    hqq = partial(load_hqq)
    hqq_diffusers = partial(load_hqq_diffusers)
    torch_artifacts = partial(load_torch_artifacts)

    def __call__(self, *args, **kwargs) -> Any:
        """
        Call the load function.

        Parameters
        ----------
        args : Any
            The arguments to pass to the load function.
        kwargs : Any
            The keyword arguments to pass to the load function.

        Returns
        -------
        Any
            The result of the load function.
        """
        if self.value is not None:
            return self.value(*args, **kwargs)
        return None


def filter_load_kwargs(func: Callable, kwargs: dict) -> dict:
    """
    Filter out keyword arguments that cannot be passed to the given function.

    Parameters
    ----------
    func : Callable
        The function to check the keyword arguments for.
    kwargs : dict
        The keyword arguments to filter.

    Returns
    -------
    dict
        The filtered keyword arguments.
    """
    # Get the function's signature
    signature = inspect.signature(func)
    valid_params = set(signature.parameters.keys())

    # Filter valid and invalid kwargs
    valid_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}
    invalid_kwargs = {k: v for k, v in kwargs.items() if k not in valid_params}

    # Log the discarded kwargs
    if invalid_kwargs:
        pruna_logger.info(f"Discarded unused loading kwargs: {list(invalid_kwargs.keys())}")

    return valid_kwargs
