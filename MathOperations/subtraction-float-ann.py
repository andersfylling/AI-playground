import torch
import sys
import numpy as np

from torch.autograd import Variable


dtype = torch.FloatTensor

N, D_in, H1, H2, D_out = 10000, 2, 12, 3, 1

# Create random Tensors to hold input and outputs, and wrap them in Variables.
# Setting requires_grad=False indicates that we do not need to compute gradients
# with respect to these Variables during the backward pass.
x = Variable(torch.randn(N, D_in).type(dtype), requires_grad=False)
y = Variable(torch.randn(N, D_out).type(dtype), requires_grad=False)

# expected results
for i in range(N):
    y[i] = x[i][0] - x[i][1]


# Create random Tensors for weights, and wrap them in Variables.
# Setting requires_grad=True indicates that we want to compute gradients with
# respect to these Variables during the backward pass.
w1 = Variable(torch.randn(D_in, H1).type(dtype), requires_grad=True)
w2 = Variable(torch.randn(H1, H2).type(dtype), requires_grad=True)
w3 = Variable(torch.randn(H2, D_out).type(dtype), requires_grad=True)


test = Variable(torch.randn(1, D_in).type(dtype), requires_grad=False)

print(test[0], test.mm(w1).clamp(min=0).mm(w2).clamp(min=0).mm(w3))
print("expected", (test[0][0] - test[0][1]))  # (-1.2450 - 0.2680)=-0.4864 == -1.5130

learning_rate = 1e-6
print("training..")
for t in range(100000):  # epochs
    # Forward pass: compute predicted y using operations on Variables; these
    # are exactly the same operations we used to compute the forward pass using
    # Tensors, but we do not need to keep references to intermediate values since
    # we are not implementing the backward pass by hand.
    y_pred = x.mm(w1).clamp(min=0).mm(w2).clamp(min=0).mm(w3)


    # Compute and print loss using operations on Variables.
    # Now loss is a Variable of shape (1,) and loss.data is a Tensor of shape
    # (1,); loss.data[0] is a scalar value holding the loss.
    loss = (y_pred - y).pow(2).sum()
    if (t % 1000 == 0):
        print(t, loss.data[0])
        sys.stdout.flush()

    # Use autograd to compute the backward pass. This call will compute the
    # gradient of loss with respect to all Variables with requires_grad=True.
    # After this call w1.grad and w2.grad will be Variables holding the gradient
    # of the loss with respect to w1 and w2 respectively.
    loss.backward()

    # Update weights using gradient descent; w1.data and w2.data are Tensors,
    # w1.grad and w2.grad are Variables and w1.grad.data and w2.grad.data are
    # Tensors.
    w1.data -= learning_rate * w1.grad.data
    w2.data -= learning_rate * w2.grad.data
    w3.data -= learning_rate * w3.grad.data

    # Manually zero the gradients
    w1.grad.data.zero_()
    w2.grad.data.zero_()
    w3.grad.data.zero_()

print("done")
print(test[0], test.mm(w1).clamp(min=0).mm(w2).clamp(min=0).mm(w3))
print("expected", (test[0][0] - test[0][1]))  # (-1.2450 - 0.2680)=-1.5130 == -1.5130, MEAN 0.06544433534145355

# Conclusion: Using ANN for subtraction seems really slow. Should take a look at RNN.
