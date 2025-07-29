from __future__ import annotations

import io
import itertools
import logging
from copy import deepcopy
from typing import TYPE_CHECKING, Sequence, Optional, List

import numpy as np
import torch as T
from torch.optim import Adam

from harl.Networks.replaybuffer import ReplayBuffer
from palaestrai.agent import (
    Brain,
)
from palaestrai.agent import BrainDumper
from palaestrai.agent.util.information_utils import (
    concat_flattened_act_scale_bias,
    concat_flattened_values,
)
from palaestrai.types import Box, Discrete, Mode
from .action_type import ActionType
from .network import Actor, Critic


if TYPE_CHECKING:
    import torch.optim

LOG = logging.getLogger("palaestrai.agent.brain.SACBrain")


class SACBrain(Brain):
    """
    Learning implementation of SAC.

    SAC learner implementation based on the
    `OpenAI Spinning Up in DRL implementation <https://spinningup.openai.com/en/latest/algorithms/sac.html>`_,
    but extended with alpha annealing.

    Further reading:

    * Soft Actor Critic: Algorithms and Applications — http://arxiv.org/abs/1812.05905
    * SAC for Discrete Action Spaces — https://arxiv.org/abs/1910.07207
    * Target Entropy Annealing for SAC — https://arxiv.org/abs/2112.02852

    Parameters
    ----------
    replay_size : int
        Maximum length of replay buffer.
    fc_dims : Sequence[int] = (256, 256)
        Dimensions of the hidden layers of the agent's actor and critic
        networks. "fc" stands for "fully connected".
    activation : str = torch.nn.ReLU
        Activation function to use
    gamma : float = 0.99
        Discount factor. (Always between 0 and 1.)
    polyak : float = 0.995
        Interpolation factor in polyak averaging for target networks.
        Target networks are updated towards main networks according to:
        $$\theta_{\text{targ}} \leftarrow \rho \theta_{\text{targ}} + (
        1-\rho) \theta,$$
        where $\rho$ is polyak. (Always between 0 and 1, usually close to 1.)
    lr : float = 1e-3
        Learning rate (used for both policy and value learning).
    batch_size : int = 100
        Minibatch size for SGD.
    update_after : int = 1000
        Number of env interactions to collect before starting to do
        gradient descent updates. Ensures replay buffer is full enough
        for useful updates.
    update_every : int = 50
        Number of env interactions that should elapse between
        gradient descent updates.
        Note: Regardless of how long you wait between updates, the ratio of
        environment interactions to gradient steps is locked to 1.
    """

    def __init__(
        self,
        replay_size: int = int(1e6),
        fc_dims: Sequence[int] = (256, 256),
        activation: str = "torch.nn.ReLU",
        gamma: float = 0.99,
        polyak: float = 0.995,
        lr: float = 1e-3,
        batch_size: int = 100,
        update_after: int = 1000,
        update_every: int = 50,
    ):
        super().__init__()

        # Action type, device, and state variables:
        self._action_type = ActionType.OTHER
        self._device = T.device("cuda" if T.cuda.is_available() else "cpu")
        self._step = 0
        self._previous_actions = None
        self._previous_objective = None
        self._previous_observations = None

        # These are our hyperparameters:
        self.replay_size = replay_size
        self._fc_dims = fc_dims
        self._activation = activation
        self.gamma = gamma
        self.polyak = polyak
        self.lr = lr
        self.batch_size = batch_size
        self.update_after = update_after
        self.update_every = update_every

        # Models (actor, critic, etc.), as well as dimensions and scaling:
        self.actor: Optional[Actor] = None
        self.actor_target: Optional[Actor] = None
        self.critic: Optional[Critic] = None
        self.critic_target: Optional[Critic] = None

        # Replay buffer and optimizer:
        self.q_params: List[torch.nn.Parameter] = []
        self.replay_buffer: Optional[ReplayBuffer] = None
        self.q_optimizer: Optional[torch.optim.Optimizer] = None
        self.pi_optimizer: Optional[torch.optim.Optimizer] = None

        # Entropy bonus and alpha annealing:
        self._target_entropy = T.tensor(0)
        self._log_alpha = T.zeros(1, requires_grad=True, device=self._device)
        self._alpha = self._log_alpha.exp().item()
        self._alpha_optimizer = Adam([self._log_alpha], lr=self.lr)

    def setup(self):
        """Configures models (actor, critic, ...) and replay buffer."""
        assert len(self.sensors) > 0
        assert len(self.actuators) > 0
        self.memory.size_limit = 2  # We have our own memory, just need "done".

        # check for action type and set to type if matched
        if all(isinstance(actuator.space, Box) for actuator in self.actuators):
            self._action_type = ActionType.CONTINUOUS
        elif all(
            isinstance(actuator.space, Discrete) for actuator in self.actuators
        ):
            self._action_type = ActionType.DISCRETE
        else:
            self._action_type = ActionType.OTHER
            LOG.error(
                self,
            )
            raise TypeError(
                f"{self} requires exclusively Box or exclusively "
                f"Discrete action spaces; hybrid SAC "
                f"is not yet supported, sorry.",
            )

        obs_dim: int = int(
            np.sum([np.prod(s.space.shape) for s in self.sensors])
        )
        act_dim: int
        act_scale: np.ndarray = np.array([0])
        act_bias: np.ndarray = np.array([0])

        if self._action_type == ActionType.CONTINUOUS:
            act_dim = int(
                np.sum([np.prod(a.space.shape) for a in self.actuators])
            )
            act_scale = concat_flattened_act_scale_bias(
                self.actuators, np.subtract
            )
            act_bias = concat_flattened_act_scale_bias(self.actuators, np.add)
        elif self._action_type == ActionType.DISCRETE:
            act_dim = self.actuators[0].space.n
        else:
            # We've already handled this, but just in case:
            raise TypeError(
                f"{self} requires exclusively Box or exclusively "
                f"Discrete action spaces; hybrid SAC "
                f"is not yet supported, sorry.",
            )

        # Make sure that we do not overwrite an already loaded Brain
        # dump. The order in which the palaestrai.agent.Learner class
        # class us is important, because we can do offline training afterwards.

        model_none_dict = {
            "actor_is_none": False,
            "critic_is_none": False,
            "actor_target_is_none": False,
            "critic_target_is_none": False,
        }

        if self.actor is None:
            model_none_dict["actor_is_none"] = True
        if self.critic is None:
            model_none_dict["critic_is_none"] = True
        if self.actor_target is None:
            model_none_dict["actor_target_is_none"] = True
        if self.critic_target is None:
            model_none_dict["critic_target_is_none"] = True

        if all(model_none_dict.values()):
            self._init_models(obs_dim, act_dim, act_scale, act_bias)
        else:
            if any(model_none_dict.values()):
                LOG.warning(
                    "%s loaded only some models: %s", self, model_none_dict
                )

        self.pi_optimizer = Adam(self.actor.pi.parameters(), lr=self.lr)
        self.q_params = itertools.chain(
            self.critic.q1.parameters(), self.critic.q2.parameters()
        )
        self.q_optimizer = Adam(self.q_params, lr=self.lr)

        self._target_entropy = -T.Tensor([act_dim]).to(self._device).item()

        self.replay_buffer = ReplayBuffer(
            state_dim=obs_dim,
            action_dim=act_dim,
            max_size=self.replay_size,
            device=self._device,
        )

        T.manual_seed(
            self.seed
        )  # cf. https://pytorch.org/docs/stable/notes/randomness.html

    def _init_models(
        self,
        obs_dim: int,
        act_dim: int,
        act_scale: np.ndarray,
        act_bias: np.ndarray,
    ):
        assert self.actor is None
        assert self.critic is None
        assert self.actor_target is None
        assert self.critic_target is None

        self.actor = Actor(
            obs_dim=obs_dim,
            act_dim=act_dim,
            act_scale=T.tensor(act_scale, dtype=T.float32).to(self._device),
            act_bias=T.tensor(act_bias, dtype=T.float32).to(self._device),
            action_type=self._action_type,
            fc_dims=self._fc_dims,
        ).to(self._device)
        self.actor.pi.to(self._device)
        self.actor.pi.net.to(self._device)
        if self._action_type == ActionType.CONTINUOUS:
            self.actor.pi.mu_layer.to(self._device)
            self.actor.pi.log_std_layer.to(self._device)
        elif self._action_type == ActionType.DISCRETE:
            self.actor.pi.logits_layer.to(self._device)

        self.critic = Critic(
            obs_dim, act_dim, self._action_type, self._fc_dims
        ).to(self._device)
        self.critic.q1.to(self._device)
        self.critic.q2.to(self._device)
        self.critic.q1.q.to(self._device)
        self.critic.q2.q.to(self._device)
        self.actor_target = deepcopy(self.actor)
        self.actor_target.to(self._device)
        self.critic_target = deepcopy(self.critic)
        self.critic_target.to(self._device)
        for p in self.actor_target.parameters():
            p.requires_grad = False
        for p in self.critic_target.parameters():
            p.requires_grad = False

    def thinking(self, muscle_id, data_from_muscle):
        assert self.actor is not None
        assert self.critic is not None
        assert self.actor_target is not None
        assert self.critic_target is not None
        assert self.replay_buffer is not None

        update = None

        if data_from_muscle is None:  # Okay, happens during initialization
            update = io.BytesIO()
            T.save(self.actor, update)
            update.seek(0)
            return update

        if self.mode != Mode.TRAIN:
            return update

        assert isinstance(data_from_muscle, tuple)
        assert len(data_from_muscle) == 2
        assert all(
            isinstance(datapoint_from_muscle, np.ndarray)
            for datapoint_from_muscle in data_from_muscle
        )

        if (
            self._previous_observations is not None
            and self._previous_actions is not None
            and self._previous_objective is not None
            # This is needed, because the None output (usually only first one)
            # as objective is stored
            # in memory as np.array([None])
            and (
                isinstance(self._previous_objective, float)
                or (
                    isinstance(self._previous_objective, np.ndarray)
                    and self._previous_objective.item() is not None
                )
            )
        ):
            self._step += 1
            self._remember(
                self._previous_observations,
                self._previous_actions,
                self._previous_objective,
                data_from_muscle[0],
                self.memory.tail(1).dones.item(),
            )
        self._previous_observations = data_from_muscle[0]
        self._previous_actions = data_from_muscle[1]
        try:
            self._previous_objective = self.memory.tail(1).objective.item()
        except ValueError as e:
            LOG.error(
                "%s: Got objective value '%s' from Memory, which is "
                "wrong: Need a 1D NumPy array. Substituting with 0.0, "
                "but this should be fixed. (%s)",
                self,
                self.memory.tail(1).objective,
                e,
            )

        if (
            self._step >= self.update_after
            and self._step % self.update_every == 0
        ):
            try:
                update = self.update()
                self.store()
            except Exception as e:
                LOG.exception(
                    "%s could not update: %s.\n" "Actor: %s\n" "Critic: %s",
                    self,
                    e,
                    self.actor,
                    self.critic,
                )
        return update

    def compute_loss_q_discrete(self, data):
        o, a, o2, r, d = data

        q1 = self.critic.q1(o, a)
        q2 = self.critic.q2(o, a)

        # maybe needed to get q values only for taken actions:
        # q1 = q1.gather(1, data.actions.long()).view(-1)
        # q2 = q2.gather(1, data.actions.long()).view(-1)

        # Bellman backup for Q functions
        with T.no_grad():
            # Target actions come from *current* policy
            a2, logp_a2, next_state_action_probs = self.actor.pi(o2)

            # Target Q-values
            q1_pi_targ = self.critic_target.q1(o2, a2)
            q2_pi_targ = self.critic_target.q2(o2, a2)
            min_qf_next_target = next_state_action_probs * (
                T.min(q1_pi_targ, q2_pi_targ) - self._alpha * logp_a2
            )
            min_qf_next_target = min_qf_next_target.sum(dim=1)
            backup = r + self.gamma * (1 - d) * min_qf_next_target
            backup = backup.reshape(q1.shape[0], -1)

        # MSE loss against Bellman backup
        loss_q1 = ((q1 - backup) ** 2).mean()
        loss_q2 = ((q2 - backup) ** 2).mean()
        loss_q = loss_q1 + loss_q2

        # Useful info for logging
        q_info = dict(
            Q1Vals=q1.cpu().detach().numpy(), Q2Vals=q2.cpu().detach().numpy()
        )

        return loss_q, q_info

    def compute_loss_q(self, data):
        o, a, o2, r, d = data

        q1 = self.critic.q1(o, a)
        q2 = self.critic.q2(o, a)

        # Bellman backup for Q functions
        with T.no_grad():
            # Target actions come from *current* policy
            a2, logp_a2, _ = self.actor.pi(o2)

            # Target Q-values
            q1_pi_targ = self.critic_target.q1(o2, a2)
            q2_pi_targ = self.critic_target.q2(o2, a2)
            q_pi_targ = T.min(q1_pi_targ, q2_pi_targ)
            backup = r + self.gamma * (1 - d) * (
                q_pi_targ - self._alpha * logp_a2
            )

        # MSE loss against Bellman backup
        loss_q1 = ((q1 - backup) ** 2).mean()
        loss_q2 = ((q2 - backup) ** 2).mean()
        loss_q = loss_q1 + loss_q2

        # Useful info for logging
        q_info = dict(
            Q1Vals=q1.cpu().detach().numpy(), Q2Vals=q2.cpu().detach().numpy()
        )

        return loss_q, q_info

    def compute_loss_pi_discrete(self, data):
        o = data[0]
        pi, logp_pi, action_probs = self.actor.pi(o)
        with T.no_grad():
            q1_pi = self.critic.q1(o, pi)
            q2_pi = self.critic.q2(o, pi)
            q_pi = T.min(q1_pi, q2_pi)

        # Entropy-regularized policy loss
        loss_pi = (action_probs * ((self._alpha * logp_pi) - q_pi)).mean()

        # Useful info for logging
        pi_info = dict(LogPi=logp_pi.cpu().detach().numpy())

        self._anneal_alpha_discrete(log_pi=logp_pi, action_probs=action_probs)
        return loss_pi, pi_info

    def compute_loss_pi(self, data):
        o = data[0]
        pi, logp_pi, _ = self.actor.pi(o)
        q1_pi = self.critic.q1(o, pi)
        q2_pi = self.critic.q2(o, pi)
        q_pi = T.min(q1_pi, q2_pi)

        # Entropy-regularized policy loss
        loss_pi = (self._alpha * logp_pi - q_pi).mean()

        # Useful info for logging
        pi_info = dict(LogPi=logp_pi.cpu().detach().numpy())

        self._anneal_alpha(log_pi=logp_pi)
        return loss_pi, pi_info

    def _anneal_alpha(self, log_pi):
        alpha_loss = (
            -self._log_alpha * (log_pi + self._target_entropy).detach()
        ).mean()
        self._alpha_optimizer.zero_grad()
        alpha_loss.backward()
        self._alpha_optimizer.step()
        self._alpha = self._log_alpha.exp().item()

    def _anneal_alpha_discrete(self, log_pi, action_probs):
        alpha_loss = (
            action_probs.detach()
            * (-self._log_alpha * (log_pi + self._target_entropy).detach())
        ).mean()
        self._alpha_optimizer.zero_grad()
        alpha_loss.backward()
        self._alpha_optimizer.step()
        self._alpha = self._log_alpha.exp().item()

    def update(self):
        data = self.replay_buffer.sample(self.batch_size)
        # self._check_device(data)
        self.q_optimizer.zero_grad()

        if self._action_type == ActionType.CONTINUOUS:
            loss_q, q_info = self.compute_loss_q(data)
        elif self._action_type == ActionType.DISCRETE:
            loss_q, q_info = self.compute_loss_q_discrete(data)
        else:
            LOG.error(
                "Brain(id=0x%x) has received a wrong action space %s when calculating q loss. Requires exclusively Box, or exclusively Discrete action spaces.",
                id(self),
                type(self._action_type),
            )
            raise TypeError

        loss_q.backward()
        self.q_optimizer.step()

        for p in self.q_params:
            p.requires_grad = False
        # Next run one gradient descent step for pi.
        self.pi_optimizer.zero_grad()
        if self._action_type == ActionType.CONTINUOUS:
            loss_pi, pi_info = self.compute_loss_pi(data)
        elif self._action_type == ActionType.DISCRETE:
            loss_pi, pi_info = self.compute_loss_pi_discrete(data)
        else:
            LOG.error(
                "Brain(id=0x%x) has received a wrong action space %s when calculating pi loss. Requires exclusively Box, or exclusively Discrete action spaces.",
                id(self),
                type(self._action_type),
            )
            raise TypeError

        loss_pi.backward()
        self.pi_optimizer.step()

        for p in self.q_params:
            p.requires_grad = True

        # updated target net
        with T.no_grad():
            for p, p_targ in zip(
                self.actor.parameters(), self.actor_target.parameters()
            ):
                p_targ.data.mul_(self.polyak)
                p_targ.data.add_((1 - self.polyak) * p.data)

            for p, p_targ in zip(
                self.critic.parameters(), self.critic_target.parameters()
            ):
                p_targ.data.mul_(self.polyak)
                p_targ.data.add_((1 - self.polyak) * p.data)

        LOG.debug(
            "%s has trained: loss_q = %f, loss_pi = %f", self, loss_q, loss_pi
        )
        bio = io.BytesIO()
        T.save(self.actor, bio)
        bio.seek(0)
        return bio

    def _check_device(self, data):
        LOG.debug(
            "All data used for computation of loss q are on cuda: %s",
            str(all(var.is_cuda for var in data)),
        )
        LOG.debug("Devices of data: %s", str([var.device for var in data]))
        LOG.debug(
            "Critic q1 model is on cuda: %s",
            str(all(p.is_cuda for p in self.critic.q1.q.parameters())),
        )
        LOG.debug(
            "Critic q1 model device: %s",
            str([p.device for p in self.critic.q1.q.parameters()]),
        )
        LOG.debug(
            "Critic q2 model is on cuda: %s",
            str(all(p.is_cuda for p in self.critic.q2.q.parameters())),
        )
        LOG.debug(
            "Critic q2 model device: %s",
            str([p.device for p in self.critic.q2.q.parameters()]),
        )
        LOG.debug(
            "Critic target q1 model is on cuda: %s",
            str(all(p.is_cuda for p in self.critic_target.q1.q.parameters())),
        )
        LOG.debug(
            "Critic target q1 model device: %s",
            str([p.device for p in self.critic_target.q1.q.parameters()]),
        )
        LOG.debug(
            "Critic target q2 model is on cuda: %s",
            str(all(p.is_cuda for p in self.critic_target.q2.q.parameters())),
        )
        LOG.debug(
            "Critic target q2 model device: %s",
            str([p.device for p in self.critic_target.q2.q.parameters()]),
        )
        LOG.debug(
            "Actor pi net model is on cuda: %s",
            str(all(p.device for p in self.actor.pi.net.parameters())),
        )
        LOG.debug(
            "Actor pi net model device: %s",
            str([p.device for p in self.actor.pi.net.parameters()]),
        )
        LOG.debug(
            "Actor target pi net model is on cuda: %s",
            str(all(p.device for p in self.actor_target.pi.net.parameters())),
        )
        LOG.debug(
            "Actor target pi net model device: %s",
            str([p.device for p in self.actor_target.pi.net.parameters()]),
        )
        if self._action_type == ActionType.CONTINUOUS:
            LOG.debug(
                "Actor pi mu_layer model is on cuda: %s",
                str(
                    all(p.device for p in self.actor.pi.mu_layer.parameters())
                ),
            )
            LOG.debug(
                "Actor pi mu_layer model device: %s",
                str([p.device for p in self.actor.pi.mu_layer.parameters()]),
            )
            LOG.debug(
                "Actor pi log_std_layer model is on cuda: %s",
                str(
                    all(
                        p.device
                        for p in self.actor.pi.log_std_layer.parameters()
                    )
                ),
            )
            LOG.debug(
                "Actor pi log_std_layer model device: %s",
                str(
                    [
                        p.device
                        for p in self.actor.pi.log_std_layer.parameters()
                    ]
                ),
            )
            LOG.debug(
                "Actor target pi mu_layer model is on cuda: %s",
                str(
                    all(
                        p.device
                        for p in self.actor_target.pi.mu_layer.parameters()
                    )
                ),
            )
            LOG.debug(
                "Actor target pi mu_layer model device: %s",
                str(
                    [
                        p.device
                        for p in self.actor_target.pi.mu_layer.parameters()
                    ]
                ),
            )
            LOG.debug(
                "Actor target pi log_std_layer model is on cuda: %s",
                str(
                    all(
                        p.device
                        for p in self.actor_target.pi.log_std_layer.parameters()
                    )
                ),
            )
            LOG.debug(
                "Actor target pi log_std_layer model device: %s",
                str(
                    [
                        p.device
                        for p in self.actor_target.pi.log_std_layer.parameters()
                    ]
                ),
            )
        elif self._action_type == ActionType.DISCRETE:
            LOG.debug(
                "Actor pi logits_layer model is on cuda: %s",
                str(
                    all(
                        p.device
                        for p in self.actor.pi.logits_layer.parameters()
                    )
                ),
            )
            LOG.debug(
                "Actor pi logits_layer model device: %s",
                str(
                    [p.device for p in self.actor.pi.logits_layer.parameters()]
                ),
            )
            LOG.debug(
                "Actor target pi logits_layer model is on cuda: %s",
                str(
                    all(
                        p.device
                        for p in self.actor_target.pi.logits_layer.parameters()
                    )
                ),
            )
            LOG.debug(
                "Actor target pi logits_layer model device: %s",
                str(
                    [
                        p.device
                        for p in self.actor_target.pi.logits_layer.parameters()
                    ]
                ),
            )
        # for var in data:
        #    assert var.device == self._device
        # for p in self.critic.q1.q.parameters():
        #    assert p.device == self._device
        # for p in self.critic.q2.q.parameters():
        #    assert p.device == self._device
        # for p in self.actor.pi.net.parameters():
        #    assert p.device == self._device
        # if self.action_type == ActionType.CONTINUOUS:
        #    for p in self.actor.pi.mu_layer.parameters():
        #        assert p.device == self._device
        #    for p in self.actor.pi.log_std_layer.parameters():
        #        assert p.device == self._device
        # elif self.action_type == ActionType.DISCRETE:
        #    for p in self.actor.pi.logits_layer.parameters():
        #        assert p.device == self._device

        # self.critic_target.q1(o2, a2)
        # q2_pi_targ = self.critic_target.q2(o2, a2)

    def store(self):
        bio = io.BytesIO()

        T.save(self.actor, bio)
        BrainDumper.store_brain_dump(bio, self._dumpers, "sac_actor")

        bio.seek(0)
        bio.truncate(0)
        T.save(self.actor_target, bio)
        BrainDumper.store_brain_dump(bio, self._dumpers, "sac_actor_target")

        bio.seek(0)
        bio.truncate(0)
        T.save(self.critic, bio),
        BrainDumper.store_brain_dump(bio, self._dumpers, "sac_critic")

        bio.seek(0)
        bio.truncate(0)
        T.save(self.critic_target, bio)
        BrainDumper.store_brain_dump(bio, self._dumpers, "sac_critic_target")

    def load(self):
        actor_dump = BrainDumper.load_brain_dump(self._dumpers, "sac_actor")
        actor_target_dump = BrainDumper.load_brain_dump(
            self._dumpers, "sac_actor_target"
        )
        critic_dump = BrainDumper.load_brain_dump(self._dumpers, "sac_critic")
        critic_target_dump = BrainDumper.load_brain_dump(
            self._dumpers, "sac_critic_target"
        )
        if any(
            [
                x is None
                for x in [
                    actor_dump,
                    actor_target_dump,
                    critic_dump,
                    critic_target_dump,
                ]
            ]
        ):
            return  # Don't apply "None"s
        self.actor = T.load(
            actor_dump, weights_only=False, map_location=self._device
        )
        self.critic = T.load(
            critic_dump, weights_only=False, map_location=self._device
        )
        self.actor_target = T.load(
            actor_target_dump, weights_only=False, map_location=self._device
        )
        self.critic_target = T.load(
            critic_target_dump, weights_only=False, map_location=self._device
        )

    def _remember(self, readings, actions, reward, next_state, done):
        state = np.array(readings)
        action = np.array(actions)
        try:
            self.replay_buffer.add(
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                done=done,
            )
        except Exception as e:
            LOG.critical(
                "Brain(id=0x%x) could not add the following to the replay_buffer: "
                "state: %s, "
                "action: %s, "
                "reward: %s, "
                "next_state: %s, "
                "done: %s, "
                "because of: %s",
                id(self),
                str(state),
                str(action),
                str(reward),
                str(next_state),
                str(done),
                e,
            )
            raise

    def pretrain(self):
        for mmem in self.memory._data.values():
            for i in range(len(mmem.rewards) - 1):
                obs = np.array(
                    [x.value for x in mmem.sensor_readings[i]],
                    dtype=np.float64,
                )
                acts = np.array(
                    [x.value for x in mmem.actuator_setpoints[i]],
                    dtype=np.float64,
                )
                reward = mmem.objective[i]
                nobs = np.array(
                    [x.value for x in mmem.sensor_readings[i + 1]],
                    dtype=np.float64,
                )
                done = mmem.dones[i]
                self.replay_buffer.add(obs, acts, nobs, reward, done)

    def get_seq(self) -> Optional[T.nn.Sequential]:
        assert self.actor is not None
        return self.actor.get_seq()

    def __repr__(self):
        return (
            f"{self.__class__}("
            f"fc_dims={self._fc_dims}, "
            f"activation={self._activation}, "
            f"replay_size={self.replay_size}, "
            f"update_after={self.update_after}, "
            f"update_every={self.update_every}, "
            f"batch_size={self.batch_size}, "
            f"lr={self.lr}, "
            f"gamma={self.gamma}, "
            f"polyak={self.polyak}"
            ")"
        )

    def __str__(self):
        return repr(self)
