import json
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, log

class UCB1:
    def __init__(self, n_actions, initial_exploration=2, decay_factor=0.99):
        self.n_actions = n_actions
        self.counts = [0] * n_actions
        self.values = [0.0] * n_actions
        self.initial_exploration = initial_exploration
        self.decay_factor = decay_factor
        self.iteration = 0
        
    def select_action(self):
        self.iteration += 1
        exploration_rate = self.exploration_rate()
        
        total_counts = sum(self.counts)
        if 0 in self.counts:
            return self.counts.index(0)
        ucb_values = [
            self.values[i] + sqrt((exploration_rate * log(total_counts)) / self.counts[i])
            for i in range(self.n_actions)
        ]
        return np.argmax(ucb_values)
    
    def update(self, action, reward):
        self.counts[action] += 1
        n = self.counts[action]
        value = self.values[action]
        self.values[action] = ((n - 1) / float(n)) * value + (1 / float(n)) * reward
        
    def exploration_rate(self):
        return self.initial_exploration * (self.decay_factor ** self.iteration)

def reward_function(max_ratio, expected_ratio):
    return 1 / (1 + abs(max_ratio - expected_ratio))

def modify_json_file(action, expected_ratio):
    possible_ratios = [20, 30, 40, 50, 60, 70, 80, 90]
    max_ratio = possible_ratios[action]
    
    with open('rrmPolicy.json', 'r+') as file:
        data = json.load(file)
        for entry in data['rrmPolicyRatio']:
            if entry['sD'] == 3:
                entry['max_ratio'] = max_ratio
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()
    
    return max_ratio

def plot_results(results, rewards):
    plt.clf()
    plt.subplot(1, 2, 1)
    plt.plot(results, label='Max Ratio')
    plt.xlabel('Iteration')
    plt.ylabel('Max Ratio')
    plt.title('Max Ratio over Time')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(rewards, label='Rewards', color='green')
    plt.xlabel('Iteration')
    plt.ylabel('Reward')
    plt.title('Rewards over Time')
    plt.legend()
    
    plt.tight_layout()
    plt.pause(5)
def main():
    n_actions = 8
    n_iterations = 100
    expected_ratio = 50 
    ucb = UCB1(n_actions)
    results = []
    rewards = []
    
    plt.ion()
    
    for _ in range(n_iterations):
        action = ucb.select_action()
        max_ratio = modify_json_file(action, expected_ratio)
        reward = reward_function(max_ratio, expected_ratio)
        ucb.update(action, reward)
        results.append(max_ratio)
        rewards.append(reward)
        
        plot_results(results, rewards)
    
    plt.ioff()
    plt.show()

if __name__ == '__main__':
    main()