import logging
import typing as t

from apolo_app_types.helm.apps.base import BaseChartValueProcessor
from apolo_app_types.helm.apps.common import gen_extra_values
from apolo_app_types.protocols.superset import SupersetInputs


logger = logging.getLogger(__name__)


class SupersetChartValueProcessor(BaseChartValueProcessor[SupersetInputs]):
    async def gen_extra_values(
        self,
        input_: SupersetInputs,
        app_name: str,
        namespace: str,
        app_secrets_name: str,
        *_: t.Any,
        **kwargs: t.Any,
    ) -> dict[str, t.Any]:
        """Generate extra values for Weaviate configuration."""

        # Get base values
        values = await gen_extra_values(
            apolo_client=self.client,
            preset_type=input_.preset,
            ingress_http=input_.ingress_http,
            # ingress_grpc=input_.ingress_grpc,
            namespace=namespace,
        )

        logger.debug("Generated extra Weaviate values: %s", values)
        # TODO: add worker and Celery as well
        return {"supersetNode": values}
