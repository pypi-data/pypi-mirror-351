from __future__ import annotations

import contextlib
import logging
import os
import time
from typing import TYPE_CHECKING, Any, Callable, Union

from . import job_metadata_constants
from .api import jobs
from .backend_connection import BackendConnection
from .check_version import check_version
from .circuit_serialization import is_a_qiskit_circuit
from .computation_local import run_circuit_cirq, run_circuit_qiskit
from .estimate_result import EstimateResult
from .exceptions import (
    BQBatchJobsLimitExceededError,
    BQCPUJobsLimitExceededError,
    BQJobCouldNotCancelError,
    BQJobInvalidDeviceTypeError,
    BQJobNotCompleteError,
    BQJobsLimitExceededError,
    BQJobsMalformedShotsError,
    BQSDKUsageError,
)
from .job_result import JobResult
from .tools import format_pauli_sum
from .version import __version__

if TYPE_CHECKING:
    import datetime

# TODO this requires imports of actual quantum libraries for proper type
# checking.
CircuitT = Any

PauliSumT = Union[list[tuple[str, float]], str]

logger = logging.getLogger("bluequbit-python-sdk")


def _run_circuits_local(circuits, device, shots, pauli_sum, options):
    created_on = time.time()
    if pauli_sum is not None:
        pauli_sum = format_pauli_sum(pauli_sum)

    def _format_result(r, num_qubits):
        def to_str_time(x):
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x))

        r["created_on"] = to_str_time(created_on)
        r["run_start"] = to_str_time(r["run_start"])
        r["run_end"] = to_str_time(r["run_end"])
        # Rename counts to top_100k
        if "counts" in r:
            r["top_100k"] = r["counts"]
            del r["counts"]
        r["has_statevector"] = "state_vector" in r
        r["num_qubits"] = num_qubits
        r["run_status"] = "COMPLETED"
        return JobResult(r)

    first_circuit = circuits[0] if isinstance(circuits, list) else circuits
    try:
        from deqart_internal.circuit_info import get_num_qubits
        from deqart_internal.computation import run_circuit_object

        logger.debug("Using local deqart_internal")

        def _run_and_format_result(circuit):
            r = run_circuit_object(
                circuit, device, shots=shots, pauli_sum=pauli_sum, options=options
            )
            num_qubits = get_num_qubits(circuit)
            return _format_result(r, num_qubits)

        if isinstance(circuits, list):
            return [_run_and_format_result(c) for c in circuits]
        return _run_and_format_result(circuits)
    except (ImportError, ModuleNotFoundError) as e:
        logger.warning("Could not import %s", e)
        fn: Callable
        if is_a_qiskit_circuit(first_circuit):
            fn = run_circuit_qiskit
        elif str(type(first_circuit)) == "<class 'cirq.circuits.circuit.Circuit'>":
            fn = run_circuit_cirq
        else:
            error_msg = f"Circuit type not yet supported for {first_circuit}"
            raise BQSDKUsageError(error_msg) from None

        if isinstance(circuits, list):
            return [_format_result(fn(c, shots=shots), len(c.qubits)) for c in circuits]
        return _format_result(fn(circuits, shots=shots), len(circuits.qubits))


class BQClient:
    """Client for managing jobs on BlueQubit platform.

    :param api_token: API token of the user. If ``None``, the token will be looked
                      in the environment variable BLUEQUBIT_API_TOKEN.
    :param execution_mode: Execution mode. Can be ``"cloud"``, ``"local"`` or ``None``.
                           If ``None``, the environment variable
                           BLUEQUBIT_EXECUTION_MODE will be used if set, otherwise
                           ``"cloud"`` will be used.
    """

    _job_name_prefix_cls: str | None = None

    def __init__(self, api_token: str | None = None, execution_mode: str | None = None):
        super().__init__()
        if os.environ.get("BLUEQUBIT_TESTING") is None:
            with contextlib.suppress(Exception):
                check_version(__version__)

        if execution_mode is None:
            if "BLUEQUBIT_EXECUTION_MODE" in os.environ:
                execution_mode = os.environ["BLUEQUBIT_EXECUTION_MODE"]
                logger.info(
                    "Using execution mode from environment variable BLUEQUBIT_EXECUTION_MODE: %s",
                    execution_mode,
                )
            else:
                execution_mode = "cloud"
        self.execution_mode = execution_mode
        if self.execution_mode not in ["cloud", "local"]:
            raise ValueError(f"Invalid execution mode: {self.execution_mode}")

        self._backend_connection = BackendConnection(api_token)

        self.job_name_prefix: str | None = BQClient._job_name_prefix_cls

    def name(self):
        return "BlueQubit"

    def validate_device(self, device):
        if not isinstance(device, str):
            raise BQJobInvalidDeviceTypeError(device)
        converted_device = device.lower()
        if converted_device not in job_metadata_constants.DEVICE_TYPES:
            raise BQJobInvalidDeviceTypeError(device)
        return converted_device

    @staticmethod
    def validate_batch(batch):
        if not isinstance(batch, list):
            return False
        if len(batch) > job_metadata_constants.MAXIMUM_NUMBER_OF_BATCH_JOBS:
            raise BQBatchJobsLimitExceededError(len(batch))
        return True

    @staticmethod
    def validate_batch_for_run(batch, device):
        if not BQClient.validate_batch(batch):
            return
        if len(batch) > job_metadata_constants.MAXIMUM_NUMBER_OF_JOBS_FOR_RUN:
            raise BQJobsLimitExceededError(len(batch))
        if (
            "cpu" in device
            and len(batch) > job_metadata_constants.QUEUED_CPU_JOBS_LIMIT
        ):
            raise BQCPUJobsLimitExceededError(len(batch))

    @staticmethod
    def _validate_options(options):
        if options is None:
            return
        for k in options:
            if k not in [
                "mps_bond_dimension",
                # "mps_truncation_threshold",
                "pauli_path_truncation_threshold",
            ]:
                raise BQSDKUsageError(f"options not supported: {k}")

    def estimate(
        self, circuits: CircuitT | list[CircuitT], device: str = "cpu"
    ) -> EstimateResult | list[EstimateResult]:
        """Estimate job runtime

        :param circuits: quantum circuit or circuits
        :type circuits: Cirq, Qiskit, list
        :param device: device for which to estimate the circuit. Can be one of
                       ``"cpu"`` | ``"gpu"`` | ``"quantum"``
        :return: result or results estimate metadata
        """
        device = self.validate_device(device)
        self.validate_batch(circuits)
        response = jobs.submit_jobs(
            self._backend_connection, circuits, device, estimate_only=True
        )
        if isinstance(circuits, list):
            return [EstimateResult(data) for data in response]
        return EstimateResult(response)

    def run(
        self,
        circuits: CircuitT | list[CircuitT],
        device: str = "cpu",
        *,
        asynchronous: bool = False,
        job_name: str | None = None,
        shots: int | None = None,
        pauli_sum: PauliSumT | list[PauliSumT] | None = None,
        options: dict | None = None,
    ) -> JobResult | list[JobResult]:
        """Submit a job to run on BlueQubit platform

        :param circuits: quantum circuit or list of circuits
        :type circuits: Cirq, Qiskit, list
        :param device: device on which to run the circuit. Can be one of
                       ``"cpu"``
                       | ``"gpu"``
                       | ``"quantum"``
                       | ``"mps.cpu"``
                       | ``"mps.gpu"``
        :param asynchronous: if set to ``False``, wait for job completion before
                             returning. If set to ``True``, return immediately
        :param job_name: customizable job name
        :param shots: number of shots to run. If device is quantum and shots is None then
                      it is set to 1000. For non quantum devices, if None, full
                      probability distribution will be returned. For mps.cpu and mps.gpu devices it is limited to 1000000, for all other devices it is limited to 100000
        :param pauli_sum: The Pauli sum or a list of Pauli sum which
                          expectation value is the computation result
        :param options: dictionary of options used to configure the run:

                       - ``mps_bond_dimension`` (int): Sets a limit on the number of Schmidt
                         coefficients retained at the end of the svd algorithm.
                         Coefficients beyond this limit will be discarded.
                         Default: None (no limit on the bond dimension).
                         Applicable only to ``"mps.cpu"`` and ``"mps.gpu"`` devices.

        :return: job or jobs metadata
        """
        device = self.validate_device(device)
        self.validate_batch_for_run(circuits, device)
        self._validate_options(options)
        if shots is not None and (
            not isinstance(shots, int)
            or shots > job_metadata_constants.MAXIMUM_NUMBER_OF_SHOTS[device]
        ):
            raise BQJobsMalformedShotsError(
                shots, device, job_metadata_constants.MAXIMUM_NUMBER_OF_SHOTS[device]
            )
        if self.execution_mode == "local":
            return _run_circuits_local(circuits, device, shots, pauli_sum, options)
        job_name = (
            job_name
            if self.job_name_prefix is None
            else self.job_name_prefix + str(job_name)
        )
        if job_name is not None:
            if not isinstance(circuits, list):
                if len(job_name) > job_metadata_constants.MAX_JOB_NAME_LENGTH:
                    logger.warning(
                        "Job name is too long, it will be truncated to %s characters.",
                        job_metadata_constants.MAX_JOB_NAME_LENGTH,
                    )
            else:  # batch
                zero_fill_count = len(str(len(circuits) - 1))
                if (
                    len(job_name)
                    > job_metadata_constants.MAX_JOB_NAME_LENGTH - zero_fill_count
                ):
                    logger.warning(
                        "Batch job name is too long, it will be truncated to %s characters.",
                        job_metadata_constants.MAX_JOB_NAME_LENGTH,
                    )
        response = jobs.submit_jobs(
            self._backend_connection,
            circuits,
            device,
            job_name,
            shots=shots,
            asynchronous=asynchronous,
            pauli_sum=pauli_sum,
            options=options,
        )
        if isinstance(circuits, list):
            logger.info(
                "Submitted %s jobs. Batch ID %s", len(response), response[0]["batch_id"]
            )

            def add_circuit_to_all(job_results, circuits):
                for job_result, circuit in zip(job_results, circuits):
                    job_result.circuit = circuit

            job_results = [
                JobResult(data, self._backend_connection) for data in response
            ]
            if not asynchronous:
                if self._check_all_in_terminal_states(job_results):
                    add_circuit_to_all(job_results, circuits)
                    return job_results

                waited_job_results = self.wait(job_results)
                add_circuit_to_all(waited_job_results, circuits)
                return waited_job_results
                # if job_results[0].batch_id is not None:
                #     return self.wait(batch_id=job_results[0].batch_id)
                # else:
            add_circuit_to_all(job_results, circuits)
            return job_results
        submitted_job = JobResult(response, self._backend_connection)
        if (
            submitted_job.run_status
            in job_metadata_constants.JOB_NO_RESULT_TERMINAL_STATES
        ):
            raise BQJobNotCompleteError(
                submitted_job.job_id,
                submitted_job.run_status,
                submitted_job.error_message,
            )
        logger.info("Submitted: %s", submitted_job)
        if (
            not asynchronous
            and submitted_job.run_status
            not in job_metadata_constants.JOB_TERMINAL_STATES
        ):
            jr = self.wait(submitted_job.job_id)
            jr.circuit = circuits  # type: ignore[union-attr]
            return jr
        submitted_job.circuit = circuits
        return submitted_job

    @staticmethod
    def _check_all_in_terminal_states(job_results):
        if not isinstance(job_results, list):
            if (
                job_results.run_status
                in job_metadata_constants.JOB_NO_RESULT_TERMINAL_STATES
            ):
                raise BQJobNotCompleteError(
                    job_results.job_id,
                    job_results.run_status,
                    job_results.error_message,
                )
            return job_results.run_status in job_metadata_constants.JOB_TERMINAL_STATES
        for job_result in job_results:
            if (
                job_result.run_status
                in job_metadata_constants.JOB_NO_RESULT_TERMINAL_STATES
            ):
                raise BQJobNotCompleteError(
                    job_result.job_id,
                    job_result.run_status,
                    job_result.error_message,
                )
        return all(
            job_result.run_status in job_metadata_constants.JOB_TERMINAL_STATES
            for job_result in job_results
        )

    def wait(
        self, job_ids: str | list[str] | JobResult | list[JobResult]
    ) -> JobResult | list[JobResult]:
        """Wait for job completion

        :param job_ids: job IDs that can be found as property of :class:`JobResult` metadata
                        of :func:`~run` method, or `JobResult` instances from which job IDs
                        will be extracted
        :return: job metadata
        """
        self.validate_batch(job_ids)
        while True:
            job_results = self._get(job_ids, need_qc_unprocessed=False)
            if self._check_all_in_terminal_states(job_results):
                return job_results
            time.sleep(1.0)

    def get(
        self,
        job_ids: str | list[str] | JobResult | list[JobResult],
    ) -> JobResult | list[JobResult]:
        """Get current metadata of jobs

        :param job_ids: job IDs that can be found as property of :class:`JobResult` metadata
                        of :func:`~run` method
        :return: jobs metadata
        """
        return self._get(job_ids)

    def _get(
        self,
        job_ids: str | list[str] | JobResult | list[JobResult],
        need_qc_unprocessed=True,
    ) -> JobResult | list[JobResult]:
        self.validate_batch(job_ids)
        job_ids_list = job_ids if isinstance(job_ids, list) else [job_ids]
        if isinstance(job_ids_list[0], JobResult):
            job_ids_list = [jr.job_id for jr in job_ids_list]  # type: ignore[union-attr]
        job_results = jobs.search_jobs(
            self._backend_connection,
            job_ids=job_ids_list,
            need_qc_unprocessed=need_qc_unprocessed,
        )
        job_results = [
            JobResult(r, self._backend_connection) for r in job_results["data"]
        ]
        if isinstance(job_ids, list):
            return job_results
        return job_results[0]

    def cancel(
        self, job_ids: str | list[str] | JobResult | list[JobResult]
    ) -> JobResult | list[JobResult]:
        """Submit jobs cancel request

        :param job_ids: job IDs that can be found as property of :class:`JobResult` metadata
                        of :func:`run` method
        :return: job or jobs metadata
        """
        self.validate_batch(job_ids)
        if isinstance(job_ids, JobResult):
            job_ids = job_ids.job_id
        elif isinstance(job_ids, list) and isinstance(job_ids[0], JobResult):
            job_ids = [jr.job_id for jr in job_ids]  # type: ignore[union-attr]
        responses = jobs.cancel_jobs(self._backend_connection, job_ids)
        if isinstance(job_ids, list):
            for response in responses:
                if response["ret"] == "FAILED":
                    logger.warning(response["error_message"])
        try:
            self.wait(job_ids)
        except BQJobNotCompleteError as e:
            if not e.run_status == "CANCELED":
                raise BQJobCouldNotCancelError(
                    e.job_id, e.run_status, e.error_message
                ) from None
        return self.get(job_ids)

    def search(
        self,
        run_status: str | None = None,
        created_later_than: str | datetime.datetime | None = None,
        batch_id: str | None = None,
    ) -> list[JobResult]:
        """Search jobs

        :param run_status: if not ``None``, run status of jobs to filter.
                           Can be one of ``"FAILED_VALIDATION"`` | ``"PENDING"`` |
                           ``"QUEUED"`` | ``"RUNNING"`` | ``"TERMINATED"`` | ``"CANCELED"`` |
                           ``"NOT_ENOUGH_FUNDS"`` | ``"COMPLETED"``

        :param created_later_than: if not ``None``, filter by latest job creation datetime.
                                   Please add timezone for clarity, otherwise UTC
                                   will be assumed

        :param batch_id: if not ``None``, filter by batch ID

        :return: metadata of jobs
        """
        job_results = jobs.search_jobs(
            self._backend_connection, run_status, created_later_than, batch_id=batch_id
        )
        return [JobResult(r, self._backend_connection) for r in job_results["data"]]

    def _set_api_min_request_interval(self, min_request_interval: float) -> None:
        """Set the minimum request interval for the API. If consecutive requests are made
        within this interval, the SDK will automatically wait until the interval has passed
        before making the next request.

        :param min_request_interval: minimum request interval in seconds
        :return: None
        """
        if min_request_interval < 0.0:
            raise ValueError("Minimum request interval must be non-negative")
        self._backend_connection.min_request_interval = min_request_interval

    def _get_api_min_request_interval(self) -> float:
        """Get the minimum request interval for the API. See :func:`set_api_min_request_interval` for more details.

        :return: minimum request interval in seconds
        """
        return self._backend_connection.min_request_interval
