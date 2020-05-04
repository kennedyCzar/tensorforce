# Copyright 2020 Tensorforce Team. All Rights Reserved.
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
# ==============================================================================

import unittest

from tensorforce import Agent, Environment, Runner

from test.unittest_base import UnittestBase


class TestDocumentation(UnittestBase, unittest.TestCase):

    def test_environment(self):
        self.start_tests(name='getting-started-environment')

        environment = Environment.create(
            environment='gym', level='CartPole', max_episode_timesteps=500
        )
        self.finished_test()

        environment = Environment.create(environment='gym', level='CartPole-v1')
        self.finished_test()

        environment = Environment.create(
            environment='test/data/environment.json', max_episode_timesteps=500
        )
        self.finished_test()

        environment = Environment.create(
            environment='test.data.custom_env.CustomEnvironment', max_episode_timesteps=10
        )
        self.finished_test()

    def test_agent(self):
        self.start_tests(name='getting-started-agent')

        environment = Environment.create(
            environment='gym', level='CartPole', max_episode_timesteps=50
        )
        self.finished_test()

        agent = Agent.create(
            agent='tensorforce', environment=environment, update=64,
            objective='policy_gradient', reward_estimation=dict(horizon=20)
        )
        self.finished_test()

        agent = Agent.create(
            agent='ppo', environment=environment, batch_size=10, learning_rate=1e-3
        )
        self.finished_test()

        agent = Agent.create(agent='test/data/agent.json', environment=environment)
        self.finished_test()

    def test_execution(self):
        self.start_tests(name='getting-started-execution')

        runner = Runner(
            agent='test/data/agent.json', environment=dict(environment='gym', level='CartPole'),
            max_episode_timesteps=10
        )
        runner.run(num_episodes=10)
        runner.run(num_episodes=5, evaluation=True)
        runner.close()
        self.finished_test()

        # Create agent and environment
        environment = Environment.create(
            environment='test/data/environment.json', max_episode_timesteps=10
        )
        agent = Agent.create(agent='test/data/agent.json', environment=environment)

        # Train for 200 episodes
        for _ in range(10):
            states = environment.reset()
            terminal = False
            while not terminal:
                actions = agent.act(states=states)
                states, terminal, reward = environment.execute(actions=actions)
                agent.observe(terminal=terminal, reward=reward)

        # Evaluate for 100 episodes
        sum_rewards = 0.0
        for _ in range(5):
            states = environment.reset()
            internals = agent.initial_internals()
            terminal = False
            while not terminal:
                actions, internals = agent.act(states=states, internals=internals, independent=True)
                states, terminal, reward = environment.execute(actions=actions)
                sum_rewards += reward

        sum_rewards / 100

        # Close agent and environment
        agent.close()
        environment.close()

        self.finished_test()

    def test_readme(self):
        self.start_tests(name='readme')

        # ====================

        from tensorforce import Agent, Environment

        # Pre-defined or custom environment
        environment = Environment.create(
            environment='gym', level='CartPole', max_episode_timesteps=500
        )

        # Instantiate a Tensorforce agent
        agent = Agent.create(
            agent='tensorforce',
            environment=environment,  # alternatively: states, actions, (max_episode_timesteps)
            memory=1000,
            update=dict(unit='timesteps', batch_size=64),
            optimizer=dict(type='adam', learning_rate=3e-4),
            policy=dict(network='auto'),
            objective='policy_gradient',
            reward_estimation=dict(horizon=20)
        )

        # Train for 300 episodes
        for _ in range(1):

            # Initialize episode
            states = environment.reset()
            terminal = False

            while not terminal:
                # Episode timestep
                actions = agent.act(states=states)
                states, terminal, reward = environment.execute(actions=actions)
                agent.observe(terminal=terminal, reward=reward)

        agent.close()
        environment.close()

        # ====================

        self.finished_test()

    def test_states_actions_multi_input(self):
        self.start_tests(name='states-actions-multi-input')

        agent, environment = self.prepare(
            states=dict(
                observation=dict(type='float', shape=(16, 16, 3)),
                attributes=dict(type='int', shape=(4, 2), num_values=5)
            ),
            actions=dict(type='float', shape=10),
            policy=[
                [
                    dict(type='retrieve', tensors=['observation']),
                    dict(type='conv2d', size=16),
                    dict(type='flatten'),
                    dict(type='register', tensor='obs-embedding')
                ],
                [
                    dict(type='retrieve', tensors=['attributes']),
                    dict(type='embedding', size=16),
                    dict(type='flatten'),
                    dict(type='register', tensor='attr-embedding')
                ],
                [
                    dict(
                        type='retrieve', tensors=['obs-embedding', 'attr-embedding'],
                        aggregation='concat'
                    ),
                    dict(type='dense', size=32)
                ]
            ]
        )

        agent.close()
        environment.close()
        self.finished_test()

    def test_masking(self):
        self.start_tests(name='masking')

        agent, environment = self.prepare(
            states=dict(type='float', shape=(10,)),
            actions=dict(type='int', shape=(), num_values=3)
        )
        states = environment.reset()
        assert 'state' in states and 'action_mask' in states
        states['action_mask'] = [True, False, True]

        action = agent.act(states=states)
        assert action != 1

        agent.close()
        environment.close()
        self.finished_test()
