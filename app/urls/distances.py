import io
import json
from itertools import combinations
from typing import Optional, List, Literal
import os
import glob
import traceback
import requests

import polars as pl
from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Body, Form
from starlette.responses import Response, JSONResponse

from ..config.constants import OUTPUT_FIGS, OUTPUT_JSONS, DISTANCES, OUTPUT_DISTANCES_URL
from ..config.loggers import get_and_set_logger
from ..models.distances import (
    DistanceInput,
    SingleListInput,
    TwoListsInput,
    CSVDistanceInput,
    StringPair,
    DistanceType,
    ModelConfig
)
from ..services.distances.base import calculate_distances
from ..services.csvs import process_csv_distances

logger = get_and_set_logger(__name__)

distances_router = APIRouter()

@distances_router.post("/calculate-distances/pairs")
async def calculate_distances_pairs(input_data: DistanceInput):
    """Direct endpoint for calculating distances between specified pairs."""
    return await calculate_distances(
        input_data.pairs,
        input_data.distance_type,
        input_data.model_name,
        input_data.use_worker,
        input_data.batch_size
    )

@distances_router.post("/calculate-distances/single-list")
async def calculate_distances_single_list(input_data: SingleListInput):
    """Endpoint for calculating distances between all pairs in a single list."""
    pairs = [
        StringPair(string1=s1, string2=s2)
        for s1, s2 in combinations(input_data.strings, 2)
    ]
    return await calculate_distances(
        pairs,
        input_data.distance_type,
        input_data.model_name,
        input_data.use_worker,
        input_data.batch_size
    )

@distances_router.post("/calculate-distances/two-lists")
async def calculate_distances_two_lists(input_data: TwoListsInput):
    """Endpoint for calculating distances between pairs from two lists."""
    pairs = [
        StringPair(string1=s1, string2=s2)
        for s1, s2 in zip(input_data.list1, input_data.list2)
    ]
    return await calculate_distances(
        pairs,
        input_data.distance_type,
        input_data.model_name,
        input_data.use_worker,
        input_data.batch_size
    )

@distances_router.post("/calculate-distances/two-lists")
async def calculate_distances_two_lists(input_data: TwoListsInput):
    """Endpoint for calculating distances between pairs from two lists."""
    pairs = [
        StringPair(string1=s1, string2=s2)
        for s1, s2 in zip(input_data.list1, input_data.list2)
    ]
    return await calculate_distances(
        pairs,
        input_data.distance_type,
        input_data.model_name,
        input_data.use_worker,
        input_data.batch_size
    )

@distances_router.post("/calculate-distances/from-csv")
async def calculate_distances_from_csv(
        file: UploadFile = File(...),
        config: str = Form(...)  # Receive as raw JSON string
):
    """Calculate distance metrics between concatenated fields from CSV rows."""
    try:
        # Parse the config JSON string
        config_dict = json.loads(config)

        # Convert simple model names to proper ModelConfig objects
        if "embedding_models" in config_dict:
            if isinstance(config_dict["embedding_models"], list):
                # Convert each model specification
                embedding_models = []
                for model in config_dict["embedding_models"]:
                    if isinstance(model, str):
                        # If it's just a string, create full config
                        embedding_models.append({
                            "model_id": model,
                            "distance_prefix": f"{model}_cosine"
                        })
                    elif isinstance(model, dict):
                        # If it's already a dict, ensure it has distance_prefix
                        if "distance_prefix" not in model:
                            model["distance_prefix"] = f"{model['model_id']}_cosine"
                        embedding_models.append(model)
                config_dict["embedding_models"] = embedding_models

        # Create CSVDistanceInput model
        config_model = CSVDistanceInput(**config_dict)

        logger.info(f"Received CSV upload with config: {config_model}")
        content = await file.read()

        try:
            df = pl.read_csv(io.BytesIO(content))
            logger.info(f"Successfully read CSV with shape: {df.shape}")
        except Exception as csv_error:
            logger.error(f"CSV reading error: {str(csv_error)}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to read CSV: {str(csv_error)}"
            )

        # Process distances with the full model configs
        result = await process_csv_distances(df, config_model)

        # Add model information to response
        if config_model.embedding_models:
            result["embedding_models"] = [
                {
                    "model_id": model.model_id,
                    "distance_prefix": model.distance_prefix or f"{model.model_id}_cosine"
                }
                for model in config_model.embedding_models
            ]

        return JSONResponse("ok")

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing config JSON: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid config JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Error in calculate_distances_from_csv: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))