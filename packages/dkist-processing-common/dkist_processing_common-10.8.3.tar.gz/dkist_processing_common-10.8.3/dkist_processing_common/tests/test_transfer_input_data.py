import json
import os
from pathlib import Path

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.models.graphql import InputDatasetRecipeRunResponse
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.transfer_input_data import TransferL0Data
from dkist_processing_common.tests.conftest import create_parameter_files
from dkist_processing_common.tests.conftest import FakeGQLClient


class TransferL0DataTask(TransferL0Data):
    def run(self) -> None:
        ...


class FakeGQLClientMissingInputDatasetPart(FakeGQLClient):
    """Same metadata mocker with calibration input dataset part missing."""

    def execute_gql_query(self, **kwargs):
        original_response = super().execute_gql_query(**kwargs)
        # Remove calibration frames part if getting InputDatasetRecipeRunResponse:
        if kwargs.get("query_response_cls") == InputDatasetRecipeRunResponse:
            del original_response[0].recipeInstance.inputDataset.inputDatasetInputDatasetParts[2]
        return original_response


def _transfer_l0_data_task_with_client(recipe_run_id, tmp_path, mocker, client_cls):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient",
        new=client_cls,
    )
    with TransferL0DataTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        yield task
        task._purge()


@pytest.fixture
def transfer_l0_data_task(recipe_run_id, tmp_path, mocker):
    yield from _transfer_l0_data_task_with_client(recipe_run_id, tmp_path, mocker, FakeGQLClient)


@pytest.fixture
def transfer_l0_data_task_missing_part(recipe_run_id, tmp_path, mocker):
    yield from _transfer_l0_data_task_with_client(
        recipe_run_id, tmp_path, mocker, FakeGQLClientMissingInputDatasetPart
    )


def test_download_dataset(transfer_l0_data_task):
    """
    :Given: a TransferL0Data task with a valid input dataset
    :When: downloading the dataset documents from the metadata store
    :Then: the correct documents are written to disk
    """
    # Given
    task = transfer_l0_data_task
    # When
    task.download_input_dataset()
    # Then
    expected_observe_doc = FakeGQLClient.observe_frames_doc_object
    observe_doc_from_file = next(
        task.read(tags=Tag.input_dataset_observe_frames(), decoder=json_decoder)
    )
    assert observe_doc_from_file == expected_observe_doc
    expected_calibration_doc = FakeGQLClient.calibration_frames_doc_object
    calibration_doc_from_file = next(
        task.read(tags=Tag.input_dataset_calibration_frames(), decoder=json_decoder)
    )
    assert calibration_doc_from_file == expected_calibration_doc
    expected_parameters_doc = FakeGQLClient.parameters_doc_object
    parameters_doc_from_file = next(
        task.read(tags=Tag.input_dataset_parameters(), decoder=json_decoder)
    )
    assert parameters_doc_from_file == expected_parameters_doc


def test_download_dataset_missing_part(transfer_l0_data_task_missing_part):
    """
    :Given: a TransferL0Data task with a valid input dataset without calibration frames
    :When: downloading the dataset documents from the metadata store
    :Then: the correct number of documents are written to disk
    """
    # Given
    task = transfer_l0_data_task_missing_part
    # When
    task.download_input_dataset()
    # Then
    observe_doc_from_file = next(
        task.read(tags=Tag.input_dataset_observe_frames(), decoder=json_decoder)
    )
    parameters_doc_from_file = next(
        task.read(tags=Tag.input_dataset_parameters(), decoder=json_decoder)
    )
    with pytest.raises(StopIteration):
        calibration_doc_from_file = next(
            task.read(tags=Tag.input_dataset_calibration_frames(), decoder=json_decoder)
        )


def test_format_frame_transfer_items(transfer_l0_data_task):
    """
    :Given: a TransferL0Data task with a downloaded input dataset
    :When: formatting frames in the input dataset for transfer
    :Then: the items are correctly loaded into GlobusTransferItem objects
    """
    # Given
    task = transfer_l0_data_task
    task.download_input_dataset()
    # When
    transfer_items = task.format_frame_transfer_items()
    # Then
    source_filenames = []
    destination_filenames = []
    all_frames = (
        FakeGQLClient.observe_frames_doc_object + FakeGQLClient.calibration_frames_doc_object
    )
    for frame_set in all_frames:
        for key in frame_set["object_keys"]:
            source_filenames.append(os.path.join("/", frame_set["bucket"], key))
            destination_filenames.append(Path(key).name)
    assert len(transfer_items) == len(source_filenames)
    for item in transfer_items:
        assert item.source_path.as_posix() in source_filenames
        assert item.destination_path.name in destination_filenames
        assert not item.recursive


def test_format_parameter_file_transfer_items(transfer_l0_data_task):
    """
    :Given: a TransferL0Data task with a downloaded input dataset
    :When: formatting parameter files in the input dataset for transfer
    :Then: the items are correctly loaded into GlobusTransferItem objects
    """
    # Given
    task = transfer_l0_data_task
    task.download_input_dataset()
    create_parameter_files(task)
    # When
    transfer_items = task.format_parameter_transfer_items()
    # Then
    source_filenames = []
    destination_filenames = []
    parameters = FakeGQLClient.parameters_doc_object
    for param in parameters:
        for value in param["parameterValues"]:
            if "__file__" in value["parameterValue"]:
                value_dict = json.loads(value["parameterValue"])
                bucket = value_dict["__file__"]["bucket"]
                object_key = value_dict["__file__"]["objectKey"]
                source_filenames.append(os.path.join("/", bucket, object_key))
                destination_filenames.append(Path(object_key).name)
    assert len(transfer_items) == len(source_filenames)
    for transfer_item in transfer_items:
        assert transfer_item.source_path.as_posix() in source_filenames
        assert transfer_item.destination_path.name in destination_filenames
        assert str(transfer_item.destination_path).startswith(str(task.scratch.workflow_base_path))
        assert not transfer_item.recursive
