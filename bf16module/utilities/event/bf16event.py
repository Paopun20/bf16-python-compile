from typing import Callable

class BF16Event:
    def __init__(self):
        self.hook_event: list[dict[str, Callable]] = []
    
    def register_event(self, event_name: str, callback: Callable):
        """Register a callback for a named event."""
        self.hook_event.append({event_name: callback})

    def emit_event(self, event_name: str, *args, **kwargs):
        """Trigger all callbacks registered for an event."""
        for hook in self.hook_event:
            if event_name in hook:
                try:
                    hook[event_name](*args, **kwargs)
                except Exception as e:
                    print(f"[event error] {event_name}: {e}")