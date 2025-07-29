import numpy as np
import torch


class ReplayBuffer(object):
    def __init__(self, state_dim, action_dim, device, max_size=int(1e6)):
        self.device = device
        self.max_size = max_size
        self.ptr = 0
        self.size = 0

        self.state_memory = np.zeros((self.max_size, state_dim))
        self.new_state_memory = np.zeros((self.max_size, state_dim))
        self.action_memory = np.zeros((self.max_size, action_dim))
        self.reward_memory = np.zeros(self.max_size)
        self.terminal_memory = np.zeros(self.max_size, dtype=np.float32)

    def add(self, state, action, next_state, reward, done):
        self.state_memory[self.ptr] = state
        self.action_memory[self.ptr] = action
        self.new_state_memory[self.ptr] = next_state
        self.reward_memory[self.ptr] = reward
        self.terminal_memory[self.ptr] = 1 if done else 0

        self.ptr = (self.ptr + 1) % self.max_size
        self.size = min(self.size + 1, self.max_size)

    def sample(self, batch_size):
        ind = np.random.randint(0, self.size, size=batch_size)

        return (
            torch.Tensor(self.state_memory[ind]).to(self.device),
            torch.Tensor(self.action_memory[ind]).to(self.device),
            torch.Tensor(self.new_state_memory[ind]).to(self.device),
            torch.Tensor(self.reward_memory[ind]).to(self.device),
            torch.Tensor(self.terminal_memory[ind]).to(self.device),
        )
