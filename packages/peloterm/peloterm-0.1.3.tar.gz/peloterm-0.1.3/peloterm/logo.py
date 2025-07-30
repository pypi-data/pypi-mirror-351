"""ASCII logo and branding for Peloterm."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def get_logo() -> str:
    """Return the ASCII logo for Peloterm."""
    return """
    ██████╗ ███████╗██╗      ██████╗ ████████╗███████╗██████╗ ███╗   ███╗
    ██╔══██╗██╔════╝██║     ██╔═══██╗╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
    ██████╔╝█████╗  ██║     ██║   ██║   ██║   █████╗  ██████╔╝██╔████╔██║
    ██╔═══╝ ██╔══╝  ██║     ██║   ██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
    ██║     ███████╗███████╗╚██████╔╝   ██║   ███████╗██║  ██║██║ ╚═╝ ██║
    ╚═╝     ╚══════╝╚══════╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
    """

def get_bike_art() -> str:
    """Return a simple bike ASCII art."""
    return """
                    🚴‍♂️
                   ___
                  /   \\
                 |  ○  |
                  \\___/
                    |
            ○━━━━━━━┿━━━━━━━○
           / \\      |      / \\
          /   \\     |     /   \\
         ○─────○    |    ○─────○
              / \\   |   / \\
             /   \\ / \\ /   \\
            ○─────○   ○─────○
    """

def get_compact_logo() -> str:
    """Return a compact version of the logo."""
    return """
    ╔═══════════════════════════════════════╗
    ║  🚴‍♂️ PELOTERM - Cycling Metrics     ║
    ║     Real-time • Recording • Strava    ║
    ╚═══════════════════════════════════════╝
    """

def get_banner() -> str:
    """Return a stylized banner for startup."""
    return """
    ╭───────────────────────────────────────────────────────────────────╮
    │                                                                   │
    │  ██████╗ ███████╗██╗      ██████╗ ████████╗███████╗██████╗ ███╗   ███╗  │
    │  ██╔══██╗██╔════╝██║     ██╔═══██╗╚══██╔══╝██╔════╝██╔══██╗████╗ ████║  │
    │  ██████╔╝█████╗  ██║     ██║   ██║   ██║   █████╗  ██████╔╝██╔████╔██║  │
    │  ██╔═══╝ ██╔══╝  ██║     ██║   ██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║  │
    │  ██║     ███████╗███████╗╚██████╔╝   ██║   ███████╗██║  ██║██║ ╚═╝ ██║  │
    │  ╚═╝     ╚══════╝╚══════╝ ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  │
    │                                                                   │
    │             🚴‍♂️ Real-time Cycling Metrics Visualization            │
    │                Power • Speed • Cadence • Heart Rate               │
    │                                                                   │
    ╰───────────────────────────────────────────────────────────────────╯
    """

def display_logo(console: Console = None, style: str = "banner") -> None:
    """Display the logo with rich formatting.
    
    Args:
        console: Rich console instance (creates new one if None)
        style: Logo style - "banner", "compact", "logo", or "bike"
    """
    if console is None:
        console = Console()
    
    if style == "banner":
        text = Text(get_banner())
        text.stylize("bold blue")
        console.print(text)
    elif style == "compact":
        console.print(Panel(get_compact_logo(), style="bold blue"))
    elif style == "logo":
        text = Text(get_logo())
        text.stylize("bold cyan")
        console.print(text)
    elif style == "bike":
        console.print(get_bike_art(), style="green")
    else:
        console.print("[red]Unknown logo style. Use: banner, compact, logo, or bike[/red]")

def get_version_banner(version: str) -> str:
    """Return a version banner."""
    return f"""
    ╭─────────────────────────────────────────╮
    │  🚴‍♂️ PELOTERM v{version:<26} │
    │     Cycling Metrics Visualization      │
    │                                         │
    │  ⚡ Power    🚴 Speed    🔄 Cadence     │
    │  💓 Heart Rate    📊 Real-time Charts   │
    │  🏁 FIT Recording    🌐 Strava Upload   │
    ╰─────────────────────────────────────────╯
    """

# Simple cycling-themed decorations
CYCLING_EMOJIS = ["🚴‍♂️", "🚴‍♀️", "🚵‍♂️", "🚵‍♀️", "⚡", "💓", "🔄", "📊", "🏁", "🌐"]
POWER_BAR = "█▓▒░"
GRADIENT_COLORS = ["red", "yellow", "green", "cyan", "blue", "magenta"]

def get_metric_separator() -> str:
    """Return a decorative separator for metrics."""
    return "─" * 60

def get_startup_animation_frames() -> list:
    """Return frames for a simple startup animation."""
    frames = [
        "🚴‍♂️ Starting Peloterm...",
        "🔍 Scanning for devices...", 
        "📡 Connecting sensors...",
        "⚡ Ready to ride!",
    ]
    return frames 