from typing import List, Tuple, Any, Optional

import numpy as np
import torch as T

from harl.sac.action_type import ActionType
from harl.sac.network import Actor
from palaestrai.agent import (
    BrainDumper,
    ActuatorInformation,
    SensorInformation,
)
from palaestrai.agent import Muscle, LOG
from palaestrai.agent.util.information_utils import concat_flattened_values
from palaestrai.types import Box, Discrete
from palaestrai.types.mode import Mode


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


class SACMuscle(Muscle):
    def __init__(self, start_steps: int = 10000):
        """
        Inference worker implementation of SAC.

        This muscle implements the rollout worker part of the SAC algorithm.

        Parameters
        ----------
        start_steps : int = 10000
            Number of steps for uniform-random action selection,
            before running real policy. Helps exploration. The parameter is
            ignored in testing mode.
        """
        super().__init__()
        self._start_steps = start_steps
        self._actions_proposed = 0
        self._model: Optional[Actor] = None
        self._device = T.device("cuda" if T.cuda.is_available() else "cpu")

    def setup(self, *args, **kwargs):
        self._actions_proposed = 0

    def propose_actions(
        self,
        sensors: List[SensorInformation],
        actuators_available: List[ActuatorInformation],
    ) -> Tuple[List[ActuatorInformation], Any]:
        assert self._model is not None
        assert (
            any(
                isinstance(actuator.space, Box)
                for actuator in actuators_available
            )
            and self._model.action_type == ActionType.CONTINUOUS
        ) or (
            any(
                isinstance(actuator.space, Discrete)
                for actuator in actuators_available
            )
            and self._model.action_type == ActionType.DISCRETE
        )
        self._actions_proposed += 1

        values = concat_flattened_values(sensors)

        if (
            self._actions_proposed < self._start_steps
            and self.mode == Mode.TRAIN
        ):
            # During warm-up, we do not have a model,
            #   so we skip everything below and just return random actions
            for actuator in actuators_available:
                action = actuator.space.sample()
                actuator(action)
            return (
                actuators_available,
                (
                    values,
                    np.array([a.value for a in actuators_available]).flatten(),
                ),
            )

        _obs_tensor = T.tensor(
            values,
            dtype=T.float,
        ).to(self._device)
        actions = self._model.act(
            _obs_tensor,
            self._mode != Mode.TRAIN,  # Apply noise only during training.
        )[0]

        for idx, actuator in enumerate(actuators_available):
            # all_seen_shapes is the number of elements in the actions array
            # represented by all n-dimensional actuators we have already
            # iterated.
            # E.g., an actuator with Box([1., 1., 1.], [2., 2., 2.]) has a
            # shape of (3,), so we have already "seen" 3 items in actions when
            # we iterated past it. In general, np.prod(space.shape) gives us
            # the number of items in a flattened list. This we need to
            # calculate for *all* actuators we've already seen.
            if not np.isscalar(actions):
                all_seen_shapes = int(
                    np.sum(
                        [
                            np.prod(
                                a.space.shape  # type: ignore[attr-defined]
                            )
                            for a in actuators_available[:idx]
                        ]
                    )
                )
                this_shape_flattened = int(
                    np.prod(actuator.action_space.shape)
                )
                setpoint_flattened = actions[
                    all_seen_shapes : all_seen_shapes + this_shape_flattened
                ]
                setpoint_unflattened = np.reshape(
                    setpoint_flattened, actuator.action_space.shape
                )
                set_setpoint_to_actuator(setpoint_unflattened, actuator)
            else:
                set_setpoint_to_actuator(actions, actuator)

        return actuators_available, (
            values,
            np.array([actions]),
        )

    def update(self, update):
        if update is None:
            LOG.error("%s cannot update without new data!", self)
            return
        self._load_model(update)

    def prepare_model(self):
        assert (
            self._model_loaders
        ), "Brain loaders are not set for preparing model"
        bio = BrainDumper.load_brain_dump(self._model_loaders, "sac_actor")
        if bio is not None:
            try:
                self._load_model(bio)
            except Exception as e:
                LOG.exception(
                    "SACMuscle(id=0x%x, uid=%s) encountered error while "
                    "loading model: %s ",
                    id(self),
                    str(self.uid),
                    e,
                )
                raise

    def _load_model(self, model):
        self._model = T.load(
            model, weights_only=False, map_location=self._device
        )
        self._model.pi.to_device(self._device)
        self._model.eval()

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return (
            f"harl.SACMuscle(uid={self.uid}, "
            f"start_steps={self._start_steps}, "
            f"device={self._device})"
        )
