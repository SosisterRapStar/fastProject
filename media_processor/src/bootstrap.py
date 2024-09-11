from src.adapters.messagequeues import AsyncioConsumer, BaseProducer, RAW_COMMAND_HANDLERS, RAW_EVENT_HANDLERS
from src.adapters.s3client import S3ABC
from typing import Dict
import inspect

# some super simple DI
def bootstrap(s3: S3ABC, producer: BaseProducer) -> AsyncioConsumer:
    injects = {
        's3': s3(),
        'producer': producer()
    }
    injected_command_handlers = {}
    injected_event_handlers = {}

    for command, handler in RAW_COMMAND_HANDLERS.items():
        injected_object = inject(handler=handler, injects=injects)
        injected_command_handlers[command] = injected_object
    
    for event, handlers in RAW_EVENT_HANDLERS:
        injected_event_handlers[event] = [inject(handler=handler, injects=injects) for handler in handlers]
    
    message_bus = AsyncioConsumer(event_handlers=injected_event_handlers, command_handlers=injected_command_handlers)
    return message_bus




def inject(handler_class: object, injects: Dict[str, object]) -> object:
    init_signature = inspect.signature(handler_class.__init__)
    params = [param.name for param in init_signature.parameters.values() if param.name != 'self']
    values_for_object_creating = {key: inject[key] for key in injects if key in params}
    handler_object = handler_class(**values_for_object_creating)
    return handler_object