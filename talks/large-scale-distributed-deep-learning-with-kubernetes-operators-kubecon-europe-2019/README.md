# Large Scale Distributed Deep Learning with Kubernetes Operators

**Abstract**:

The focus of this talk is the usage of Kubernetes operators to manage and automate training process for machine learning tasks. Two open source Kubernetes operators, tf-operator and mpi-operator, will be discussed. Both operators manage training jobs for TensorFlow but they have different distribution strategies. The tf-operator fits the parameter server distribution strategy which has a centralized parameter server for coordination. The mpi-operator, on the other hand, utilize MPI allreduce primitive implementation. While the parameter server strategy requires a right ratio of CPU (for parameter servers) and GPU (for workers) to reach network-optimal, the all reduce distribution might be easier to optimize network cost. We will share our performance numbers in out talk for comparison of those two operators. 

* 400+ attendees for the presentation.
* Also joined as a panelist for AI Media Roundtable.
* [Slides](presentation.pdf)
* [Schedule](https://kccnceu19.sched.com/event/MPaT)
* [Video](https://youtu.be/jyLi1cfJeM8)
* [Examples](examples.py)
