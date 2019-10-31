import copy
from typing import Any, Dict

import numpy as np

from fragile.core.env import DiscreteEnv
from fragile.core.states import States


class AtariEnv(DiscreteEnv):
    """The AtariEnv acts as an interface with `plangym.AtariEnvironment`.

    It can interact with any Atari environment that follows the interface of `plangym`.
    """

    STATE_CLASS = States

    def get_params_dict(self) -> Dict[str, Dict[str, Any]]:
        """Return a dictionary containing the param_dict to build an instance \
        of States that can handle all the data generated by the environment.
        """
        super_params = super(AtariEnv, self).get_params_dict()
        params = {"game_ends": {"dtype": np.bool_}}
        params.update(super_params)
        return params

    def step(self, model_states: States, env_states: States) -> States:
        """
        Set the environment to the target states by applying the specified \
        actions an arbitrary number of time steps.

        Args:
            model_states: States representing the data to be used to act on the environment..
            env_states: States representing the data to be set in the environment.

        Returns:
            States containing the information that describes the new state of the Environment.

        """
        actions = model_states.actions.astype(np.int32)
        n_repeat_actions = model_states.dt if hasattr(model_states, "dt") else 1
        new_states, observs, rewards, ends, infos = self._env.step_batch(
            actions=actions, states=env_states.states, n_repeat_action=n_repeat_actions
        )
        game_ends = [inf["game_end"] for inf in infos]

        new_state = self._get_new_states(new_states, observs, rewards,
                                         ends, len(actions), game_ends)
        return new_state

    def reset(self, batch_size: int = 1, **kwargs) -> States:
        """
        Reset the environment to the start of a new episode and returns a new \
        States instance describing the state of the Environment.

        Args:
            batch_size: Number of walkers that the returned state will have.
            **kwargs: Ignored. This environment resets without using any external data.

        Returns:
            States instance describing the state of the Environment. The first \
            dimension of the data tensors (number of walkers) will be equal to \
            batch_size.

        """
        state, obs = self._env.reset()
        states = np.array([copy.deepcopy(state) for _ in range(batch_size)])
        observs = np.array([copy.deepcopy(obs) for _ in range(batch_size)])
        rewards = np.zeros(batch_size, dtype=np.float32)
        ends = np.zeros(batch_size, dtype=np.bool_)
        game_ends = np.zeros(batch_size, dtype=np.bool_)
        new_states = self._get_new_states(states, observs, rewards, ends, batch_size, game_ends)
        return new_states

    def _get_new_states(self, states, observs, rewards, ends, batch_size, game_ends) -> States:
        ends = np.array(ends, dtype=np.bool_)
        rewards = np.array(rewards, dtype=np.float32)
        observs = np.array(observs)
        states = np.array(states)
        game_end = np.array(game_ends)
        state = self.create_new_states(batch_size=batch_size)
        state.update(states=states, observs=observs, rewards=rewards, ends=ends,
                     game_ends=game_end)
        return state