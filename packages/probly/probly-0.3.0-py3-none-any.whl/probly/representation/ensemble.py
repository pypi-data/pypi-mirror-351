"""Ensemble class implementation."""

from __future__ import annotations

import copy

import torch
from torch import nn
from torch.nn import functional as F

from probly.utils import torch_reset_all_parameters


class Ensemble(nn.Module):
    """Implementation of an ensemble representation to be used for uncertainty quantification.

    Attributes:
        models: torch.nn.ModuleList, the list of models in the ensemble based on the base model.

    """

    def __init__(self, base: nn.Module, n_members: int) -> None:
        """Initialization of an instance of the Ensemble class.

        Ensemble members are constructed based on copies of the base model.

        Args:
            base: torch.nn.Module, the base model to be used.
            n_members: int, the number of members in the ensemble.
        """
        super().__init__()
        self._convert(base, n_members)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of the ensemble.

        Args:
            x: torch.Tensor, input data
        Returns:
            torch.Tensor, ensemble output

        """
        return torch.stack([model(x) for model in self.models], dim=1).mean(dim=1)

    def predict_pointwise(self, x: torch.Tensor, logits: bool = False) -> torch.Tensor:
        """Forward pass that gives a point-wise prediction.

        Args:
            x: torch.Tensor, input data
            logits: bool, whether to return logits or probabilities
        Returns:
            torch.Tensor, point-wise prediction
        """
        if logits:
            return torch.stack([model(x) for model in self.models], dim=1).mean(dim=1)
        return torch.stack([F.softmax(model(x), dim=1) for model in self.models], dim=1).mean(dim=1)

    def predict_representation(self, x: torch.Tensor, logits: bool = False) -> torch.Tensor:
        """Forward pass that gives an uncertainty representation.

        Args:
            x: torch.Tensor, input data
            logits: bool, whether to return logits or probabilities
        Returns:
            torch.Tensor, uncertainty representation
        """
        if logits:
            return torch.stack([model(x) for model in self.models], dim=1)
        return torch.stack([F.softmax(model(x), dim=1) for model in self.models], dim=1)

    def _convert(self, base: nn.Module, n_members: int) -> None:
        """Convert the base model to an ensemble with n_members members.

        Args:
            base: torch.nn.Module, the base model to be converted.
            n_members: int, the number of members in the ensemble.

        """
        self.models = nn.ModuleList()
        for _ in range(n_members):
            model = copy.deepcopy(base)
            torch_reset_all_parameters(model)
            self.models.append(model)
