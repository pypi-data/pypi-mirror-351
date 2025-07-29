from contextlib import contextmanager
from io import BytesIO
from typing import (
    Iterator, Callable, List, Any, Union, Tuple, Dict, Optional, BinaryIO
)
from pathlib import Path
from tarfile import TarFile
from zipfile import ZipFile

import json
import os
import tempfile

from ._exceptions import (
    ByomlValidationError,
)


# type aliases for documentation purpose
PathLike = Union[str, os.PathLike]
PytorchModel = Any
TensorflowModel = Any
XgboostModel = Any
SklearnModel = Any
ByomlModel = Union[PytorchModel, TensorflowModel, XgboostModel, SklearnModel]
ModelSerializer = Callable[[PathLike, ByomlModel], PathLike]


def assert_dir_exists(dir_name: PathLike):
    """Raise error if the input directory does not exist."""
    if not os.path.exists(str(dir_name)):
        raise ByomlValidationError(f"The directory '{dir_name}' does not exist.")


def _serialize_torch(work_dir: PathLike, trained_model: PytorchModel) -> PathLike:
    """Serialize a pytorch model to a `model.pt` file."""
    # assuming a TorchScript model
    import torch  # pylint: disable=import-error

    model_file = f'{work_dir}/model.pt'
    model_script = torch.jit.script(trained_model)
    model_script.save(model_file)
    return model_file


def _serialize_joblib(work_dir: PathLike, trained_model: SklearnModel) -> PathLike:
    """Serialize a sklearn model to a `model.joblib` file."""
    import joblib  # pylint: disable=import-error

    model_file = f'{work_dir}/model.joblib'
    joblib.dump(trained_model, model_file)
    return model_file


def _serialize_dill(work_dir: PathLike, trained_model: Any) -> PathLike:
    """Serialize a custom model to a `model.dill` file."""
    import dill  # pylint: disable=import-error

    model_path = f'{work_dir}/model.dill'
    with open(model_path, 'wb') as model_file:
        dill.settings['recurse'] = True
        dill.dump(trained_model, model_file)
    return model_path


def _serialize_tf(work_dir: PathLike, trained_model: TensorflowModel) -> PathLike:
    """Serialize a tensorflow model to a model folder."""
    import tensorflow as tf  # pylint: disable=import-error

    tf.saved_model.save(trained_model, work_dir)
    return work_dir


def _serialize_bst(work_dir: PathLike, trained_model: XgboostModel) -> PathLike:
    """Serialize a xgboost model to a `model.bst` file."""
    if hasattr(trained_model, 'save_model'):
        model_file = f'{work_dir}/model.bst'
        trained_model.save_model(model_file)
        return model_file
    raise ByomlValidationError('Could not serialise this model: missing `save_model` method.')


SUPPORTED_FRAMEWORKS: Dict[str, ModelSerializer] = {
    "pytorch": _serialize_torch,
    "sklearn": _serialize_joblib,
    "tensorflow": _serialize_tf,
    "xgboost": _serialize_bst,
    "custom": _serialize_dill,
}


class ModelArchiveBuilder:
    """A context to build model archives."""

    work_dir_path: Path

    def __init__(self, work_dir: Optional[PathLike]):
        """Create a model archive build context."""
        self.work_dir = work_dir
        self.temp_dir = None

    def __enter__(self):
        """Enter the model archive build context."""
        if self.work_dir:
            self.work_dir_path = Path(self.work_dir)
        else:
            self.temp_dir = tempfile.TemporaryDirectory()
            self.work_dir_path = Path(self.temp_dir.__enter__())
        return self

    def __exit__(self, typ, value, traceback):
        """Exit the model archive build context."""
        if self.temp_dir:
            self.temp_dir.__exit__(typ, value, traceback)

    def serialize_model(
        self, trained_model: ByomlModel, framework: str
    ) -> PathLike:
        """Serialize a model to a given path."""
        framework_function = SUPPORTED_FRAMEWORKS.get(framework, None)
        if framework_function is not None:
            return framework_function(str(self.work_dir_path), trained_model)

        raise ByomlValidationError(
            f'Passing a model instance is not supported for this `{framework}` model, '
            'please provide the path to the saved model instead.'
        )


class ModelZipArchiveBuilder(ModelArchiveBuilder):
    """A context to build a zip model archives (legacy byoml api)."""

    def _get_files_to_zip(self, file_or_dir: PathLike) -> List[Tuple[str, str]]:
        """Get the filenames to zip and the name it should have in the zipfile."""
        file_or_dir = str(file_or_dir)
        if not os.path.isdir(file_or_dir):
            # single file
            zip_file_name = os.path.basename(file_or_dir)
            return [(file_or_dir, zip_file_name)]

        file_names: List[Tuple[str, str]] = []
        for root, _, files in os.walk(file_or_dir):
            for file_name in files:
                # the root will always contain the same suffix, which should not end up in the zip
                zip_root = root[len(file_or_dir):]
                zip_file_name = os.path.join(zip_root, file_name)

                file_path = os.path.join(root, file_name)

                file_names.append((file_path, zip_file_name))

        return file_names

    @contextmanager
    def save_model_in_dir(
        self, trained_model: Union[PathLike, ByomlModel], framework: str
    ):
        """Create the model zip file in a temporary buffer."""
        if not isinstance(trained_model, (str, os.PathLike)):
            file_name = self.serialize_model(trained_model, framework)
            files = self._get_files_to_zip(file_name)
        else:
            files = self._get_files_to_zip(trained_model)

        model_zip_buffer = BytesIO()
        with ZipFile(model_zip_buffer, 'w') as zipper:
            for file_name, zip_file_name in files:
                zipper.write(file_name, zip_file_name)

        yield model_zip_buffer
        model_zip_buffer.close()


class ModelPlugArchiveBuilder(ModelArchiveBuilder):
    """A context to build a model plug archive (openfaas)."""

    model_spec_path: Path
    model_path: Path
    requirements_path: Path
    lib_path: Path

    def add_model_spec(
        self,
        model_spec: Dict
    ):
        """Add a model specification."""
        model_spec_path = self.work_dir_path / 'model.json'
        with open(model_spec_path, 'wt') as model_spec_file:
            json.dump(model_spec, model_spec_file)
        self.model_spec_path = model_spec_path

    def add_model(
        self, trained_model: Union[PathLike, ByomlModel], framework: str
    ):
        """Add a serialized model file."""
        if isinstance(trained_model, (str, os.PathLike)):
            self.model_path = Path(trained_model)
        else:
            self.model_path = Path(
                self.serialize_model(trained_model, framework)
            )

    def add_requirements(
        self,
        requirements_file: Optional[PathLike],
        requirements: Optional[str]
    ):
        """Add requirements file."""
        if requirements_file:
            if requirements:
                raise AttributeError(
                    "cannot specify both 'requirements' and 'requirements_file'"
                )
            self.requirements_path = Path(requirements_file)
        else:
            with open(self.work_dir_path / 'requirements.txt', 'wt') as f:
                f.write(requirements or '')
            self.requirements_path = self.work_dir_path / 'requirements.txt'

    def add_lib(self, lib: Optional[PathLike]):
        """Add a lib folder."""
        if not lib:
            # create an empty dir
            self.lib_path = self.work_dir_path / 'lib'
            self.lib_path.mkdir()
        else:
            lib_path = Path(lib)
            if not lib_path.is_dir():
                raise AttributeError(
                    f"argument 'lib={lib}' must refer to an existing directory."
                )
            self.lib_path = lib_path

    @contextmanager
    def create_plug_tar_archive(self) -> Iterator[Tuple[BinaryIO, int]]:
        """Create a tar archive buffer."""
        assert self.model_spec_path
        assert self.model_path
        tar_bytes = BytesIO()
        with TarFile.open(fileobj=tar_bytes, mode='w:gz') as tar_file:
            # spec file
            tar_file.add(self.model_spec_path, arcname='model.json')
            # model file or dir
            tar_file.add(self.model_path, arcname='models/' + self.model_path.name)
            tar_file.add(self.requirements_path, arcname='requirements.txt')
            tar_file.add(self.lib_path, arcname='lib')

        tar_size = tar_bytes.tell()
        tar_bytes.seek(0)
        yield tar_bytes, tar_size
        tar_bytes.close()
