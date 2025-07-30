"""
functions used to create dask-clusters automatically based on the environment a script is executed in.
"""
import os
import sys
import dask
import distributed
import multiprocessing
from .tempdir import TempDir
from .batchjob import get_batch_job, _get_num_available_procs
import atexit
import logging
from time import sleep

# storage the batchjob object
batchjob_object = None

# adapt some settings for dask
from distributed.config import config
config["connect-timeout"] = "30"        # increase the connect-timeout from 3 to 10s


def init_cluster(ntasks=None, extend=False):
    """
    Create a Dask.distributed cluster and return the client object. The type of the cluster is automatically selected
    based on the environment of the script. Inside of a SLURM job, a distributed Cluster is created. All allocated
    resources are used for this purpose. Without a job scheduler like SLURM, a LocalCluster is created.

    Parameters
    ----------
    ntasks : int
            the number of tasks (threads or processes) to start.
    extend : bool
            launch workers in a separate slurm jobs or not
    Returns
    -------
    distributed.Client
            a client object usable to submit computations to the new cluster.
    """
    
    # In case of requesting an extension of the available resources through asking for more workers through SlurmCluster
    # check that the sbatch command its present in the system and call init_slurm_cluster()
    logging.debug("Starting cluster")
    if extend == True and check_sbatch_availability():
        job_id = os.getenv("SLURM_JOB_ID")
        if job_id is None:
            logging.info("Launching new workers through SLURM.")
        else:
            logging.info("Launching new workers through SLURM even do we already are inside a SLURM job with ID %s" %
                         job_id)

        return init_slurm_cluster(nodes=ntasks)

    # create a temporal directory for the work log files
    tmpdir = TempDir(cleanup=False)
    
    # figure out which type of cluster to create
    global batchjob_object
    batchjob_object = get_batch_job(local_dir=tmpdir.getpath(), ntasks=ntasks)

    # start the distributed cluster prepared by the command above
    batchjob_object.start()

    return batchjob_object.get_client()


def init_slurm_cluster(nodes=1, tmp_dir="/dev/shm/"):
    """
    # Submiting DASK workers to a Slurm cluster. Need to merge it with the init_cluster in enstools.core

           Parameters
    ----------
    nodes : int
            number of nodes
    """
    from dask.distributed import Client
    from dask_jobqueue import SLURMCluster

    # Define the kind of jobs that will be launched to the cluster
    # This will apply for each one of the different jobs sent
    cluster = SLURMCluster(
        cores=12,
        memory="24 GB",
        queue="cluster",
        local_directory=tmp_dir,
        #silence_logs="debug",
    )
    # Start workers
    cluster.scale(jobs=nodes)
    client = Client(cluster)
    logging.info("You can follow the dashboard in the following link:\n%s" % client.dashboard_link)
    # client.wait_for_workers(nodes)
    return client    


def get_num_available_procs():
    """
    Get the number of processes available for parallel execution of tasks. If a distributed cluster was started before,
    then the number of workers within this cluster is returned. Otherwise the number of physical processors on the local
    computer. If OMP_NUM_THREADS is defined, it's value will be used!

    Returns
    -------
    int :
            number of processors.
    """
    if batchjob_object is not None:
        return batchjob_object.ntasks
    else:
        return _get_num_available_procs()


def get_client_and_worker():
    """
    This function can be used the get dask distributed client and worker objects.

    Returns
    -------
    tuple :
            (None, None): when called without dask cluster running
            (client, None) when called on a non-worker process
            (client, worker) when called on a worker process
    """
    try:
        client = distributed.get_client()
        logging.debug("get_client_and_worker: client object found!")
    except ValueError:
        client = None
        logging.debug("get_client_and_worker: not running in a dask cluster!")
    if client is not None:
        try:
            worker = distributed.get_worker()
            logging.debug("get_client_and_worker: worker object found!")
        except ValueError:
            worker = None
            logging.debug("get_client_and_worker: not running inside of a worker process!")
    else:
        worker = None
    return client, worker


def all_workers_are_local(client):
    """
    Use the client the get information about the workers.

    Returns
    -------
    bool :
            True is all workers are running on local host
    """
    workers = list(client.scheduler_info()['workers'])
    for worker in workers:
        if not worker.startswith("tcp://127.0.0.1:"):
            return False
    return True


class RoundRobinWorkerIterator():
    def __init__(self, client):
        """
        an iterator that iterates over and over over all workers

        Parameters
        ----------
        client : distributed.client
                the client object of which the worker should be utilised.
        """
        workers = list(client.scheduler_info()['workers'])
        self.workers = list(map(lambda x: tuple(x.replace("tcp://", "").rsplit(":", 1)), workers))
        self.index = 0

    def __iter__(self):
        return self

    def next(self):
        next = self.workers[self.index]  # type: tuple
        self.index += 1
        if self.index == len(self.workers):
            self.index = 0
        return next

    
def check_sbatch_availability():
    """
    Function that checks that sbatch command can be reached in the system.
    It launches the sbatch version command and checks that the return code its 0.
    """
    from subprocess import run, PIPE, CalledProcessError
    
    command = "sbatch --version"
    arguments = command.split()
    result = run(arguments, stdout=PIPE)
    try:
        result.check_returncode()
        return True
    except CalledProcessError:
        logging.warning("Sbatch its not available, won't start an additional cluster.")
        return False