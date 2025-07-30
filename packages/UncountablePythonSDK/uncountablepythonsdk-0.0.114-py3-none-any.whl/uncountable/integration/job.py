import functools
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pkgs.argument_parser import CachedParser
from uncountable.core.async_batch import AsyncBatchProcessor
from uncountable.core.client import Client
from uncountable.core.file_upload import FileUpload
from uncountable.integration.telemetry import JobLogger
from uncountable.types import base_t, entity_t, webhook_job_t
from uncountable.types.job_definition_t import JobDefinition, JobResult, ProfileMetadata


@dataclass(kw_only=True)
class JobArguments:
    job_definition: JobDefinition
    profile_metadata: ProfileMetadata
    client: Client
    batch_processor: AsyncBatchProcessor
    logger: JobLogger
    payload: base_t.JsonValue


# only for compatibility:
CronJobArguments = JobArguments


PT = typing.TypeVar("PT")


class Job[PT](ABC):
    _unc_job_registered: bool = False

    @property
    @abstractmethod
    def payload_type(self) -> type[PT]: ...

    @abstractmethod
    def run_outer(self, args: JobArguments) -> JobResult: ...

    @functools.cached_property
    def _cached_payload_parser(self) -> CachedParser[PT]:
        return CachedParser(self.payload_type)

    def get_payload(self, payload: base_t.JsonValue) -> PT:
        return self._cached_payload_parser.parse_storage(payload)


class CronJob(Job):
    @property
    def payload_type(self) -> type[None]:
        return type(None)

    def run_outer(self, args: JobArguments) -> JobResult:
        assert isinstance(args, CronJobArguments)
        return self.run(args)

    @abstractmethod
    def run(self, args: JobArguments) -> JobResult: ...


WPT = typing.TypeVar("WPT")


class WebhookJob[WPT](Job[webhook_job_t.WebhookEventPayload]):
    @property
    def payload_type(self) -> type[webhook_job_t.WebhookEventPayload]:
        return webhook_job_t.WebhookEventPayload

    @property
    @abstractmethod
    def webhook_payload_type(self) -> type[WPT]: ...

    def run_outer(self, args: JobArguments) -> JobResult:
        webhook_body = self.get_payload(args.payload)
        inner_payload = CachedParser(self.webhook_payload_type).parse_api(
            webhook_body.data
        )
        return self.run(args, inner_payload)

    @abstractmethod
    def run(self, args: JobArguments, payload: WPT) -> JobResult: ...


def register_job(cls: type[Job]) -> type[Job]:
    cls._unc_job_registered = True
    return cls


class RunsheetWebhookJob(WebhookJob[webhook_job_t.RunsheetWebhookPayload]):
    @property
    def webhook_payload_type(self) -> type:
        return webhook_job_t.RunsheetWebhookPayload

    @abstractmethod
    def build_runsheet(
        self,
        *,
        args: JobArguments,
        entities: list[entity_t.Entity],
    ) -> FileUpload: ...

    def run(
        self, args: JobArguments, payload: webhook_job_t.RunsheetWebhookPayload
    ) -> JobResult:
        runsheet = self.build_runsheet(args=args, entities=payload.entities)

        files = args.client.upload_files(file_uploads=[runsheet])
        args.client.complete_async_upload(
            async_job_id=payload.async_job_id, file_id=files[0].file_id
        )

        return JobResult(
            success=True,
        )
