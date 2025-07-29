"""
    This file contains a neural network module for us to
    define our actor and critic networks in PPO.
"""

from typing import Sequence

import numpy as np
import torch
from torch import nn
from torch.distributions import MultivariateNormal
import torch.distributions.constraints
from torch.optim import Adam
from torch.nn.utils import skip_init
from harl.ppo.action_type import ActionType
from palaestrai.agent import LOG

from torch.distributions.categorical import Categorical


class ActorNetwork(nn.Module):
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        action_type: ActionType,
        lr: float = 0.0003,
        eps: float = 1e-5,
        fc_dims: Sequence[int] = (256, 256),
        action_std_init: float = 0.6,
    ):
        super(ActorNetwork, self).__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.action_type = action_type

        self.action_var = torch.full(
            (action_dim,), action_std_init * action_std_init
        )

        modules = nn.ModuleList(
            [
                layer_init(skip_init(nn.Linear, state_dim, fc_dims[0])),
                nn.ReLU(),
            ]
        )  # Input Layer
        for i in range(0, len(fc_dims) - 1):
            modules.extend(
                [
                    layer_init(
                        skip_init(nn.Linear, fc_dims[i], fc_dims[i + 1])
                    ),
                    nn.ReLU(),
                ]
            )  # Hidden Layers
        modules.extend(  # "The policy output layer weights are initialised with the scale of 0.01"
            [
                layer_init(
                    skip_init(nn.Linear, fc_dims[-1], action_dim), std=0.01
                ),
                nn.Tanh(),
            ]
        )  # Output Layer
        self.actor = nn.Sequential(*modules)

        self.optimizer = Adam(self.actor.parameters(), lr=lr, eps=eps)
        self.device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu"
        )
        self.to(self.device)

    def forward(self, state):
        if self.action_type == ActionType.DISCRETE:
            state = state.view(-1, self.state_dim)
            actions = self.actor(state.to(self.device))
            dist = Categorical(logits=actions)
            return dist

        elif self.action_type == ActionType.CONTINUOUS:
            state = state.view(-1, self.state_dim)
            action_mean = self.actor(state.to(self.device))
            cov_mat = (
                torch.diag(self.action_var).unsqueeze(dim=0).to(self.device)
            )
            dist = MultivariateNormal(action_mean, cov_mat)
            return dist

        else:
            LOG.error(
                (
                    "Brain(id=0x%x) has received a wrong action type %s when initializing actor. "
                    "Requires exclusively Box, or exclusively Discrete action spaces."
                ),
                id(self),
                self.action_type,
            )
            raise TypeError

    def set_action_std(self, new_action_std):
        self.action_var = torch.full(
            (self.action_dim,), new_action_std * new_action_std
        ).to(self.device)


class CriticNetwork(nn.Module):
    def __init__(
        self,
        state_dim: int,
        lr: float = 0.001,
        eps: float = 1e-5,
        fc_dims: Sequence[int] = (256, 256),
    ):
        super(CriticNetwork, self).__init__()
        self.state_dim = state_dim

        modules = nn.ModuleList(
            [
                layer_init(skip_init(nn.Linear, state_dim, fc_dims[0])),
                nn.ReLU(),
            ]
        )  # Input Layer
        for i in range(0, len(fc_dims) - 1):
            modules.extend(
                [
                    layer_init(
                        skip_init(nn.Linear, fc_dims[i], fc_dims[i + 1])
                    ),
                    nn.ReLU(),
                ]
            )  # Hidden Layers
        modules.extend(  # "The value output layer weights are initialized with the scale of 1"
            [layer_init(skip_init(nn.Linear, fc_dims[-1], 1), std=1.0)]
        )  # Output Layer
        self.critic = nn.Sequential(*modules)

        self.optimizer = Adam(self.critic.parameters(), lr=lr, eps=eps)
        self.device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu"
        )
        self.to(self.device)

    def forward(self, state):
        state = state.view(-1, self.state_dim)
        value = self.critic(state.to(self.device))
        return value


def layer_init(layer, std=np.sqrt(2), bias_const=0.0):
    """Reference: https://iclr-blog-track.github.io/2022/03/25/ppo-implementation-details/"""
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer


class PPOMemory:
    def __init__(self, batch_size):
        self.states = []
        self.probs = []
        self.vals = []
        self.actions = []
        self.rewards = []
        self.dones = []

        self.batch_size = batch_size

    def generate_batches(self):
        n_states = len(self.states)
        batch_start = np.arange(0, n_states, self.batch_size)
        indices = np.arange(n_states, dtype=np.int64)
        np.random.shuffle(indices)
        batches = [indices[i : i + self.batch_size] for i in batch_start]
        return (
            np.array(self.states),
            np.array(self.actions),
            np.array(self.probs),
            np.array(self.vals),
            np.array(self.rewards),
            np.array(self.dones),
            batches,
        )

    def store_memory(self, state, action, probs, vals, reward, done):
        self.states.append(state)
        self.actions.append(action)
        self.probs.append(probs)
        self.vals.append(vals)
        self.rewards.append(reward)
        self.dones.append(done)

    def clear_memory(self):
        self.states = []
        self.probs = []
        self.actions = []
        self.rewards = []
        self.dones = []
        self.vals = []
