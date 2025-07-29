# File: python/sdk/luminarycloud/inference/inference.py
# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from __future__ import annotations

from datetime import datetime
from typing import Any
from json import loads as json_loads

from .._client import get_default_client
from .._helpers._timestamp_to_datetime import timestamp_to_datetime
from .._proto.api.v0.luminarycloud.inference import inference_pb2 as inferencepb
from .._proto.inferenceservice import inferenceservice_pb2 as inferenceservicepb
from .._wrapper import ProtoWrapper, ProtoWrapperBase
from .._helpers.warnings import experimental


@experimental
def start_inference_job(
    stl_url: str,
    model_url: str,
    config_name: str,
    stencil_size: int,
) -> dict[str, Any]:
    """Creates an inference service job.
    Parameters
    ----------
    stl_url : str
        URL of the STL file to be used for inference.
    model_url : str
        URL of the model to be used for inference.
    config_name :str
        Name of the configuration to be used for inference.
    stencil_size :int
        Size of the stencil to be used for inference.


    Returns
    dict[str, Any]
        Response from the server as key-value pairs.

    warning:: This feature is experimental and may change or be removed without notice.
    """

    req = inferencepb.CreateInferenceServiceJobRequest(
        stl_url=stl_url,
        model_url=model_url,
        config_name=config_name,
        stencil_size=stencil_size,
    )

    res: inferencepb.CreateInferenceServiceJobResponse = (
        get_default_client().CreateInferenceServiceJob(req)
    )

    return json_loads(str(res.response, encoding="utf-8"))
