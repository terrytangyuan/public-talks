# --------------------------------------------------------------------------------
# airflow

def create_dag(dag_id,
               schedule,
               dag_number,
               default_args):

    def hello_world_py(*args):
        print('Hello World')
        print('This is one of Python function on DAG: {}'.format(str(dag_number)))

    dag = DAG(dag_id,
              schedule_interval=schedule,
              default_args=default_args)

    with dag:
        t1 = PythonOperator(
            task_id='hello_world',
            python_callable=hello_world_py,
            dag_number=dag_number)

    return dag


# build a dag for each number in range(10)
for n in range(1, 10):
    dag_id = 'hello_world_{}'.format(str(n))

    default_args = {'owner': 'airflow',
                    'start_date': datetime(2018, 1, 1)
                    }

    schedule = '@daily'

    dag_number = n

    globals()[dag_id] = create_dag(
        dag_id,
        schedule,
        dag_number,
        default_args)

# --------------------------------------------------------------------------------
# kfp

class FlipCoinOp(dsl.ContainerOp):
    """Flip a coin and output heads or tails randomly."""

    def __init__(self):
        super(FlipCoinOp, self).__init__(
            name='Flip',
            image='python:alpine3.6',
            command=['sh', '-c'],
            arguments=['python -c "import random; result = \'heads\' if random.randint(0,1) == 0 '
                       'else \'tails\'; print(result)" | tee /tmp/output'],
            file_outputs={'output': '/tmp/output'})


class PrintOp(dsl.ContainerOp):
    """Print a message."""
    def __init__(self, msg):
        super(PrintOp, self).__init__(
            name='Print',
            image='alpine:3.6',
            command=['echo', msg],
        )


# define the recursive operation
@graph_component
def flip_component(flip_result):
    print_flip = PrintOp(flip_result)
    flipA = FlipCoinOp().after(print_flip)
    with dsl.Condition(flipA.output == 'heads'):
        flip_component(flipA.output)


@dsl.pipeline(
    name='pipeline flip coin',
    description='shows how to use graph_component.'
)
def recursive():
    flipA = FlipCoinOp()
    flipB = FlipCoinOp()
    flip_loop = flip_component(flipA.output)
    flip_loop.after(flipB)
    PrintOp('cool, it is over. %s' % flipA.output).after(flip_loop)

# --------------------------------------------------------------------------------
# argo-python-dsl

class DagDiamond(Workflow):

    @task
    @parameter(name="message", value="A")
    def A(self, message: V1alpha1Parameter) -> V1alpha1Template:
        return self.echo(message=message)

    @task
    @parameter(name="message", value="B")
    @dependencies(["A"])
    def B(self, message: V1alpha1Parameter) -> V1alpha1Template:
        return self.echo(message=message)

    @task
    @parameter(name="message", value="C")
    @dependencies(["A"])
    def C(self, message: V1alpha1Parameter) -> V1alpha1Template:
        return self.echo(message=message)

    @task
    @parameter(name="message", value="D")
    @dependencies(["B", "C"])
    def D(self, message: V1alpha1Parameter) -> V1alpha1Template:
        return self.echo(message=message)

    @template
    @inputs.parameter(name="message")
    def echo(self, message: V1alpha1Parameter) -> V1Container:
        container = V1Container(
            image="alpine:3.7",
            name="echo",
            command=["echo", "{{inputs.parameters.message}}"],
        )

        return container

# --------------------------------------------------------------------------------
# couler - coin flip

def random_code():
    import random

    result = "heads" if random.randint(0, 1) == 0 else "tails"
    print(result)


def flip_coin():
    return couler.run_script(
        image="couler/python:3.6",
        source=random_code,
    )


def heads():
    return couler.run_container(
        image="couler/python:3.6",
        command=["bash", "-c", 'echo "it was heads"'],
    )


def tails():
    return couler.run_container(
        image="couler/python:3.6",
        command=["bash", "-c", 'echo "it was tails"'],
    )


result = flip_coin()
couler.when(couler.equal(result, "heads"), lambda: heads())
couler.when(couler.equal(result, "tails"), lambda: tails())

# --------------------------------------------------------------------------------
# couler - DAG

def job(name):
    couler.run_container(
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=[name],
        step_name=name,
    )

#     A
#    / \
#   B   C
#  /
# D
def linear():
    couler.set_dependencies(lambda: job(name="A"), dependencies=None)
    couler.set_dependencies(lambda: job(name="B"), dependencies=["A"])
    couler.set_dependencies(lambda: job(name="C"), dependencies=["A"])
    couler.set_dependencies(lambda: job(name="D"), dependencies=["B"])

#   A
#  / \
# B   C
#  \ /
#   D
def diamond():
    couler.dag(
        [
            [lambda: job(name="A")],
            [lambda: job(name="A"), lambda: job(name="B")],  # A -> B
            [lambda: job(name="A"), lambda: job(name="C")],  # A -> C
            [lambda: job(name="B"), lambda: job(name="D")],  # B -> D
            [lambda: job(name="C"), lambda: job(name="D")],  # C -> D
        ]
    )
