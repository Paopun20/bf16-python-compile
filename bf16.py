import os; os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1" # Bye
import sys, pygame, argparse, time

# rich
from rich.console import Console
from rich.traceback import install as rich_traceback_install
from rich.pretty import install as pretty_install
from rich.panel import Panel
from rich.status import Status
from rich.live import Live
from rich import box

# add-on rich
from rich_argparse import RichHelpFormatter

# bf16 core (don't remove)
from bf16module.utilities.colors.bf16color import BF16color
from bf16module.utilities.compile.bf16compile import BF16compile
from bf16module.runtime.bf16runtime import BF16Runtime

rich_traceback_install()
pretty_install()

console = Console()

WINDOW_SIZE = 512
PROGRAM_END = False

def main():
    """
    Main entry point for the BF16 Interpreter and Compiler command-line interface.
    This function sets up the argument parser, handles subcommands for compiling and running Brainfuck-based games,
    and manages runtime events and hooks. It supports debug mode, color modes, and displays runtime information.
    The function also initializes Pygame for graphical output when running programs.
    Subcommands:
        - compile: Compiles a .b source file to a .bf16c binary, with options for color mode, app name, and output file.
        - run: Runs a .b or .bf16c program, with options for color mode and FPS display.
    Arguments:
        --debug: Enables debug output.
        --color: Sets the color mode (default: rgb332).
        --showfps: Displays frames per second (run mode only).
        --use_v2_compile: Uses the v2 binary format for compilation (compile mode only).
        --appname: Sets the application name for the binary (compile mode only).
        -o, --output: Specifies the output filename for the compiled binary (compile mode only).
    Raises:
        FileNotFoundError: If the specified input file does not exist.
        ValueError: If an unsupported file type is provided.
        Exception: For errors during compilation or loading.
    Side Effects:
        - Prints status and error messages to the console.
        - Initializes and manages a Pygame window for graphical output.
        - Registers and emits runtime events for program execution.
    """
    parser = argparse.ArgumentParser(
        prog="bf16",
        description="""BF16 Interpreter and Compiler: Visual Brainfuck game runtime""",
        epilog="Examples:\n"
               "  bf16 compile game.b\n"
               "  bf16 run game.b --color rgb332 --showfps\n"
               "  bf16 run demo.bf16c --color grayscale",
        formatter_class=RichHelpFormatter
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_parser = subparsers.add_parser("compile", help="Compile a .b source file to .bf16c")
    compile_parser.add_argument("filename")
    compile_parser.add_argument("--use_v2_compile", action="store_true")
    compile_parser.add_argument("--color", default="rgb332")
    compile_parser.add_argument("--appname", default="UNNAMED BF16")
    compile_parser.add_argument("-o", "--output", help="Output filename (default: auto .bf16c)")

    run_parser = subparsers.add_parser("run", help="Run a .b or .bf16c program")
    run_parser.add_argument("filename")
    run_parser.add_argument("--color", default="rgb332")
    run_parser.add_argument("--showfps", action="store_true")

    with Status("Initializing BF16...", console=console, spinner="material"):
        console.clear()

        args = parser.parse_args()

        if args.debug:
            console.print("[bold blue]🛠 Debug mode enabled[/]")
            import logging
            logging.basicConfig(level=logging.DEBUG)

        compiler = BF16compile()
        runtime = BF16Runtime()
        time.sleep(0) # but why
        console.print("[green]✔ BF16 initialized[/]")

    with Status("Checking file, What I Got", console=console, spinner="material"):
        if not os.path.isfile(args.filename):
            console.print(f"[bold red]❌ File not found:[/] {args.filename}")
            return
        time.sleep(0) # but why
        console.print("[green]✔ File check done[/]")
    
    if args.command == "compile":
        with Status("Compiling...", console=console, spinner="material"):
            if not args.filename.endswith(".b"):
                console.print("[bold red]❌ Compile only supports .b files[/]")
                return
            try:
                with open(args.filename, "rb") as f:
                    source = f.read()
                compiler.compile(source)
                bin_filename = args.output or args.filename.rsplit(".", 1)[0] + ".bf16c"
                if args.use_v2_compile:
                    compiler.write_bin_v2(bin_filename, color_mode=args.color, app_name=args.appname)
                else:
                    compiler.write_bin(bin_filename)
                console.print(Panel.fit(
                    f"✅ Compiled [bold cyan]{args.filename}[/] → [green]{bin_filename}[/]",
                    title="Compile Success", box=box.ROUNDED, style="green"))
            except Exception as e:
                console.print(Panel(str(e), title="💥 Compile Failed", style="red"))
            return

    if args.command == "run":
        try:
            color = getattr(BF16color, args.color.lower())
            if not callable(color):
                raise AttributeError
        except AttributeError:
            available = [m for m in dir(BF16color) if not m.startswith("_")]
            console.print(f"[bold red]❌ Unknown color mode:[/] {args.color}")
            console.print(f"[yellow]Available modes:[/] {', '.join(available)}")
            color = BF16color.rgb332

        with Status("Initializing Pygame...", console=console, spinner="material"):
            pygame.init()
            pygame.display.set_caption("BF16 - Loading...")
            screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
            font = pygame.font.SysFont("Arial", 24)
            clock = pygame.time.Clock()

            text_surface = font.render("Loading...", True, (255, 255, 255))
            screen.blit(text_surface, text_surface.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2)))
            pygame.display.flip()
            
            time.sleep(0) # but why

            console.print("[green]✔ Pygame initialized[/]")
        
        with Status("Get Detail File, What I Got", console=console, spinner="material"):
            filename = args.filename
            ext = filename.lower()
            text_load = ""
            if ext.endswith((".b", ".bf16")):
                text_load = "Compiling source"
            elif ext.endswith((".bin", ".bf16c")):
                text_load = "Loading binary"

        with Status(text_load, console=console, spinner="material"):
            try:
                if ext.endswith((".b", ".bf16")):
                    console.print(f"🧠 [bold blue]Compiling source[/] '{filename}'")
                    with open(filename, "rb") as f:
                        runtime.program = compiler.compile(f.read())
                    pygame.display.set_caption(f"BF16 - {os.path.basename(filename)} | compile runtime")
                    console.print("[green]✔ Compilation done[/]")

                elif ext.endswith((".bin", ".bf16c")):
                    console.print(f"📦 [bold magenta]Loading binary[/] '{filename}'")
                    if compiler.is_v2_bin(filename):
                        runtime.program, color_mode, app_name = compiler.read_bin_v2(filename)
                        console.print("[green]✔ V2 BF16 binary loaded[/]")
                        console.print(f"📘 App: [green]{app_name}[/], Color: [cyan]{color_mode}[/]")
                        pygame.display.set_caption(f"BF16 - {app_name} | v2 compile runtime")
                        try:
                            color = getattr(BF16color, color_mode.lower())
                        except AttributeError:
                            color = BF16color.rgb332
                    else:
                        runtime.program = compiler.read_bin(filename)
                        console.print("[yellow]⚠ Old format binary loaded[/]")

                else:
                    raise ValueError(f"❌ Unsupported file type: {filename}")

            except Exception as e:
                console.print(Panel(str(e), title="💥 Load Error", style="red"))
                return
        
        def on_tick_hook():
            tol_memory = sum(x for x in runtime.memory) / 1024 / 1024 if hasattr(runtime, "memory") else 0
            console.log(f"[dim]Tick {runtime.tick} | memory usage: {tol_memory:.2f} MB[/]")

        def on_program_end_hook():
            global PROGRAM_END
            PROGRAM_END = True
            console.log(f"[bold green]✅ Program finished in {runtime.tick} ticks.[/]")

        runtime.register_event("program_end", on_program_end_hook)
        runtime.register_event("memory_address", lambda msg: console.log(f"[dim cyan]{msg}[/]"))

        if args.debug:
            with Status("Setup Debuger") as status:
                runtime.register_event("tick", on_tick_hook)
                
                runtime.register_event("debug.instruction", lambda msg: console.log(f"[dim blue]{msg}[/]"))
                runtime.register_event("debug.pointer", lambda msg: console.log(f"[dim yellow]{msg}[/]"))
                runtime.register_event("debug.memory", lambda msg: console.log(f"[dim green]{msg}[/]"))
                runtime.register_event("debug.jump", lambda msg: console.log(f"[dim purple]{msg}[/]"))
                runtime.register_event("debug.render", lambda msg: console.log(f"[dim cyan]{msg}[/]"))
                runtime.register_event("debug.input", lambda msg: console.log(f"[dim magenta]{msg}[/]"))
                runtime.register_event("debug.error", lambda msg: console.log(f"[bold red]{msg}[/]"))

                time.sleep(0) # but why
                console.print("Successfully setup debug")
    
        console.print("[green]" + "="*80 + "[/]")

        runtime.reset()
        running = True
        while running:
            if PROGRAM_END:
                running = False
                break
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            runtime.emit_event("tick")
            runtime.run_program_threaded(screen, color=color)

            if args.showfps:
                runtime.draw_fps(screen, clock)

            runtime.graphic_engine.update()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Program interrupted by user.[/]")
        sys.exit(0)
    except pygame.error as e:
        console.print(f"[bold red]💥 Pygame error:[/] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]💥 An unexpected error occurred:[/] {e}")
        sys.exit(1)
