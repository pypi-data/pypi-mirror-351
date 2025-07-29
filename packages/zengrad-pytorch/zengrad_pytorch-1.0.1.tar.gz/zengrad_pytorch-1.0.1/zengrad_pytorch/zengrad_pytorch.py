import torch
from torch.optim import Optimizer
import math

class ZenGrad(Optimizer):
    def __init__(self, params, lr=0.01, initial_accumulator_value=0.1):
        if lr <= 0.0:
            raise ValueError(f"Invalid learning rate: {lr}")
        if initial_accumulator_value < 0.0:
            raise ValueError(f"Invalid accumulator value: {initial_accumulator_value}")

        defaults = dict(lr=lr, initial_accumulator_value=initial_accumulator_value)
        super(ZenGrad, self).__init__(params, defaults)

    def step(self, closure=None):
        """Performs a single optimization step."""
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            lr = group['lr']
            acc_init = group['initial_accumulator_value']

            for p in group['params']:
                if p.grad is None:
                    continue

                grad = p.grad.data
                if grad.is_sparse:
                    raise RuntimeError("ZenGrad does not support sparse gradients")

                state = self.state[p]

                # State initialization
                if 'accumulator' not in state:
                    state['accumulator'] = torch.full_like(p.data, acc_init)

                accumulator = state['accumulator']
                accumulator.add_(grad.pow(2))  # A_t = A_{t-1} + g_t^2

                # Compute effective learning rate
                effective_lr = lr / (torch.log(accumulator + 1) + 1)

                # Update parameters
                p.data.addcmul_(grad, -effective_lr)  # θ = θ - η_t * g_t

        return loss
