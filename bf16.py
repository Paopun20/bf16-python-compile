import os; os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import sys, pygame, argparse, time, threading, json
import textwrap

# rich
from rich.console import Console
from rich.traceback import install as rich_traceback_install
from rich.pretty import install as pretty_install
from rich.panel import Panel
from rich.status import Status
from rich.table import Table
from rich import box

# add-on rich
from bf16module.utilities.CoolCustomRichFormatter import CoolCustomRichFormatter

# bf16 core (don't remove)
from bf16module.utilities.colors.bf16color import BF16color
from bf16module.utilities.compile.bf16compile import BF16compile
from bf16module.runtime.bf16runtime import BF16Runtime

rich_traceback_install()
pretty_install()

console = Console()

WINDOW_SIZE = 512
PROGRAM_END = False
debugger_server = None  # Global debugger server object

def main():
    parser = argparse.ArgumentParser(
        prog="bf16",
        description="""
        [bold blue]🧠 BF16 Interpreter & Compiler:[/]

        A visual [bold]Brainfuck-16[/] runtime that supports real-time graphics, sound, and input.
        Supports compiling `.b` to `.bf16c` with metadata, color mode, and other features.
        """,
        formatter_class=CoolCustomRichFormatter
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging and memory monitoring [bold underline red](Don't use, it not fully working yet. It's a work in progress!)[/]")

    subparsers = parser.add_subparsers(title="Available Commands", dest="command", metavar="<command>", required=True)

    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile .b source code to .bf16c binary",
        formatter_class=CoolCustomRichFormatter
    )
    compile_parser.add_argument("filename", help="Input .b file to compile")
    compile_parser.add_argument("--use_v2_compile", action="store_true", help="Use v2 binary format with metadata")
    compile_parser.add_argument("--color", default="rgb332", help="Color mode (default: rgb332)")
    compile_parser.add_argument("--appname", default="UNNAMED BF16", help="Application name for metadata")
    compile_parser.add_argument("-o", "--output", help="Output filename (.bf16c)")

    run_parser = subparsers.add_parser(
        "run",
        help="Run a .b or .bf16c program visually",
        formatter_class=CoolCustomRichFormatter
    )
    run_parser.add_argument("filename", help="Program file (.b or .bf16c)")
    run_parser.add_argument("--color", default="rgb332", help="Color mode (default: rgb332)")
    run_parser.add_argument("--showfps", action="store_true", help="Show FPS counter on screen")

    if len(sys.argv) == 1 or sys.argv[1] in ["-h", "--help"]:
        return parser.print_help()

    with Status("Initializing BF16...", console=console, spinner="material"):
        console.clear()

        args = parser.parse_args()

        if args.debug:
            global debugger_server
            console.print("[bold blue]🛠 Debug mode enabled[/]")
            import logging
            logging.basicConfig(level=logging.DEBUG)
            from bf16module.utilities.debugger.debugger import BF16Server
            debugger_server = BF16Server("127.0.0.1", 5000)
            threading.Thread(target=debugger_server.start, daemon=True).start()

        compiler = BF16compile()
        runtime = BF16Runtime()
        console.print("[green]✔ BF16 initialized[/]")

    with Status("Checking file, What I Got", console=console, spinner="material"):
        if not os.path.isfile(args.filename):
            console.print(f"[bold red]❌ File not found:[/] {args.filename}")
            return
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
            if not callable(color): raise AttributeError
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

            console.print("[green]✔ Pygame initialized[/]")

        with Status("Get Detail File, What I Got", console=console, spinner="material"):
            filename = args.filename
            ext = filename.lower()
            text_load = "Compiling source" if ext.endswith((".b", ".bf16")) else "Loading binary"

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
            
        def render_data(data):
            out = []
            for row in data:
                out_row = []
                for val in row:
                    out_row.append(int(val))
                out.append(out_row)
            return out

        def on_tick_hook():
            memory_mb = len(runtime.memory) * sys.getsizeof(int()) / 1024 / 1024
            console.log(f"[dim]Tick {runtime.tick} | memory usage: {memory_mb:.2f} MB[/]")
            if debugger_server:
                debugger_server.send_data_to_client(json.dumps({
                    "ID": f"render_{runtime.tick}",
                    "name": "render",
                    "data": render_data(runtime.display_image)
                }))

        def on_program_end_hook():
            global PROGRAM_END
            PROGRAM_END = True
            console.log(f"[bold green]✅ Program finished in {runtime.tick} ticks.[/]")
            if debugger_server:
                debugger_server.send_data_to_client(json.dumps({
                    "ID": f"program_end_{runtime.tick}",
                    "name": "program_end",
                    "data": "Program finished"
                }, indent=4))

        runtime.register_event("program_end", on_program_end_hook)
        runtime.register_event("memory_address", lambda msg: console.log(f"[dim cyan]{msg}[/]"))

        if args.debug:
            def data_format(name, data):
                return json.dumps({
                    "ID": f"{name}_{runtime.tick}",
                    "name": name,
                    "data": data
                }, indent=4)

            with Status("Setting up Debugger...", console=console, spinner="material"):
                console.print("[green]🐛 Debugger fully initialized[/]")
                console.print("Wait For Client For 10 Seconds...")
                if debugger_server:
                    if not debugger_server.wait_for_client(timeout=10):
                        console.print("[bold red]❌ Debugger client did not connect in time. Exiting.[/]")
                        return
                    else:
                        runtime.register_event("tick", on_tick_hook)
                        runtime.register_event("debug.instruction", lambda msg: debugger_server.send_data_to_client(data_format("instruction", msg)))
                        runtime.register_event("debug.pointer", lambda msg: debugger_server.send_data_to_client(data_format("pointer", msg)))
                        runtime.register_event("debug.memory", lambda msg: debugger_server.send_data_to_client(data_format("memory", msg)))
                        runtime.register_event("debug.jump", lambda msg: debugger_server.send_data_to_client(data_format("jump", msg)))
                        runtime.register_event("debug.render", lambda msg: debugger_server.send_data_to_client(data_format("render", msg)))
                        runtime.register_event("debug.input", lambda msg: debugger_server.send_data_to_client(data_format("input", msg)))

        console.print("[green]" + "="*80 + "[/]")

        runtime.reset()
        running = True
        while running:
            if PROGRAM_END:
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
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]👋 Program interrupted by user. Exiting gracefully.[/]\n")
    except Exception as e:
        console.print(Panel(str(e), title="💥 An unexpected error occurred", style="red"))
    finally:
        if debugger_server:
            debugger_server.stop()
        pygame.quit()
        sys.exit(1)