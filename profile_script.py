from plangym import AtariEnvironment, ParallelEnvironment
from fragile.env import DiscreteEnv
from fragile.models import RandomDiscrete
from fragile.swarm import States, Swarm
import numpy as np


if __name__ == "__main__":

    env = ParallelEnvironment(
        env_class=AtariEnvironment,
        name="MsPacman-v0",
        clone_seeds=True,
        autoreset=True,
        blocking=False,
    )

    state, obs = env.reset()

    states = [state.copy() for _ in range(10)]
    actions = [env.action_space.sample() for _ in range(10)]

    data = env.step_batch(states=states, actions=actions)
    new_states, observs, rewards, ends, infos = data
    fe = DiscreteEnv(env)
    states = fe.reset(batch_size=10)
    swarm = Swarm(
        model=lambda x: RandomDiscrete(x),
        env=lambda: fe,
        n_walkers=100,
        skipframe=4,
        max_iters=300,
    )
    from IPython.core.display import clear_output

    def run_swarm(self, model_states: "States" = None, env_states: "States" = None):
        self.init_walkers(model_states=model_states, env_states=env_states)
        i = 0
        while not self.walkers.calculate_end_cond():
            self.step_walkers()
            self.walkers.balance()
            if i % 2500000 == 0:
                print(self.walkers)
                clear_output(True)
            i += 1

        return self.calculate_action()

    swarm.run_swarm()