"""
Module for generating AWS Lambda handler code for EventBridge-based consumer triggers.

This module defines a generator class that creates handler code to process
EventBridge events, mapping them to use cases defined in the application.
"""
from typing import List, Optional, Tuple

from bisslog_schema.schema import TriggerConsumer
from bisslog_schema.schema.triggers.trigger_info import TriggerInfo

from .aws_handler_trigger_generator import AWSHandlerTriggerGenerator
from ...aws_handler_gen_response import AWSHandlerGenResponse


class ConsumerAWSEventBridgeHandlerGenerator(AWSHandlerTriggerGenerator):
    """
    Generates handler code for AWS EventBridge consumer triggers.

    This class inspects a list of trigger configurations and generates the
    corresponding Python code required to process EventBridge events.
    """

    main_conditional = 'if event.get("source") or event.get("detail-type") ' \
                       'or event.get("version") == "0":'
    name_standard_mapper = "mapper_consumer_event_bridge"

    def __call__(self, triggers: List[TriggerInfo],
                 uc_var_name: str) -> Optional[AWSHandlerGenResponse]:
        """
        Generates an AWS handler response object from given EventBridge consumer triggers.

        Parameters
        ----------
        triggers : List[TriggerInfo]
            A list of trigger configurations defined for the use case.
        uc_var_name : str
            The variable name used to call the use case implementation.

        Returns
        -------
        Optional[AWSHandlerGenResponse]
            A handler generation result with the build and handler code, or None if not applicable.
        """
        triggers_ok = [
            trigger for trigger in triggers
            if isinstance(trigger.options, TriggerConsumer)
        ]
        if not triggers_ok:
            return None

        is_single = len(triggers_ok) == 1
        depth = 1
        lines: List[Tuple[str, int]] = [(self.main_conditional, depth)]
        depth += 1

        pre_build_lines = [
            self.generate_mapper("mapper_consumer_event_bridge", {"detail": "event"})]
        lines.append(("response = []", depth))

        depth_before = depth
        for i, trigger in enumerate(triggers_ok):
            depth = depth_before
            keyname = trigger.keyname
            options = trigger.options
            lines.append(("mapped_standard_event = mapper_consumer_event_bridge.map(event)", depth))

            mapper_name = self.generate_mapper_name(trigger.type.val + "_event_bridge", keyname, i)
            conditional = f'if "{options.queue}" in event.get("source", ""):'

            if not is_single:
                lines.append((conditional, depth))
                depth += 1
            else:
                lines.append((self.comm(conditional), depth))

            if options.mapper:
                pre_build_lines.append(self.generate_mapper(mapper_name, options.mapper))
                lines.append(
                    (f"request_to_uc : dict = {mapper_name}.map(mapped_standard_event)", depth))
            else:
                lines.append(("request_to_uc = mapped_standard_event", depth))

            lines.append((f"uc_response = {uc_var_name}(**request_to_uc)", depth))
            lines.append(("response.append(uc_response)", depth))

        depth = depth_before
        lines.append(('return {"statusCode": 200, "body": response}', depth))

        return AWSHandlerGenResponse(
            self.join_with_depth(lines),
            "\n".join(pre_build_lines),
            {}
        )
