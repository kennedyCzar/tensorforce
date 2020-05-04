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

from collections import OrderedDict

from test.unittest_base import UnittestBase


class UnittestAgent(UnittestBase):
    """
    Collection of unit-tests for agent functionality.
    """

    replacement_action = 'bool'
    has_experience = True
    has_update = True

    def test_single_state_action(self):
        self.start_tests(name='single-state-action')

        states = dict(type='float', shape=(1,))
        if self.__class__.exclude_float_action:
            actions = dict(type=self.__class__.replacement_action, shape=())
        else:
            actions = dict(type='float', shape=())
        self.unittest(states=states, actions=actions)

    def test_full(self):
        self.start_tests(name='full')
        self.unittest()

    def test_query(self):
        self.start_tests(name='query')

        states = dict(type='float', shape=(1,))
        actions = dict(type=self.__class__.replacement_action, shape=())

        if self.__class__.has_update:
            agent, environment = self.prepare(
                # min_timesteps=2,  # too few steps for update otherwise
                # states=states, actions=actions,
                # policy=dict(network=dict(type='auto', size=8, depth=1, rnn=2)),
                # update=1
                # TODO: shouldn't be necessary!
            )

        else:
            agent, environment = self.prepare(states=states, actions=actions)

        states = environment.reset()
        query = agent.get_query_tensors(function='act')
        actions, queried = agent.act(states=states, query=query)
        self.assertEqual(first=len(queried), second=len(query))

        states, terminal, reward = environment.execute(actions=actions)

        query = agent.get_query_tensors(function='observe')
        _, queried = agent.observe(terminal=terminal, reward=reward, query=query)
        self.assertEqual(first=len(queried), second=len(query))

        while not terminal:
            actions = agent.act(states=states)
            states, terminal, reward = environment.execute(actions=actions)
            agent.observe(terminal=terminal, reward=reward, query=query)

        states_batch = list()
        internals_batch = list()
        actions_batch = list()
        terminal_batch = list()
        reward_batch = list()

        for _ in range(2):
            states = environment.reset()
            internals = agent.initial_internals()
            terminal = False
            while not terminal:
                states_batch.append(states)
                internals_batch.append(internals)
                actions, internals = agent.act(states=states, internals=internals, independent=True)
                actions_batch.append(actions)
                states, terminal, reward = environment.execute(actions=actions)
                terminal_batch.append(terminal)
                reward_batch.append(reward)
        if isinstance(states_batch[0], dict):
            states_batch = OrderedDict(
                (name, [states[name] for states in states_batch]) for name in states_batch[0]
            )
        if isinstance(internals_batch[0], dict):
            internals_batch = OrderedDict(
                (name, [internals[name] for internals in internals_batch])
                for name in internals_batch[0]
            )
        if isinstance(actions_batch[0], dict):
            actions_batch = OrderedDict(
                (name, [actions[name] for actions in actions_batch]) for name in actions_batch[0]
            )

        if self.__class__.has_experience:
            query = agent.get_query_tensors(function='experience')
            queried = agent.experience(
                states=states_batch, internals=internals_batch, actions=actions_batch,
                terminal=terminal_batch, reward=reward_batch, query=query
            )
            self.assertEqual(first=len(queried), second=len(query))

        if self.__class__.has_update:
            query = agent.get_query_tensors(function='update')
            queried = agent.update(query=query)
            self.assertEqual(first=len(queried), second=len(query))

        agent.close()
        environment.close()

        self.finished_test()
