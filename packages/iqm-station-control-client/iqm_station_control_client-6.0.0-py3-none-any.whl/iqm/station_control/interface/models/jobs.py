# Copyright 2025 IQM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Job executor artifact and state models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
import functools
from uuid import UUID

from iqm.station_control.interface.pydantic_base import PydanticBase


class TimelineEntry(PydanticBase):
    """Status and timestamp pair as described in a job timeline."""

    status: JobStatus
    timestamp: datetime


class JobResult(PydanticBase):
    """Progress information about a running job."""

    job_id: UUID
    parallel_sweep_progress: list[tuple[str, int, int]]
    interrupted: bool


class JobError(PydanticBase):
    """Error log for a job."""

    full_error_log: str
    user_error_message: str


class JobData(PydanticBase):
    """Job response data model"""

    job_id: UUID
    job_status: JobStatus
    job_result: JobResult
    job_error: JobError | None
    position: int | None


@functools.total_ordering
class JobStatus(Enum):
    """Enumeration of different states a job can be in. The ordering of these statuses is important,
    and execution logic relies on it. Thus if a new status is added, ensure that it is slotted
    in at the appropriate place. See the __lt__ implementation for further details.
    """

    # Received by the server
    RECEIVED = "received"

    # Validating the job

    VALIDATION_STARTED = "validation_started"
    VALIDATION_ENDED = "validation_ended"

    FETCH_CALIBRATION_STARTED = "fetch_calibration_started"
    FETCH_CALIBRATION_ENDED = "fetch_calibration_ended"

    # Running PulLA
    COMPILATION_STARTED = "compilation_started"
    COMPILATION_ENDED = "compilation_ended"

    # Executing sweep
    SAVE_SWEEP_METADATA_STARTED = "save_sweep_metadata_started"
    SAVE_SWEEP_METADATA_ENDED = "save_sweep_metadata_ended"
    EXECUTION_PENDING = "execution_pending"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_ENDED = "execution_ended"
    EXECUTION_STAGE_COMPLETED = "execution_completed"

    # Extracting artifacts from results
    POST_PROCESSING_STARTED = "post_processing_started"
    POST_PROCESSING_ENDED = "post_processing_ended"

    READY = "ready"

    # Job failed, can happen at any stage
    FAILED = "failed"

    # Job aborted
    ABORTED = "aborted"

    def __str__(self):
        return self.name.lower()

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, str):
            try:
                other = JobStatus(other.lower())
            except ValueError:
                return False
        elif not isinstance(other, JobStatus):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other):
        """Enable comparison according to definition order.

        Examples:
            >>> JobStatus.VALIDATION_STARTED < JobStatus.COMPILATION_ENDED
            True

        """
        if isinstance(other, str):
            try:
                other = JobStatus(other.lower())
            except ValueError:
                return NotImplemented
        elif not isinstance(other, JobStatus):
            return NotImplemented
        members = list(JobStatus.__members__.values())
        return members.index(self) < members.index(other)

    @classmethod
    def terminal_statuses(cls) -> set[JobStatus]:
        """Statuses from which the execution can't continue."""
        return {cls.ABORTED, cls.FAILED, cls.READY}
