# Copyright 2025 - Oumi
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

import copy
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import jsonlines
from tqdm import tqdm

from oumi.core.configs import (
    GenerationParams,
    InferenceConfig,
    ModelParams,
)
from oumi.core.types.conversation import Conversation
from oumi.utils.logging import logger


class BaseInferenceEngine(ABC):
    """Base class for running model inference."""

    _model_params: ModelParams
    """The model parameters."""

    _generation_params: GenerationParams
    """The generation parameters."""

    def __init__(
        self,
        model_params: ModelParams,
        *,
        generation_params: Optional[GenerationParams] = None,
    ):
        """Initializes the inference engine.

        Args:
            model_params: The model parameters.
            generation_params: The generation parameters.
        """
        self._model_params = copy.deepcopy(model_params)
        if generation_params:
            self._check_unsupported_params(generation_params)
        else:
            generation_params = GenerationParams()
        self._generation_params = generation_params

    def infer(
        self,
        input: Optional[list[Conversation]] = None,
        inference_config: Optional[InferenceConfig] = None,
    ) -> list[Conversation]:
        """Runs model inference.

        Args:
            input: A list of conversations to run inference on. Optional.
            inference_config: Parameters for inference.
                If not specified, a default config is inferred.

        Returns:
            List[Conversation]: Inference output.
        """
        if input is not None and (
            inference_config and inference_config.input_path is not None
        ):
            raise ValueError(
                "Only one of input or inference_config.input_path should be provided."
            )

        # Ensure the inference config has up-to-date generation parameters.
        if inference_config:
            if inference_config.generation:
                self._check_unsupported_params(inference_config.generation)
            elif self._generation_params:
                inference_config = copy.deepcopy(inference_config)
                inference_config.generation = self._generation_params

                # Warn the user: They provided an inference config without generation
                # params, so what was the point of providing it in the first place?
                logger.warning(
                    "No generation parameters provided in the inference config. Using "
                    "the generation parameters that the engine was initialized with."
                )

        if input is not None:
            return self.infer_online(input, inference_config)
        elif inference_config and inference_config.input_path is not None:
            return self.infer_from_file(inference_config.input_path, inference_config)
        else:
            raise ValueError(
                "One of input or inference_config.input_path must be provided."
            )

    def _read_conversations(self, input_filepath: str) -> list[Conversation]:
        """Reads conversations from a file in Oumi chat format.

        Args:
            input_filepath: The path to the file containing the conversations.

        Returns:
            List[Conversation]: A list of conversations read from the file.
        """
        conversations = []
        with open(input_filepath) as f:
            for line in f:
                # Only parse non-empty lines.
                if line.strip():
                    conversation = Conversation.from_json(line)
                    conversations.append(conversation)
        return conversations

    def _get_scratch_filepath(self, output_filepath: str) -> str:
        """Returns a scratch filepath for the given output filepath.

        For example, if the output filepath is "/foo/bar/output.json", the scratch
        filepath will be "/foo/bar/scratch/output.json"

        Args:
            output_filepath: The output filepath.

        Returns:
            str: The scratch filepath.
        """
        original_filepath = Path(output_filepath)
        return str(original_filepath.parent / "scratch" / original_filepath.name)

    def _save_conversation(
        self, conversation: Conversation, output_filepath: str
    ) -> None:
        """Appends a conversation to a file in Oumi chat format.

        Args:
            conversation: The conversation to save.
            output_filepath: The path to the file where the conversation should be
                saved.
        """
        # Make the directory if it doesn't exist.
        Path(output_filepath).parent.mkdir(parents=True, exist_ok=True)
        with jsonlines.open(output_filepath, mode="a") as writer:
            json_obj = conversation.to_dict()
            writer.write(json_obj)

    def _save_conversations(
        self, conversations: list[Conversation], output_filepath: str
    ) -> None:
        """Saves conversations to a file in Oumi chat format.

        Args:
            conversations: A list of conversations to save.
            output_filepath: The path to the file where the conversations should be
                saved.
        """
        # Make the directory if it doesn't exist.
        Path(output_filepath).parent.mkdir(parents=True, exist_ok=True)
        with jsonlines.open(output_filepath, mode="w") as writer:
            for conversation in tqdm(conversations, desc="Saving conversations"):
                json_obj = conversation.to_dict()
                writer.write(json_obj)

    def _check_unsupported_params(self, generation_params: GenerationParams):
        """Checks for unsupported parameters and logs warnings.

        If a parameter is not supported, and a non-default value is provided,
        a warning is logged.
        """
        supported_params = self.get_supported_params()
        default_generation_params = GenerationParams()

        for param_name, value in generation_params:
            if param_name not in supported_params:
                is_non_default_value = (
                    getattr(default_generation_params, param_name) != value
                )

                if is_non_default_value:
                    logger.warning(
                        f"{self.__class__.__name__} does not support {param_name}. "
                        f"Received value: {param_name}={value}. "
                        "This parameter will be ignored."
                    )

    @abstractmethod
    def get_supported_params(self) -> set[str]:
        """Returns a set of supported generation parameters for this engine.

        Override this method in derived classes to specify which parameters
        are supported.

        Returns:
            Set[str]: A set of supported parameter names.
        """
        raise NotImplementedError

    @abstractmethod
    def infer_online(
        self,
        input: list[Conversation],
        inference_config: Optional[InferenceConfig] = None,
    ) -> list[Conversation]:
        """Runs model inference online.

        Args:
            input: A list of conversations to run inference on.
            inference_config: Parameters for inference.

        Returns:
            List[Conversation]: Inference output.
        """
        raise NotImplementedError

    @abstractmethod
    def infer_from_file(
        self,
        input_filepath: str,
        inference_config: Optional[InferenceConfig] = None,
    ) -> list[Conversation]:
        """Runs model inference on inputs in the provided file.

        This is a convenience method to prevent boilerplate from asserting the existence
        of input_filepath in the generation_params.

        Args:
            input_filepath: Path to the input file containing prompts for generation.
            inference_config: Parameters for inference.

        Returns:
            List[Conversation]: Inference output.
        """
        raise NotImplementedError

    def apply_chat_template(
        self, conversation: Conversation, **tokenizer_kwargs
    ) -> str:
        """Applies the chat template to the conversation.

        Args:
            conversation: The conversation to apply the chat template to.
            tokenizer_kwargs: Additional keyword arguments to pass to the tokenizer.

        Returns:
            str: The conversation with the chat template applied.
        """
        tokenizer = getattr(self, "_tokenizer", None)

        if tokenizer is None:
            raise ValueError("Tokenizer is not initialized.")

        if tokenizer.chat_template is None:
            raise ValueError("Tokenizer does not have a chat template.")

        if "tokenize" not in tokenizer_kwargs:
            tokenizer_kwargs["tokenize"] = False

        return tokenizer.apply_chat_template(conversation, **tokenizer_kwargs)
