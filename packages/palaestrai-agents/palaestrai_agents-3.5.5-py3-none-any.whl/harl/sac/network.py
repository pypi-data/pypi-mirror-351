# Source: OpenAI SpinningUp
from __future__ import annotations

from typing import Sequence, Any, Union, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions.categorical import Categorical
from torch.distributions.normal import Normal

from harl.sac.action_type import ActionType
from palaestrai.agent import LOG


def mlp(sizes, activation, output_activation=nn.Identity):
    layers = []
    for j in range(len(sizes) - 1):
        act = activation if j < len(sizes) - 2 else output_activation
        layers += [nn.Linear(sizes[j], sizes[j + 1]), act()]
    return nn.Sequential(*layers)


LOG_STD_MAX = 2
LOG_STD_MIN = -20


class DiscreteMLPActor(nn.Module):
    def __init__(self, obs_dim, act_dim, hidden_sizes, activation):
        super().__init__()
        self.obs_dim = obs_dim
        self.net = mlp([obs_dim] + list(hidden_sizes), activation, activation)
        self.logits_layer = nn.Linear(hidden_sizes[-1], act_dim)

    def forward(self, obs, deterministic=False, with_logprob=True):
        obs = obs.view(-1, self.obs_dim)
        net_out = self.net(obs)
        logits = self.logits_layer(net_out)
        pi_distribution = Categorical(logits=logits)
        if deterministic:
            # Only used for evaluating policy at test time.
            pi_action = torch.argmax(logits, dim=1)
        else:
            pi_action = pi_distribution.sample()

        if with_logprob:
            logp_pi = torch.log_softmax(logits, dim=1)
        else:
            logp_pi = None

        action_probs = pi_distribution.probs

        return pi_action, logp_pi, action_probs

    def to_device(self, device):
        self.net.to(device)
        self.logits_layer.to(device)


class SquashedGaussianMLPActor(nn.Module):
    def __init__(
        self,
        obs_dim: int,
        act_dim: int,
        fc_dims: Sequence[int],
        activation: nn.Module,
        act_scale: torch.Tensor,
        act_bias: torch.Tensor,
    ):
        super().__init__()
        self.obs_dim = obs_dim
        self.net = mlp([obs_dim] + list(fc_dims), activation, activation)
        self.mu_layer = nn.Linear(fc_dims[-1], act_dim)
        self.log_std_layer = nn.Linear(fc_dims[-1], act_dim)
        self.act_scale = act_scale
        self.act_bias = act_bias

    def forward(self, obs, deterministic=False, with_logprob=True):
        obs = obs.view(-1, self.obs_dim)
        net_out = self.net(obs)
        mu = self.mu_layer(net_out)
        log_std = self.log_std_layer(net_out)
        log_std = torch.clamp(log_std, LOG_STD_MIN, LOG_STD_MAX)
        std = torch.exp(log_std)

        # Pre-squash distribution and sample
        pi_distribution = Normal(mu, std)
        if deterministic:
            # Only used for evaluating policy at test time.
            pi_action = mu
        else:
            pi_action = pi_distribution.rsample()

        if with_logprob:
            # Compute logprob from Gaussian, and then apply correction for Tanh squashing.
            # NOTE: The correction formula is a little bit magic. To get an understanding
            # of where it comes from, check out the original SAC paper (arXiv 1801.01290)
            # and look in appendix C. This is a more numerically-stable equivalent to Eq 21.
            # Try deriving it yourself as a (very difficult) exercise. :)
            logp_pi = pi_distribution.log_prob(pi_action).sum(axis=-1)
            logp_pi -= (
                2 * (np.log(2) - pi_action - F.softplus(-2 * pi_action))
            ).sum(axis=1)
        else:
            logp_pi = None

        pi_action = torch.tanh(pi_action)
        pi_action = pi_action * self.act_scale + self.act_bias
        # None is needed to have same output dimension as discrete variant
        return pi_action, logp_pi, None

    def to_device(self, device):
        self.net.to(device)
        self.mu_layer.to(device)
        self.log_std_layer.to(device)

    def get_seq(self) -> nn.Sequential:
        modules = []

        for i, (name, m) in enumerate(self.net.named_children()):
            modules.append(m)

        modules.append(self.mu_layer)
        net = torch.nn.Sequential(*modules)

        return net


class MLPQFunction(nn.Module):
    def __init__(
        self, obs_dim, act_dim, action_type, hidden_sizes, activation
    ):
        super().__init__()
        self.obs_dim = obs_dim
        self.action_type = action_type
        if action_type == ActionType.CONTINUOUS:
            self.q = mlp(
                [obs_dim + act_dim] + list(hidden_sizes) + [1], activation
            )
        elif action_type == ActionType.DISCRETE:
            self.q = mlp(
                [obs_dim] + list(hidden_sizes) + [act_dim], activation
            )
        else:
            LOG.error(
                "Brain(id=0x%x) has received a wrong action type %s when initializing actor. Requires exclusively Box, or exclusively Discrete action spaces.",
                id(self),
                action_type,
            )
            raise TypeError

    def forward(self, obs, act):
        if self.action_type == ActionType.CONTINUOUS:
            obs = obs.view(-1, self.obs_dim)
            q = self.q(torch.cat([obs, act], dim=-1))
            return torch.squeeze(
                q, -1
            )  # Critical to ensure q has right shape.
        elif self.action_type == ActionType.DISCRETE:
            obs = obs.view(-1, self.obs_dim)
            q = self.q(obs)
            return torch.squeeze(
                q, -1
            )  # Critical to ensure q has right shape.
        else:
            LOG.error(
                "Brain(id=0x%x) has received a wrong action type %s when initializing actor. Requires exclusively Box, or exclusively Discrete action spaces.",
                id(self),
                self.action_type,
            )
            raise TypeError


class MLPActorCritic(nn.Module):
    def __init__(
        self,
        observation_space,
        action_space,
        act_limit,
        hidden_sizes=(256, 256),
        activation=nn.ReLU,
    ):
        super().__init__()

        obs_dim = observation_space
        act_dim = action_space
        act_limit = act_limit

        # build policy and value functions
        self.pi = SquashedGaussianMLPActor(
            obs_dim, act_dim, hidden_sizes, activation, act_limit
        )
        self.q1 = MLPQFunction(obs_dim, act_dim, hidden_sizes, activation)
        self.q2 = MLPQFunction(obs_dim, act_dim, hidden_sizes, activation)

    def act(self, obs, deterministic: bool = False):
        with torch.no_grad():
            a, _, __ = self.pi(obs, deterministic, False)
            return a.numpy()


class Actor(nn.Module):
    """
    An ANN actor with a squashed gaussion policy.

    Parameters
    ----------
    obs_dim : int
        Dimension of the observation space (e.g., product of sensor spaces)
    act_dim : int
        Dimension of the actuator/action space
    act_scale : np.array
        A vector containing (high - low) / 2.0
    action_type: ActionType
        Enumerate value for the type of action space (e.g. continuous, discrete)
    fc_dims : List[int] = (256, 256)
        Dimensions of hidden layers ("fc" stands for "fully connected")
    activation : torch.nn.module = torch.nn.ReLU
        Activation function to use
    """

    def __init__(
        self,
        obs_dim: int,
        act_dim: int,
        act_scale: torch.Tensor,
        act_bias: torch.Tensor,
        action_type: ActionType,
        fc_dims: Sequence[int] = (256, 256),
        activation: Any = nn.ReLU,
    ):
        super().__init__()
        self.pi: Union[SquashedGaussianMLPActor, DiscreteMLPActor]

        self.act_dim = act_dim
        self.action_type = action_type
        # build policy and value functions
        if action_type == ActionType.CONTINUOUS:
            self.pi = SquashedGaussianMLPActor(
                obs_dim,
                act_dim,
                fc_dims,
                activation,
                act_scale,
                act_bias,
            )
        elif action_type == ActionType.DISCRETE:
            self.pi = DiscreteMLPActor(obs_dim, act_dim, fc_dims, activation)
        else:
            LOG.error(
                "Brain(id=0x%x) has received a wrong action type %s when initializing actor. Requires exclusively Box, or exclusively Discrete action spaces.",
                id(self),
                action_type,
            )
            raise TypeError

    def act(self, obs, deterministic=False):
        with torch.no_grad():
            a, _, _ = self.pi(obs, deterministic, False)
            return a.cpu().detach().numpy()

    def get_seq(self) -> Optional[nn.Sequential]:
        assert self.pi is not None

        if isinstance(self.pi, SquashedGaussianMLPActor):
            return self.pi.get_seq()
        else:
            LOG.warning(f"No get_seq method found for: {str(self.pi)}")
            return None


class Critic(nn.Module):
    def __init__(
        self,
        obs_dim: int,
        act_dim: int,
        action_type: ActionType,
        fc_dims: Sequence[int],
        activation: Any = nn.ReLU,
    ):
        super().__init__()
        self.q1 = MLPQFunction(
            obs_dim, act_dim, action_type, fc_dims, activation
        )
        self.q2 = MLPQFunction(
            obs_dim, act_dim, action_type, fc_dims, activation
        )
