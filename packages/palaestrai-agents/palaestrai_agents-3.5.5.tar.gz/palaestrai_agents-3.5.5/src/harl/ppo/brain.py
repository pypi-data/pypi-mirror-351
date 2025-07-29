from __future__ import annotations
from typing import Optional, Sequence, Any

import io
import torch as T
import numpy as np

from harl.ppo.network import (
    PPOMemory,
    ActorNetwork,
    CriticNetwork,
)
from palaestrai.agent import (
    Brain,
    BrainDumper,
    LOG,
)
from palaestrai.types import Mode
from palaestrai.types import Box, Discrete
from .action_type import ActionType


class PPOBrain(Brain):
    """
    Implements the Proximal Policy Optimization (PPO) Algorithm.

    For details of the algorithm, see the original publication:
    Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov,
    "Proximal policy optimization algorithms," arXiv.org,
    `<https://arxiv.org/abs/1707.06347>`_, arXiv:1707.06347 [cs.LG].

    Alternatively, the section on PPO in OpenAI's "Spinning Up in
    Deep Reinforcement Learning" documentation is also a way to understand
    the algorithm:
    `<https://spinningup.openai.com/en/latest/algorithms/ppo.html>`_

    Parameters
    ----------
    timesteps_per_batch : int = 4
        Number of timesteps per batch.
    max_timesteps_per_episode : int = 96
        Maximum amount of timesteps per episode.
    n_updates_per_iteration : int = 50
        The number of updates per learning iteration.

    actor_lr : float = 3e-4
        The actor's learning rate.
    critic_lr : float = 1e-3
        The critic's learning rate.
    adam_eps : float = 1e-5
        The adam optimiser's epsilon parameter.
    fc_dims: Sequence[int] = (256, 256)
        Dimensions (amount of fully connected neurons) of the hidden layers
        in the agent's actor and critic networks.

    gamma : float = 0.99
        Factor by which to discount the worth of later rewards.
    clip : float = 0.2
        Epsilon value of the clipping function.
    gae_lambda : float = 0.95
        Lambda of the general advantage estimation.
    action_std_init : float = 0.6
        Initial standard deviation of the actions.
    action_std_decay_rate : float = 0.05
        Rate by which the action's standard deviation should decay.
    min_action_std : float = 0.1
        Minimum value of the action's standard deviation.
    action_std_decay_freq : int = 2.5e5
        Frequency of the decay (every x steps).
    """

    def __init__(
        self,
        timesteps_per_batch: int = 4,
        max_timesteps_per_episode: int = 96,
        n_updates_per_iteration: int = 50,
        actor_lr: float = 3e-4,  # CleanRL: 2.5e-4
        critic_lr: float = 1e-3,  # CleanRL: 2.5e-4
        adam_eps: float = 1e-5,
        fc_dims: Sequence[int] = (256, 256),
        gamma: float = 0.99,
        clip: float = 0.2,
        gae_lambda: float = 0.95,
        action_std_init: float = 0.6,  # STD = Standard Deviation
        action_std_decay_rate: float = 0.05,
        min_action_std: float = 0.1,
        action_std_decay_freq: int = 2.5e5,  # type: ignore[assignment]
    ):
        super().__init__()

        self.timesteps_per_batch = timesteps_per_batch
        self.max_timesteps_per_episode = max_timesteps_per_episode
        self.n_updates_per_iteration = n_updates_per_iteration

        self.actor_lr = actor_lr
        self.critic_lr = critic_lr
        self.adam_eps = adam_eps
        self.fc_dims = fc_dims

        self.gamma = gamma
        self.clip = clip
        self.gae_lambda = gae_lambda

        self.action_std_init = action_std_init
        self.action_std_decay_rate = action_std_decay_rate
        self.min_action_std = min_action_std
        self.action_std_decay_freq = action_std_decay_freq

        self.actor: ActorNetwork | None = None
        self.critic: CriticNetwork | None = None

        self.t = 0
        self.step = 0
        self._action_type = ActionType.OTHER
        self._ppo_memory: Optional[PPOMemory] = None
        self._device = T.device("cuda" if T.cuda.is_available() else "cpu")
        self.action_std = self.action_std_init

    def setup(self):
        assert len(self.sensors) > 0
        assert len(self.actuators) > 0

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
                f"Discrete action spaces",
            )

        sen_dim = len(self._sensors)
        if self._action_type == ActionType.CONTINUOUS:
            act_dim = int(
                np.sum([np.prod(a.space.shape) for a in self.actuators])
            )
        elif self._action_type == ActionType.DISCRETE:
            act_dim = self.actuators[0].space.n
        else:
            # We've already handled this, but just in case:
            raise TypeError(
                f"{self} requires exclusively Box or exclusively "
                f"Discrete action spaces; hybrid SAC "
                f"is not yet supported, sorry.",
            )

        model_none_dict = {
            "actor_is_none": False,
            "critic_is_none": False,
        }

        # TODO: Why the hell are actor and critic set to CriticNetwork
        # before setup is called?
        self.actor = None
        self.critic = None

        if self.actor is None:
            model_none_dict["actor_is_none"] = True
        if self.critic is None:
            model_none_dict["critic_is_none"] = True

        if all(model_none_dict.values()):
            self._init_models(sen_dim, act_dim)
        else:
            if any(model_none_dict.values()):
                LOG.warning(
                    "Only some models are loaded: " + str(model_none_dict)
                )

        self._ppo_memory = PPOMemory(self.timesteps_per_batch)
        self.t = 0
        T.manual_seed(self.seed)

    def _init_models(
        self,
        sen_dim: int,
        act_dim: int,
    ):
        assert self.actor is None
        assert self.critic is None

        self.actor = ActorNetwork(
            sen_dim,
            act_dim,
            self._action_type,
            self.actor_lr,
            self.adam_eps,
            self.fc_dims,
            action_std_init=self.action_std_init,
        ).to(self._device)

        self.critic = CriticNetwork(
            sen_dim,
            self.critic_lr,
            self.adam_eps,
            self.fc_dims,
        ).to(self._device)

    def thinking(self, muscle_id, data_from_muscle: Any) -> Any:
        _ = muscle_id
        assert self.actor is not None
        assert self.critic is not None

        if data_from_muscle is None:
            return {
                "actor": self.actor,
                "critic": self.critic,
            }

        assert isinstance(data_from_muscle, tuple)
        assert len(data_from_muscle) == 2

        self._remember(
            reading=data_from_muscle[1]["readings"],
            action=data_from_muscle[0],
            probs=data_from_muscle[1]["probs"],
            values=data_from_muscle[1]["vals"],
            reward=self.memory.tail(1).objective.item(),  # TODO Passt net
            done=self.memory.tail(1).dones.item(),
        )

        self.step += 1
        if self.step % self.max_timesteps_per_episode == 0:
            response = self._learn()
        else:
            response = None

        if self.step % self.action_std_decay_freq == 0:
            self.decay_action_std()
        return response

    def _learn(self):
        assert self._ppo_memory is not None
        for update in range(self.n_updates_per_iteration):
            (
                state_arr,
                action_arr,
                old_prob_arr,
                values,
                reward_arr,
                dones_arr,
                batches,
            ) = self._ppo_memory.generate_batches()

            advantage = np.zeros(len(reward_arr), dtype=np.float32)
            self.learning_rate_annealing(update)

            values = values.reshape(-1)

            for t in range(len(reward_arr) - 1):
                discount = 1
                a_t = 0
                for k in range(t, len(reward_arr) - 1):
                    a_t += discount * (
                        reward_arr[k]
                        + self.gamma * values[k + 1] * (1 - int(dones_arr[k]))
                        - values[k]
                    )
                    discount *= self.gamma * self.gae_lambda
                advantage[t] = a_t
            advantage = T.tensor(advantage).to(self.actor.device)

            values = T.tensor(values).to(self.actor.device)
            for batch in batches:
                states = T.tensor(state_arr[batch], dtype=T.float).to(
                    self.actor.device
                )
                old_probs = T.tensor(old_prob_arr[batch]).to(self.actor.device)
                actions = T.tensor(action_arr[batch]).to(self.actor.device)

                critic_value = self.critic(states)
                dist = self.actor(states)
                actions = T.reshape(actions, (-1, 1))
                # actions = actions.reshape(-1)
                new_probs = dist.log_prob(actions)

                prob_ratio = new_probs.exp() / old_probs.reshape(-1).exp()
                prob_ratio = prob_ratio.reshape(-1, len(advantage[batch]))
                weighted_probs = advantage[batch] * prob_ratio
                weighted_clipped_probs = (
                    T.clamp(prob_ratio, 1 - self.clip, 1 + self.clip)
                    * advantage[batch]
                )
                actor_loss = -T.min(
                    weighted_probs, weighted_clipped_probs
                ).mean()

                returns = advantage[batch] + values[batch]
                critic_loss = (returns - critic_value) ** 2
                critic_loss = 0.5 * critic_loss.mean()

                # Could add Entropy Bonus below,
                # but no evidence of performance improvement
                total_loss = actor_loss + critic_loss
                self.actor.optimizer.zero_grad()
                self.critic.optimizer.zero_grad()
                total_loss.backward()
                self.actor.optimizer.step()
                self.critic.optimizer.step()
        self._ppo_memory.clear_memory()
        return {
            "actor": self.actor,
            "critic": self.critic,
        }

    def load(self):
        actor_dump = BrainDumper.load_brain_dump(self._dumpers, "ppo_critic")
        actor_target_dump = BrainDumper.load_brain_dump(
            self._dumpers, "ppo_actor"
        )
        critic_dump = BrainDumper.load_brain_dump(self._dumpers, "ppo_critic")
        critic_target_dump = BrainDumper.load_brain_dump(
            self._dumpers, "ppo_critic"
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
        self.actor = T.load(actor_dump, weights_only=False)
        self.critic = T.load(critic_dump, weights_only=False)

    def store(self):
        bio = io.BytesIO()

        T.save(self.actor, bio)
        BrainDumper.store_brain_dump(bio, self._dumpers, "ppo_actor")

        bio.seek(0)
        bio.truncate(0)
        T.save(self.critic, bio)
        BrainDumper.store_brain_dump(bio, self._dumpers, "ppo_critic")

    def _remember(self, reading, action, probs, values, reward, done):
        assert self._ppo_memory is not None
        self._ppo_memory.store_memory(
            state=reading,
            action=action,
            probs=probs,
            vals=values,
            reward=reward,
            done=done,
        )

    def decay_action_std(self):
        self.action_std = round(
            self.action_std - self.action_std_decay_rate, 4
        )
        if self.action_std <= self.min_action_std:
            self.action_std = self.min_action_std
        self.actor.set_action_std(self.action_std)

    def learning_rate_annealing(self, update):
        """Anneals the learning rate
        update: The current update iteration
        """
        frac = 1.0 - (update - 1.0) / self.n_updates_per_iteration
        actor_lrnow = frac * self.actor_lr
        critic_lrnow = frac * self.critic_lr
        self.actor.optimizer.param_groups[0]["lr"] = actor_lrnow
        self.critic.optimizer.param_groups[0]["lr"] = critic_lrnow
