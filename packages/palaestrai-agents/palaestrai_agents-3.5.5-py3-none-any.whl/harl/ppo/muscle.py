from typing import List, Any

import numpy as np
import torch

from palaestrai.agent import (
    BrainDumper,
    ActuatorInformation,
    SensorInformation,
)
from palaestrai.agent import Muscle, LOG
from palaestrai.types import Box, Discrete
from harl.ppo.action_type import ActionType


def set_setpoint_to_actuator(setpoint, actuator: ActuatorInformation):
    """Clip actions to make sure they are not higher than max or lower than min
    of allowed action space."""
    if isinstance(actuator.space, Box):
        box_space: Box = actuator.space
        _clipped_value: np.ndarray = np.clip(
            setpoint, box_space.low, box_space.high
        )
        setpoint = box_space.reshape_to_space(_clipped_value)
    elif not isinstance(actuator.space, Discrete):
        raise NotImplementedError(
            "Spaces other than Box and Discrete are currently not supported"
        )
    actuator(setpoint)


class PPOMuscle(Muscle):
    def __init__(self) -> None:
        super().__init__()

        # Initialize the covariance matrix used to query the actor for actions
        self.cov_mat = None
        self.actor = None
        self.critic = None
        self._device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

    def setup(self) -> None:
        pass

    @torch.no_grad()
    def propose_actions(
        self,
        sensors: List[SensorInformation],
        actuators_available: List[ActuatorInformation],
    ) -> tuple[list[ActuatorInformation], Any]:
        assert self.actor is not None
        assert (
            any(
                isinstance(actuator.space, Box)
                for actuator in actuators_available
            )
            and self.actor.action_type == ActionType.CONTINUOUS
        ) or (
            any(
                isinstance(actuator.space, Discrete)
                for actuator in actuators_available
            )
            and self.actor.action_type == ActionType.DISCRETE
        )

        readings = [v.value for v in sensors]

        obs = torch.tensor(
            np.array(readings),
            dtype=torch.float,
        ).to(self._device)

        dist = self.actor(obs)
        value = self.critic(obs)
        action = dist.sample()

        probs = dist.log_prob(action).cpu().data.numpy().flatten()
        action = action.cpu().data.numpy().flatten()
        value = value.cpu().data.numpy().flatten()

        for idx, actuator in enumerate(actuators_available):
            # all_seen_shapes is the number of elements in the actions array
            # represented by all n-dimensional actuators we have already
            # iterated.
            # E.g., an actuator with Box([1., 1., 1.], [2., 2., 2.]) has a
            # shape of (3,), so we have already "seen" 3 items in actions when
            # we iterated past it. In general, np.prod(space.shape) gives us
            # the number of items in a flattened list. This we need to
            # calculate for *all* actuators we've already seen.
            if not np.isscalar(action):
                all_seen_shapes = int(
                    np.sum(
                        [
                            np.prod(a.space.shape)  # type: ignore[attr-defined]
                            for a in actuators_available[:idx]
                        ]
                    )
                )
                this_shape_flattened = int(np.prod(actuator.space.shape))
                setpoint_flattened = action[
                    all_seen_shapes : all_seen_shapes + this_shape_flattened
                ]
                setpoint_unflattened = np.reshape(
                    setpoint_flattened, actuator.space.shape
                )
                set_setpoint_to_actuator(setpoint_unflattened, actuator)
            else:
                set_setpoint_to_actuator(action, actuator)

        additional_data = {"readings": readings, "probs": probs, "vals": value}

        return actuators_available, (action, additional_data)

    def update(self, update: Any) -> None:
        if update is None:
            LOG.error("%s cannot update without new data!", self)
            return
        self.actor = update["actor"]
        self.critic = update["critic"]

    def prepare_model(self) -> None:
        assert (
            self._model_loaders
        ), "Brain loaders are not set for preparing model"
        actor_bio = BrainDumper.load_brain_dump(
            self._model_loaders, "ppo_actor"
        )
        critic_bio = BrainDumper.load_brain_dump(
            self._model_loaders, "ppo_critic"
        )

        if actor_bio is not None and critic_bio is not None:
            try:
                self.actor = torch.load(
                    actor_bio, weights_only=False, map_location=self._device
                )
                if self.actor is not None:
                    self.actor.to(self._device)

                self.critic = torch.load(
                    critic_bio, weights_only=False, map_location=self._device
                )
                if self.actor is not None:
                    self.critic.to(self._device)
            except Exception as e:
                LOG.exception(
                    "PPOMuscle(id=0x%x, uid=%s) encountered error while "
                    "loading model: %s ",
                    id(self),
                    str(self.uid),
                    e,
                )
                raise

    def __repr__(self):
        pass
