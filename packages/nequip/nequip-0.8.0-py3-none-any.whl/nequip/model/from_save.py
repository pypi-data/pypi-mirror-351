# This file is a part of the `nequip` package. Please see LICENSE and README at the root for information on using it.
"""
The functions in this script handle loading from saved formats, i.e. checkpoint files and package files (`.nequip.zip` files).
There are three main types of clients for these functions
1. users can interact with them through the config to load models
2. Python inference codes (e.g. ASE Calculator)
3. internal workflows, i.e. `nequip-package` and `nequip-compile`
"""

import torch

from .utils import (
    override_model_compile_mode,
    get_current_compile_mode,
    _COMPILE_MODE_OPTIONS,
    _EAGER_MODEL_KEY,
)
from nequip.scripts._workflow_utils import get_workflow_state
from nequip.utils import get_current_code_versions
from nequip.utils.logger import RankedLogger

import yaml
import hydra
import os
import warnings
from typing import List, Dict, Any

# === setup logging ===
logger = RankedLogger(__name__, rank_zero_only=True)


def _check_compile_mode(compile_mode: str, client: str, exclude_keys: List[str] = []):
    # helper function for checking input arguments
    allowed_options = [
        mode for mode in _COMPILE_MODE_OPTIONS if mode not in exclude_keys
    ]
    assert (
        compile_mode in allowed_options
    ), f"`compile_mode={compile_mode}` is not recognized for `{client}`, only the following are supported: {allowed_options}"


def _check_file_exists(file_path: str, file_type: str):
    if not os.path.isfile(file_path):
        assert file_type in ("checkpoint", "package")
        client = (
            "`ModelFromCheckpoint`"
            if file_type == "checkpoint"
            else "`ModelFromPackage`"
        )
        raise RuntimeError(
            f"{file_type} file provided at `{file_path}` is not found. NOTE: Any process that loads a checkpoint produced from training runs based on {client} will look for the original {file_type} file at the location specified during training. It is also recommended to use full paths (instead or relative paths) to avoid potential errors."
        )


def ModelFromCheckpoint(checkpoint_path: str, compile_mode: str = _EAGER_MODEL_KEY):
    """Builds model from a NequIP framework checkpoint file.

    This function can be used in the config file as follows.
    ::

      model:
        _target_: nequip.model.ModelFromCheckpoint
        checkpoint_path: path/to/ckpt
        compile_mode: eager/compile

    .. warning::
        DO NOT CHANGE the directory structure or location of the checkpoint file if this model loader is used for training. Any process that loads a checkpoint produced from training runs originating from a package file will look for the original package file at the location specified during training. It is also recommended to use full paths (instead or relative paths) to avoid potential errors.

    Args:
        checkpoint_path (str): path to a ``nequip`` framework checkpoint file
        compile_mode (str): ``eager`` or ``compile`` allowed for training
    """
    # === sanity checks ===
    _check_file_exists(file_path=checkpoint_path, file_type="checkpoint")
    _check_compile_mode(compile_mode, "ModelFromCheckpoint")
    logger.info(f"Loading model from checkpoint file: {checkpoint_path} ...")

    # === load checkpoint and extract info ===
    checkpoint = torch.load(
        checkpoint_path,
        map_location="cpu",
        weights_only=False,
    )

    # === versions ===
    ckpt_versions = checkpoint["hyper_parameters"]["info_dict"]["versions"]
    session_versions = get_current_code_versions(verbose=False)

    for code, session_version in session_versions.items():
        if code in ckpt_versions:
            ckpt_version = ckpt_versions[code]
            # sanity check that versions for current build matches versions from ckpt
            if ckpt_version != session_version:
                warnings.warn(
                    f"`{code}` versions differ between the checkpoint file ({ckpt_version}) and the current run ({session_version}) -- `ModelFromCheckpoint` will be built with the current run's versions, but please check that this decision is as intended."
                )

    # === load model via lightning module ===
    training_module = hydra.utils.get_class(
        checkpoint["hyper_parameters"]["info_dict"]["training_module"]["_target_"]
    )
    # ensure that model is built with correct `compile_mode`
    with override_model_compile_mode(compile_mode):
        lightning_module = training_module.load_from_checkpoint(checkpoint_path)

    model = lightning_module.evaluation_model
    return model


# most of the complexity for `ModelFromPackage` is due to the need to keep track of the `Importer` if we ever repackage
# see `nequip/scripts/package.py` to get the full picture of how they interact
# we expect the following variable to only be used during `nequip-package`

_PACKAGE_TIME_SHARED_IMPORTER = None


def _get_shared_importer():
    global _PACKAGE_TIME_SHARED_IMPORTER
    return _PACKAGE_TIME_SHARED_IMPORTER


def _get_package_metadata(imp):
    """Load packaged model metadata."""
    pkg_metadata: Dict[str, Any] = yaml.safe_load(
        imp.load_text(package="model", resource="package_metadata.txt")
    )
    assert int(pkg_metadata["package_version_id"]) > 0
    # ^ extra sanity check since saving metadata in txt files was implemented in packaging version 1

    return pkg_metadata


def ModelFromPackage(package_path: str, compile_mode: str = _EAGER_MODEL_KEY):
    """Builds model from a NequIP framework packaged zip file constructed with ``nequip-package``.

    This function can be used in the config file as follows.
    ::

      model:
        _target_: nequip.model.ModelFromPackage
        checkpoint_path: path/to/pkg
        compile_mode: eager/compile

    .. warning::
        DO NOT CHANGE the directory structure or location of the package file if this model loader is used for training. Any process that loads a checkpoint produced from training runs originating from a package file will look for the original package file at the location specified during training. It is also recommended to use full paths (instead or relative paths) to avoid potential errors.

    Args:
        package_path (str): path to NequIP framework packaged model with the ``.nequip.zip`` extension (an error will be thrown if the file has a different extension)
        compile_mode (str): ``eager`` or ``compile`` allowed for training
    """
    # === sanity checks ===
    _check_file_exists(file_path=package_path, file_type="package")
    assert str(package_path).endswith(
        ".nequip.zip"
    ), f"NequIP framework packaged files must have the `.nequip.zip` extension but found {str(package_path)}"

    # === account for checkpoint loading ===
    # if `ModelFromPackage` is used by itself, `override=False` and the input `compile_mode` argument is used
    # if this function is called at the end of checkpoint loading via `ModelFromCheckpoint`, `override=True` and the overriden `compile_mode` takes precedence
    cm, override = get_current_compile_mode(return_override=True)
    compile_mode = cm if override else compile_mode

    # === sanity check compile modes ===
    workflow_state = get_workflow_state()
    _check_compile_mode(compile_mode, "ModelFromPackage")

    # === load model ===
    logger.info(f"Loading model from package file: {package_path} ...")
    with warnings.catch_warnings():
        # suppress torch.package TypedStorage warning
        warnings.filterwarnings(
            "ignore",
            message="TypedStorage is deprecated.*",
            category=UserWarning,
            module="torch.package.package_importer",
        )

        # during `nequip-package`, we need to use the same importer for all the models for successful repackaging
        # see https://pytorch.org/docs/stable/package.html#re-export-an-imported-object
        if workflow_state == "package":
            global _PACKAGE_TIME_SHARED_IMPORTER
            imp = _PACKAGE_TIME_SHARED_IMPORTER
            # we load the importer from `package_path` for the first time
            if imp is None:
                imp = torch.package.PackageImporter(package_path)
                _PACKAGE_TIME_SHARED_IMPORTER = imp
            # if it's not `None`, it means we've previously loaded a model during `nequip-package` and should keep using the same importer
        else:
            # if not doing `nequip-package`, we just load a new importer every time `ModelFromPackage` is called
            imp = torch.package.PackageImporter(package_path)

        # do sanity checking with available models
        pkg_metadata = _get_package_metadata(imp)
        available_models = pkg_metadata["available_models"]
        # throw warning if desired `compile_mode` is not available, and default to eager
        if compile_mode not in available_models:
            warnings.warn(
                f"Requested `{compile_mode}` model is not present in the package file ({package_path}). `nequip-{workflow_state}` task will default to using the `{_EAGER_MODEL_KEY}` model."
            )
            compile_mode = _EAGER_MODEL_KEY

        model = imp.load_pickle(
            package="model",
            resource=f"{compile_mode}_model.pkl",
            map_location="cpu",
        )

    # NOTE: model returned is not a GraphModel object tied to the `nequip` in current Python env, but a GraphModel object from the packaged zip file
    return model
