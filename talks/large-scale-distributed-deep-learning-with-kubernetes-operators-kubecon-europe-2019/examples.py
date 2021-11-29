"""An example of training Keras model with multi-worker strategies."""
import tensorflow as tf


dataset = tf.data.Dataset.from_tensor_slices((x, y))

model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(16, activation='relu', input_shape=(10,)))
model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

mirrored_strategy = tf.distribute.MirroredStrategy()
with mirrored_strategy.scope():
  model = tf.keras.Sequential([tf.keras.layers.Dense(1, input_shape=(1,))])
  model.compile(loss='mse', optimizer='sgd')

model.fit(dataset, epochs=2)
model.evaluate(dataset)


apiVersion: "kubeflow.org/v1beta1"
kind: TFJob
metadata:
  name: distributed-training
spec:
  tfReplicaSpecs:
    Worker:
      replicas: 4
      template:
        spec:
          containers:
            - name: tensorflow
              image: distributed_training_tf:latest
              resources:
                limits:
                  nvidia.com/gpu: 4

apiVersion: kubeflow.org/v1alpha2
kind: MPIJob
metadata:
  name: distributed-training
spec:
  mpiReplicaSpecs:
    Worker:
      replicas: 4
      template:
        spec:
          containers:
            - name: tensorflow
              image: distributed_training_horovod:latest
              resources:
                limits:
                  nvidia.com/gpu: 4
              command: "mpirun python horovod_benchmarks.py"



import tensorflow as tf
import horovod.keras as hvd


dataset = tf.data.Dataset.from_tensor_slices((x, y))

model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(16, activation='relu', input_shape=(10,)))
model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

opt = tf.train.AdagradOptimizer(0.01 * hvd.size())
opt = hvd.DistributedOptimizer(opt)

model = tf.keras.Sequential([tf.keras.layers.Dense(1, input_shape=(1,))])
model.compile(loss='mse', optimizer=opt)

callbacks = [
    # Horovod: broadcast initial variable states from rank 0 to all other processes.
    # This is necessary to ensure consistent initialization of all workers when
    # training is started with random weights or restored from a checkpoint.
    hvd.callbacks.BroadcastGlobalVariablesCallback(0),
]

model.fit(dataset, epochs=2000, callbacks=callbacks)
model.evaluate(dataset)


import torch
import horovod.torch as hvd


data_loader = torch.utils.data.DataLoader(train_dataset, batch_size=100)

model = ...

optimizer = torch.optim.SGD(model.parameters())
optimizer = hvd.DistributedOptimizer(optimizer, named_parameters=model.named_parameters())

hvd.broadcast_parameters(model.state_dict(), root_rank=0)

for epoch in range(100):
   for batch_idx, (data, target) in enumerate(data_loader):
       optimizer.zero_grad()
       output = model(data)
       loss = torch.nn.functional.F.nll_loss(output, target)
       loss.backward()
       optimizer.step()