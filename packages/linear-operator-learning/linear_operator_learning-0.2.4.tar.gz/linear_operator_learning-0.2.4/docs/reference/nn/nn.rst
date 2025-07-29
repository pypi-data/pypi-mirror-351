.. _nn:
==========
:code:`nn`
==========

.. rst-class:: lead

   Neural Network Modules

.. module:: linear_operator_learning.nn

Table of Contents
~~~~~~~~~~~~~~~~~

- :ref:`Regressors <nn_regressors>`
- :ref:`Loss Functions <nn_loss_fns>`
- :ref:`Modules <nn_modules>`

.. _nn_regressors:
Regressors (see also :ref:`kernel regressors <kernel_regressors>`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autofunction:: linear_operator_learning.nn.ridge_least_squares

.. autofunction:: linear_operator_learning.nn.eig

.. autofunction:: linear_operator_learning.nn.evaluate_eigenfunction

.. _nn_loss_fns:
Loss Functions
~~~~~~~~~~~~~~

.. autoclass:: linear_operator_learning.nn.L2ContrastiveLoss
    :members:
    :exclude-members: __init__, __new__

.. autoclass:: linear_operator_learning.nn.KLContrastiveLoss
    :members:
    :exclude-members: __init__, __new__

.. autoclass:: linear_operator_learning.nn.VampLoss
    :members:
    :exclude-members: __init__, __new__

.. autoclass:: linear_operator_learning.nn.DPLoss
    :members:
    :exclude-members: __init__, __new__

.. _nn_modules:
Modules
~~~~~~~

.. autoclass:: linear_operator_learning.nn.MLP
    :members:
    :exclude-members: __init__, __new__, forward

.. autoclass:: linear_operator_learning.nn.ResNet
    :members:
    :exclude-members: __init__, __new__, forward

.. autoclass:: linear_operator_learning.nn.SimNorm
    :members:
    :exclude-members: __init__, __new__, forward

.. footbibliography::

