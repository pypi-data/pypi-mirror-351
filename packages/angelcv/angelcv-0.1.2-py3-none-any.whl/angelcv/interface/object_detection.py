from datetime import datetime
import logging
import os
from pathlib import Path
from typing import Any

import lightning as L
from lightning.pytorch.callbacks import (
    DeviceStatsMonitor,
    EarlyStopping,
    LearningRateMonitor,
    ModelCheckpoint,
    RichProgressBar,
)
from lightning.pytorch.loggers import TensorBoardLogger
import numpy as np
import torch
import yaml

from angelcv.config import ConfigManager
from angelcv.dataset.coco_datamodule import CocoDataModule
from angelcv.dataset.yolo_datamodule import YOLODataModule
from angelcv.interface.inference_result import InferenceResult
from angelcv.model.yolo import YoloDetectionModel
from angelcv.utils.path_utils import CHECKPOINT_FILE_EXTENSIONS, resolve_file_path
from angelcv.utils.source_utils import preprocess_sources

# Configure logging
logger = logging.getLogger(__name__)


class ObjectDetectionModel:
    """
    High-level interface for object detection models.

    Provides simplified methods for common tasks like training, inference,
    and exporting.

    Examples:
        ```python
        # Create a new model from a configuration file
        model = ObjectDetectionModel("yolov10n.yaml")

        # Load a pretrained model from a checkpoint
        model = ObjectDetectionModel("yolov10n.ckpt")

        # Train the model using a dataset configuration
        results = model.train(dataset="coco.yaml", epochs=100)

        # Validate the model
        results = model.validation()

        # Perform inference on an image
        results = model("path/to/image.jpg")

        # Export the model to ONNX format
        success = model.export(format="onnx")
        ```
    """

    def __init__(self, model_source: Path | str):
        """
        Initializes the Object Detection Model.

        Args:
            model_source: Path to a model config file or checkpoint file.
                        If .yaml, loads a fresh model configuration - can be in angelcv/config/dataset/ or absolute path
                        If .ckpt or .pt, loads weights from the checkpoint - in project root or absolute path
        """
        # This function will find the actual path of the model file and download it from S3 if it exists
        model_source_abs_path = resolve_file_path(model_source)
        is_checkpoint = model_source_abs_path.suffix in CHECKPOINT_FILE_EXTENSIONS

        if is_checkpoint:
            # NOTE: this is used instead of YoloDetectionModel.load_from_checkpoint(...)
            # because the lightning implementation isn't working with different model files
            self.model: YoloDetectionModel = YoloDetectionModel.load_from_checkpoint_custom(model_source_abs_path)
            ConfigManager.set_config(self.model.config)
        else:
            # Otherwise use model_source as the config file (i.e. .yaml)
            config = ConfigManager.upsert_config(model_file=model_source_abs_path)
            self.model = YoloDetectionModel(config=config)

        logger.info(f"Initialized model: {self.model.__class__.__name__}")

        # Store training results for last run
        self.training_results = None
        self.validation_results = None
        self.test_results = None

    def __call__(self, *args, **kwargs) -> list[InferenceResult]:
        """
        Performs object detection on the provided source.

        Args:
            source: Source for detection: file path, URL, PIL image, torch.Tensor, numpy array, or a list of these.
            confidence_th: Confidence threshold for filtering detections.
            image_size: Size of the longest side of the image to be resized to (defaults to the model's image_size)

        Returns:
            list[InferenceResult]: A list of InferenceResult objects containing detection results.
        """
        return self.predict(*args, **kwargs)

    def predict(
        self,
        source: str | Path | torch.Tensor | np.ndarray | list[str | Path | torch.Tensor | np.ndarray],
        confidence_th: float = 0.3,
        image_size: int | None = None,
    ) -> list[InferenceResult]:
        """
        Performs inference on the given source(s).

        Args:
            source: Source for detection: file path, URL, PIL image, torch.Tensor, numpy array, or a list of these.
            confidence_th: Confidence threshold for filtering detections.
            image_size: Size of the longest side of the image to be resized to (defaults to the model's image_size)

        Returns:
            list[InferenceResult]: A list of InferenceResult objects containing detection results.
        """
        logger.info(f"Running prediction with conf={confidence_th}")

        if image_size is None:
            image_size = self.model.config.image_size

        # Set model to evaluation mode
        self.model.eval()

        # Process input sources
        processed_tensors, orig_imgs_np, source_identifiers, img_coordinate_mappers = preprocess_sources(
            source, image_size=image_size
        )

        # Run model inference
        results: list[InferenceResult] = []
        with torch.no_grad():
            # Batch processing could be implemented here
            for i, processed_tensor in enumerate(processed_tensors):
                # Move to the same device as the model
                processed_tensor = processed_tensor.to(self.model.device)

                # Run model forward pass (unsqueeze to add batch dimension)
                output = self.model(processed_tensor)

                # Postrocess model output (1, 400, 6 --> N, 6), where N is the number of detections above threshold
                output = self._postprocess_detections(output, confidence_th=confidence_th)

                results.append(
                    InferenceResult(
                        model_output=output,
                        original_image=orig_imgs_np[i],
                        img_coordinate_mapper=img_coordinate_mappers[i],
                        class_labels=self.model.config.dataset.names if self.model.config.dataset else None,
                    )
                )

        logger.info(f"Prediction finished. Found {sum(r.boxes.xyxy.shape[0] for r in results)} detections.")
        return results

    def _postprocess_detections(self, model_output: torch.Tensor, confidence_th: float = 0.3) -> torch.Tensor:
        """
        Postprocesses model output to extract detections.

        Args:
            model_output: Raw output from the model (shape: B, 400, 6)
                          where B is batch size and each box is [x1, y1, x2, y2, conf, class_id]
            confidence_th: Confidence threshold for filtering

        Returns:
            Filtered detections (shape: N, 6) where N is the number of detections above threshold
        """
        # TODO [LOW]: implement NMS (not required for YOLOv10)

        assert model_output.ndim == 3, "model_output must be a 3D tensor"
        assert model_output.shape[0] == 1, "model_output must have 1 batch dimension"
        assert model_output.shape[2] == 6, "model_output must have 6 columns"

        model_output = model_output.squeeze(0)  # Remove batch dimension: (400, 6)

        # Filter based on confidence threshold
        # Identify the confidence values (5th column, index 4)
        conf_mask = model_output[..., 4] >= confidence_th

        # Apply mask to get filtered detections
        filt_model_output = model_output[conf_mask]

        return filt_model_output

    def train(
        self,
        dataset: str | Path,
        image_size: int = None,
        batch_size: int = None,
        num_workers: int = None,
        patience: int = 0,
        **kwargs,  # everything available in Lightning Trainer
    ) -> dict[str, Any]:
        """
        Trains the object detection model.

        Args:
            dataset: Path to a YAML file
            image_size: Image size of the model.
            batch_size: Batch size for training.
            num_workers: Number of worker threads for data loading.
            patience: Number of epochs with worse validation loss to wait before stopping training.

            accelerator: Supports passing different accelerator types ("cpu", "gpu", "tpu", "hpu", "mps", "auto")
            devices:The devices to use. Can be set to a positive number (int or str), a sequence of device indices
                (list or str), the value ``-1`` to indicate all available devices should be used, or ``"auto"`` for
                automatic selection based on the chosen accelerator. Default: ``"auto"``.
            precision: Double precision (64, '64' or '64-true'), full precision (32, '32' or '32-true'),
                16bit mixed precision (16, '16', '16-mixed') or bfloat16 mixed precision ('bf16', 'bf16-mixed').
                Can be used on CPU, GPU, TPUs, or HPUs.
                Default: ``'32-true'``.
            max_epochs: Number of training epochs.
            callbacks: Additional callbacks for training.
            **kwargs: Additional keyword arguments passed to the trainer (everything available in Lightning Trainer)

        Returns:
            dict[str, Any]: Dictionary containing training results.
        """
        # Set model to training mode
        self.model.train()

        # TODO [MID]: decide how to handle this (shouldn't be the default, but proposed as an option if required)
        # Disable peer-to-peer (P2P) direct memory access between GPUs
        # NOTE: Some GPUs (specially consumer ones) have issues with P2P (tested with RTX A4000)
        os.environ["NCCL_P2P_DISABLE"] = "1"

        # Find the file and update the configuration
        dataset_path = resolve_file_path(dataset)
        # TODO [MID]: FIX THIS, it shouldn't be required to reassign to self.model.config, probably the issue comes
        # from the ConfigManager.set_config(...)
        self.model.config = ConfigManager.upsert_config(dataset_file=str(dataset_path))

        # Get the class names from the dataset config
        new_num_classes = len(self.model.config.dataset.names)
        original_num_classes = self.model.blocks[-1].num_classes

        # If the model was loaded from a checkpoint and has a different number of classes
        if new_num_classes != original_num_classes:
            logger.info(f"Updating model from {original_num_classes} to {new_num_classes} classes")
            self.model.update_num_classes(new_num_classes)

        # Update configuration with any provided settings
        # TODO [LOW]: think of a generic way to save the arguments used during training in the config
        if "max_epochs" in kwargs:
            self.model.config.train.max_epochs = kwargs["max_epochs"]
        if patience > 0:
            self.model.config.train.patience = patience
        if image_size is not None:
            self.model.config.image_size = image_size
        if batch_size is not None:
            self.model.config.train.data.batch_size = batch_size
        if num_workers is not None:
            self.model.config.num_workers = num_workers

        # Setup datamodule
        datamodule = self._setup_datamodule(dataset)

        # Setup training callbacks
        experiment_dir = self._setup_experiment_directory()

        train_callbacks = [
            ModelCheckpoint(
                dirpath=experiment_dir / "checkpoints",
                filename="model-{epoch:03d}-{val_loss:.2f}",
                monitor="val_loss",
                save_top_k=3,
                save_last=True,
                auto_insert_metric_name=True,
            ),
            LearningRateMonitor(logging_interval="step"),
            DeviceStatsMonitor(),
            RichProgressBar(),
        ]

        if self.model.config.train.patience > 0:
            train_callbacks.append(EarlyStopping(monitor="val_loss", patience=self.model.config.train.patience))

        # Add custom callbacks if provided
        if "callbacks" in kwargs:
            train_callbacks.extend(kwargs["callbacks"])
        kwargs["callbacks"] = train_callbacks

        # Setup logger
        tb_logger = TensorBoardLogger(save_dir=experiment_dir, name="tb_logs")

        # Create trainer
        trainer_kwargs = {
            "logger": tb_logger,
            "deterministic": False,
            **kwargs,  # All the Trainer arguments, that come from function arguments
        }

        # Save confg to experiment directory
        with open(experiment_dir / "config.yaml", "w") as f:
            yaml.dump(self.model.config.model_dump(), f)

        with open(experiment_dir / "trainer_kwargs.yaml", "w") as f:
            yaml.dump(trainer_kwargs, f)

        trainer = L.Trainer(**trainer_kwargs)
        # TODO [MID]: think how to prune the model after training (make them smaller)

        # --- Train model ---
        logger.info(f"Starting training for {self.model.config.train.max_epochs} epochs")
        trainer.fit(self.model, datamodule=datamodule)

        # --- Store and return results ---
        # Extract metrics from trainer/logger
        self.training_results = {
            "epochs_completed": trainer.current_epoch,
            "global_step": trainer.global_step,
            "experiment_dir": str(experiment_dir),
            "best_model_path": trainer.checkpoint_callback.best_model_path
            if hasattr(trainer, "checkpoint_callback")
            else None,
            "best_model_score": trainer.checkpoint_callback.best_model_score
            if hasattr(trainer, "checkpoint_callback")
            else None,
        }

        logger.info(f"Training completed. Best model: {self.training_results['best_model_path']}")
        return self.training_results

    def _setup_datamodule(self, dataset: str | Path) -> L.LightningDataModule:
        """
        Sets up a data module for training/validation/testing.

        Args:
            dataset: Dataset yaml path (str or Path)

        Returns:
            LightningDataModule: Configured data module
        """
        # Path to a dataset config file
        data_path = Path(dataset)

        if data_path.suffix.lower() == ".yaml":
            # TODO [LOW]: make this more generic, so it can handle any dataset
            # YAML config file
            if "coco" in data_path.stem.lower():
                # COCO dataset
                ConfigManager.upsert_config(dataset_file=str(data_path))
                datamodule = CocoDataModule(self.model.config)
            else:
                # Other YAML formats (YOLO format)
                datamodule = YOLODataModule(self.model.config)

        else:
            raise ValueError(f"Unsupported dataset file format: {data_path.suffix}")

        return datamodule

    def _setup_experiment_directory(self) -> Path:
        """
        Creates and returns a single experiment directory.
        """
        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Create main experiment directory
        experiment_dir = Path("experiments") / timestamp_str
        experiment_dir.mkdir(parents=True, exist_ok=True)

        # Pass it to nested model
        self.model.experiment_dir = experiment_dir

        logger.info(f"Created experiment directory: {experiment_dir}")

        return experiment_dir

    def test(
        self,
        dataset: str | Path | None = None,
        image_size: int | None = None,
        batch_size: int | None = None,
        num_workers: int | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Tests the model using a test dataset.

        Args:
            dataset: Path to YAML file containing dataset configuration with test set.
                    If None and training_results exists, will use the same dataset from training.
            image_size: Image size for testing (overrides config).
            batch_size: Batch size for testing.
            num_workers: Number of worker threads for data loading.
            **kwargs: Additional keyword arguments passed to the trainer (everything available in Lightning Trainer).

        Returns:
            dict[str, Any]: Dictionary containing test metrics.
        """
        # Set model to evaluation mode
        self.model.eval()

        # Use training dataset if no dataset is specified and we have a previous training run
        if dataset is None:
            if self.model.config.dataset is None:
                raise ValueError("No dataset specified for testing and no previous training dataset available")

            logger.info("Using training dataset for testing")
        else:
            dataset_path = resolve_file_path(dataset)
            logger.info(f"Using dataset for testing: {dataset_path}")
            # TODO [MID]: FIX THIS, it shouldn't be required to reassign to self.model.config, probably the issue comes
            # from the ConfigManager.set_config(...)
            self.model.config = ConfigManager.upsert_config(dataset_file=str(dataset_path))

        # Update configuration with any provided settings
        if image_size is not None:
            self.model.config.image_size = image_size
        if batch_size is not None:
            self.model.config.test.data.batch_size = batch_size
        if num_workers is not None:
            self.model.config.num_workers = num_workers

        # Setup datamodule
        datamodule = self._setup_datamodule(dataset)
        datamodule.setup("test")

        # Verify that test dataset exists
        if not hasattr(datamodule, "test_dataset") or datamodule.test_dataset is None:
            raise ValueError("No test dataset available in the provided dataset configuration")

        # Setup test callbacks
        test_callbacks = [RichProgressBar()]

        # Add custom callbacks if provided
        if "callbacks" in kwargs:
            test_callbacks.extend(kwargs["callbacks"])
        kwargs["callbacks"] = test_callbacks

        # Setup logger
        # TODO [MID]: do it in a similar way that it's done in train(...)
        date_str = self._get_date_str()
        tb_logger = TensorBoardLogger(save_dir="tb_logs", name=f"test_{date_str}")

        # Create trainer with appropriate settings for testing
        trainer_kwargs = {
            "logger": tb_logger,
            "enable_checkpointing": False,
            "deterministic": kwargs.pop("deterministic", False),
            **kwargs,  # All the remaining Trainer arguments
        }
        trainer = L.Trainer(**trainer_kwargs)

        # Run test
        logger.info("Starting testing")
        results = trainer.test(self.model, datamodule=datamodule)

        # Store results with more information
        self.test_results = {
            **(results[0] if results and isinstance(results, list) else {}),
            "timestamp": date_str,
            "dataset": str(dataset) if dataset else "default",
            "image_size": self.model.config.image_size,
            "batch_size": batch_size
            if batch_size is not None
            else getattr(
                getattr(self.model.config, "test", None),
                "batch_size",
                getattr(self.model.config.validation.data, "batch_size", None),
            ),
        }

        logger.info(f"Testing completed. mAP: {self.test_results.get('test/map', 'N/A')}")
        return self.test_results

    def export(self, format: str = "onnx", output_path: str | None = None, **kwargs) -> Path | None:
        """
        Exports the model to a specified format.

        Args:
            format: The target format ('onnx', etc.)
            output_path: Path to save the exported model. Defaults to a standard naming pattern.
            **kwargs: Additional format-specific arguments.

        Returns:
            Path: Path to the exported model. None if export failed.
        """
        logger.info(f"Starting export to {format} format")

        # Set model to evaluation mode
        self.model.eval()

        # --- Determine Output Path ---
        if output_path is None:
            output_path = Path(".") / f"{self.model.config.model.name}.{format.lower()}"
            logger.info(f"No output path specified, using default: {output_path}")
        else:
            output_path = Path(output_path)

        # Create export directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Export Logic
        try:
            if format.lower() == "onnx":
                # Get input size from config
                img_size = self.model.config.image_size

                # Create example input
                example_input = torch.randn(1, 3, img_size, img_size).to(self.model.device)

                # Export to ONNX
                opset_version = kwargs.get("opset_version", 11)  # Default to ONNX opset 11
                torch.onnx.export(
                    self.model,
                    example_input,
                    str(output_path),
                    opset_version=opset_version,
                    input_names=["images"],
                    output_names=["output"],
                    **kwargs,
                )
                logger.info(f"Model successfully exported to ONNX: {output_path}")
                return output_path

            elif format.lower() == "saved_model" or format.lower() == "pb":
                logger.warning("TensorFlow SavedModel export requires TensorFlow installation")
                # This would require additional TensorFlow dependencies
                raise NotImplementedError("TensorFlow SavedModel export not yet implemented")

            else:
                logger.error(f"Unsupported export format: {format}")
                return None

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return None

        return None


def test_inference():
    # Load model
    # model = ObjectDetectionModel("yolov10n.yaml") # from yaml (no weights)
    # model = ObjectDetectionModel("checkpoints/2025-05-07_09-49-47/last.ckpt") # from local checkpoint (weights)
    model = ObjectDetectionModel("yolov10s.ckpt")  # from S3 checkpoint (weights)

    # Perform inference
    results_inference = model("angelcv/images/city.jpg", confidence_th=0.2)
    results_inference[0].show()
    # results_inference[0].save(Path("city_pred.jpg"))


def test_train():
    from angelcv.utils.env_utils import is_debug_mode

    model = ObjectDetectionModel("yolov10s.ckpt")  # from S3 checkpoint (weights)

    # Train model
    dataset = "../../defendry-dataset/export-custom-v1/dataset.yaml"  # "coco.yaml"
    # dataset = "coco.yaml"

    if is_debug_mode():
        print("Running in DEBUG mode")
        kwargs = {
            "batch_size": 4,
            "num_workers": 2,
            "patience": -1,
            # "overfit_batches": 256,  # NOTE: 256 first multiple of 2 that val_loss != nan
            "overfit_batches": 0.0,  # entire dataset
            "num_sanity_val_steps": 2,
        }
    else:
        print("Running in PRODUCTION mode")
        kwargs = {
            "batch_size": 8,
            "num_workers": -1,
            "patience": 50,
            "overfit_batches": 0.0,  # entire dataset
            "num_sanity_val_steps": 0,
        }

    results_train = model.train(
        dataset=dataset,
        max_epochs=900,
        **kwargs,
        accelerator="gpu",
        devices=-1,  # Use all available GPUs
        precision="16-mixed",  # Better performance, especially for multi-GPU
        sync_batchnorm=True,  # Important for multi-GPU training
    )
    print(results_train)


def test_testset():
    model = ObjectDetectionModel("yolov10s.ckpt")  # from S3 checkpoint (weights)

    # Test model
    results_test = model.test(dataset="coco.yaml", batch_size=8)
    print(results_test)


if __name__ == "__main__":
    test_inference()
    # test_train()
    # test_testset()
