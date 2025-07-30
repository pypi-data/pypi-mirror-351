def fidelity_reward(simulated, target):
    # Calculate state fidelity
    return np.abs(np.vdot(target, simulated)) ** 2

def cost_function_reward(cost_value):
    # Inverse exponential reward for minimization problems
    return np.exp(-cost_value)

def composite_reward(fidelity, cost, depth, weights=(0.7, 0.2, 0.1)):
    return (
        weights[0] * fidelity +
        weights[1] * (1 - cost) +
        weights[2] * (1 / depth)
    )

def hardware_aware_reward(fidelity, execution_time, error_rate):
    return fidelity * (1 - error_rate) / np.log(execution_time + 1)