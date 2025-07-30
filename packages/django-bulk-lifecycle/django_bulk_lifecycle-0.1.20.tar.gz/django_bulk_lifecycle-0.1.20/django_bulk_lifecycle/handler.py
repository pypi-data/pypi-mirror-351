from django_bulk_lifecycle.conditions import HookCondition
from django_bulk_lifecycle.registry import get_hooks, register_hook
import logging

logger = logging.getLogger(__name__)

class TriggerHandlerMeta(type):
    def __new__(mcs, name, bases, namespace):
        cls = super().__new__(mcs, name, bases, namespace)

        for method_name, method in namespace.items():
            if hasattr(method, "lifecycle_hook"):
                model_cls, event, condition, priority = method.lifecycle_hook
                register_hook(
                    model=model_cls,
                    event=event,
                    handler_cls=cls,
                    method_name=method_name,
                    condition=condition,
                    priority=priority,
                )
                logger.debug(
                    "Registered hook %s.%s → %s.%s (cond=%r, prio=%s)",
                    model_cls.__name__,
                    event,
                    cls.__name__,
                    method_name,
                    condition,
                    priority,
                )
        return cls

class TriggerHandler(metaclass=TriggerHandlerMeta):
    @classmethod
    def handle(
        cls,
        event: str,
        model: type,
        *,
        new_records: list = None,
        old_records: list = None,
        **kwargs,
    ) -> None:
        new_records = new_records or []
        # pad old_records with None so the zip has length
        old_records = (
            old_records
            if old_records is not None
            else [None] * len(new_records)
        )
        logger.debug(
            "ℹ️  bulk_lifecycle.handle() start: model=%s event=%s new_count=%d old_count=%d",
            model.__name__,
            event,
            len(new_records),
            len(old_records),
        )

        for handler_cls, method_name, condition, priority in get_hooks(model, event):
            logger.debug(
                "→ evaluating hook %s.%s (cond=%r, prio=%s)",
                handler_cls.__name__,
                method_name,
                condition,
                priority,
            )

            # --- condition check ---
            passed = True
            if condition is not None:
                if isinstance(condition, HookCondition):
                    checks = []
                    for new, old in zip(new_records, old_records):
                        result = condition.check(new, old)
                        checks.append(result)
                        logger.debug(
                            "   [cond-check] %s.%s → new=%r old=%r => %s",
                            handler_cls.__name__,
                            method_name,
                            new,
                            old,
                            result,
                        )
                    passed = any(checks)
                    logger.debug(
                        "   [cond-summary] %s.%s any-passed=%s",
                        handler_cls.__name__,
                        method_name,
                        passed,
                    )
                else:
                    passed = condition(new_records=new_records, old_records=old_records)
                    logger.debug(
                        "   [legacy-cond] %s.%s → full-list => %s",
                        handler_cls.__name__,
                        method_name,
                        passed,
                    )

            if not passed:
                logger.debug(
                    "↳ skipping %s.%s (condition not met)",
                    handler_cls.__name__,
                    method_name,
                )
                continue

            # instantiate & invoke
            handler = handler_cls()
            method = getattr(handler, method_name)
            logger.info(
                "✨ invoking %s.%s on %d record(s)",
                handler_cls.__name__,
                method_name,
                len(new_records),
            )
            try:
                method(new_records=new_records, old_records=old_records, **kwargs)
            except Exception:
                logger.exception(
                    "❌ exception in %s.%s",
                    handler_cls.__name__,
                    method_name,
                )

        logger.debug("✔️  bulk_lifecycle.handle() complete for %s.%s", model.__name__, event)
