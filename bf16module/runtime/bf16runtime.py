import pygame
import threading
from itertools import product
from typing import Callable

from bf16module.utilities.sound.bf16audio import BF16audio
from bf16module.utilities.input.bf16input import BF16input
from bf16module.graphic_engine.bf16graphic import BF16graphic

MEMORY_SIZE = 30000
PIXEL_SCALE = 512 // 16

class BF16Runtime:
    def __init__(self):
        self.graphic_engine = None
        self.program: list[int] = []
        self.memory: list[int] = [0] * MEMORY_SIZE
        self.display_image: list[list[int]] = [[0] * 16 for _ in range(16)]
        self.cursor = 0
        self.address = 0
        self.tick = 0
        self.current_note = 0
        self.last_key_state = 0
        self.hook_event: list[dict[str, Callable]] = []

    def reset(self):
        """Reset runtime memory and state."""
        self.memory = [0] * MEMORY_SIZE
        self.cursor = 0
        self.address = 0
        self.tick = 0
        self.current_note = 0
        self.last_key_state = 0

    def register_event(self, event_name: str, callback: Callable):
        """Register a callback for a named event."""
        self.hook_event.append({event_name: callback})

    def emit_event(self, event_name: str, *args, **kwargs):
        """Trigger all callbacks registered for an event in a separate thread."""

        def run_hooks():
            for hook in self.hook_event:
                if event_name in hook:
                    try:
                        threading.Thread(target=run_hooks).start()
                    except Exception as e:
                        print(f"[event error] {event_name}: {e}")

        run_hooks()
        # it delay
        # threading.Thread(target=run_hooks).start()
        

    def run_program(self, screen: pygame.Surface, color: Callable[[int], tuple[int, int, int]]):
        """Run a single frame of the program until next draw ('.') or end."""
    
        if self.cursor >= len(self.program):
            self.emit_event("program_end")
    
        if self.graphic_engine is None:
            self.graphic_engine = BF16graphic(screen)
        graphic_engine = self.graphic_engine
    
        while self.cursor < len(self.program):
            cmd = self.program[self.cursor]
            self.emit_event("debug.instruction", f"PC={self.cursor} CMD={chr(cmd)}")
            self.cursor += 1
    
            if cmd == ord('>'):
                arg = self.program[self.cursor]
                self.address += arg
                self.address = min(self.address, MEMORY_SIZE - 1)
                self.emit_event("debug.pointer", f"> Move right by {arg} → {self.address}")
                self.cursor += 1
    
            elif cmd == ord('<'):
                arg = self.program[self.cursor]
                self.address -= arg
                self.address = max(self.address, 0)
                self.emit_event("debug.pointer", f"< Move left by {arg} → {self.address}")
                self.cursor += 1
    
            elif cmd == ord('+'):
                arg = self.program[self.cursor]
                before = self.memory[self.address]
                self.memory[self.address] = (before + arg) % 256
                self.emit_event("debug.memory", f"+ Add {arg} → mem[{self.address}] {before} → {self.memory[self.address]}")
                self.cursor += 1
    
            elif cmd == ord('-'):
                arg = self.program[self.cursor]
                before = self.memory[self.address]
                self.memory[self.address] = (before - arg) % 256
                self.emit_event("debug.memory", f"- Subtract {arg} → mem[{self.address}] {before} → {self.memory[self.address]}")
                self.cursor += 1
    
            elif cmd == ord('['):
                offset = self.program[self.cursor]
                self.emit_event("debug.jump", f"[ Jump forward {offset} if mem[{self.address}] == 0")
                if self.memory[self.address] == 0:
                    self.cursor += offset
                self.cursor += 1
    
            elif cmd == ord(']'):
                offset = self.program[self.cursor]
                self.emit_event("debug.jump", f"] Jump back {offset} if mem[{self.address}] != 0")
                if self.memory[self.address] != 0:
                    self.cursor -= offset
                self.cursor += 1
    
            elif cmd == ord('.'):
                self.cursor += 1
                for i, j in product(range(16), repeat=2):
                    val = self.memory[i * 16 + j]
                    graphic_engine.draw_box(
                        x=j * PIXEL_SCALE,
                        y=i * PIXEL_SCALE,
                        width=PIXEL_SCALE,
                        height=PIXEL_SCALE,
                        color=color(val)
                    )
                    self.display_image[i][j] = val
                self.emit_event("debug.render", "Display frame updated")
                return
    
            elif cmd == ord(','):
                self.cursor += 1
                self.memory[self.address] = self.last_key_state = BF16input.get_key_state()
                self.emit_event("debug.input", f", Read key → {self.last_key_state}")
    
            elif cmd == ord('?'):
                self.cursor += 1
                # self.emit_event("debug.memory", f"? Inspect → mem[{self.address}] = {self.memory[self.address]}")
                self.emit_event("memory_address", f"memory[{self.address}] = {self.memory[self.address]}")
    
            else:
                self.emit_event("debug.error", f"Unknown instruction: '{chr(cmd)}'")
    
            self.tick += 1

    def run_program_threaded(self, screen: pygame.Surface, color: Callable[[int], tuple[int, int, int]]):
        """Run the program in a thread and update audio if needed."""
        thread = threading.Thread(target=self.run_program, args=(screen, color), daemon=True)
        thread.start()
        thread.join() # Wait for the program to finish its current instruction

        new_value = self.memory[self.address]
        if new_value != self.current_note:
            self.current_note = new_value
            BF16audio.play_note(self.current_note)

    def draw_fps(self, screen: pygame.Surface, clock: pygame.time.Clock):
        """Draw the current FPS on screen."""
        font = pygame.font.SysFont("Arial", 18)
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255), (0, 0, 0))
        screen.blit(fps_text, (10, 10))
