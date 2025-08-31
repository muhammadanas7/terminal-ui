#!/usr/bin/env python3
"""
Terminal UI Library - A comprehensive library for terminal-based user interfaces
Provides spinners, progress bars, animations, and visual effects for CLI applications.

Features:
- Multiple spinner styles with Unicode and ASCII patterns
- Progress bars with various themes and styles
- Animated text effects (typewriter, breathing, rainbow, glitch)
- Status indicators and notifications
- Theme support with color schemes
- Context managers for easy integration
- Thread-safe operations
- Performance monitoring

Usage:
    from terminal_ui import TerminalUI, SpinnerStyle, ProgressStyle, Theme
    
    ui = TerminalUI(theme='cyberpunk')
    
    # Simple spinner
    with ui.spinner("Loading data..."):
        time.sleep(2)
    
    # Progress bar
    with ui.progress("Processing files", total=100) as pbar:
        for i in range(100):
            time.sleep(0.01)
            pbar.update(1)
"""

import sys
import time
import random
import threading
import os
import math
import itertools
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import signal
import shutil

# Third-party imports (graceful degradation if not available)
try:
    from colorama import init, Fore, Back, Style
    COLORAMA_AVAILABLE = True
    init(autoreset=True)
except ImportError:
    # Fallback color constants
    class MockFore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
        LIGHTRED_EX = LIGHTGREEN_EX = LIGHTYELLOW_EX = ""
        LIGHTBLUE_EX = LIGHTMAGENTA_EX = LIGHTCYAN_EX = ""
        LIGHTWHITE_EX = LIGHTBLACK_EX = ""
    
    class MockBack:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
    
    class MockStyle:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""
    
    Fore, Back, Style = MockFore(), MockBack(), MockStyle()
    COLORAMA_AVAILABLE = False


class SpinnerStyle(Enum):
    """Predefined spinner animation styles"""
    # Basic ASCII patterns
    CLASSIC = ['|', '/', '-', '\\']
    DOTS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    DOTS2 = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    DOTS3 = ['⠄', '⠆', '⠇', '⠋', '⠙', '⠸', '⠰', '⠠', '⠰', '⠸', '⠙', '⠋', '⠇', '⠆']
    
    # Geometric patterns
    ARROW = ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙']
    TRIANGLE = ['▲', '▶', '▼', '◀']
    SQUARE = ['▖', '▘', '▝', '▗']
    CIRCLE = ['◐', '◓', '◑', '◒']
    QUARTER = ['◴', '◷', '◶', '◵']
    
    # Fancy Unicode patterns
    MOON = ['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']
    CLOCK = ['🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖', '🕗', '🕘', '🕙', '🕚', '🕛']
    HEARTS = ['🤍', '🤎', '❤️', '🧡', '💛', '💚', '💙', '💜']
    
    # Block patterns  
    BLOCKS = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▁']
    BOUNCE = ['⠁', '⠂', '⠄', '⠂']
    SNAKE = ['⣀', '⣄', '⣤', '⣦', '⣶', '⣷', '⣿', '⢿', '⡿', '⠿', '⢻', '⣛', '⣋', '⣍', '⡋', '⠋', '⠙', '⠹', '⢸', '⣸', '⣴', '⣤', '⣄', '⣀']
    
    # Text-based patterns
    BINARY = ['0', '1']
    DNA = ['⠋', '⠙', '⠸', '⠴', '⠦', '⠇', '⠏', '⠋']
    PULSE = ['●', '◐', '○', '◑']
    
    # Matrix-style
    MATRIX = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;:,./<>?")
    
    # Weather
    WEATHER = ['☀️', '⛅', '☁️', '🌧️', '⛈️', '🌦️', '🌈']


class ProgressStyle(Enum):
    """Progress bar styles"""
    BLOCKS = ('█', '░')
    BLOCKS2 = ('▰', '▱')
    ARROWS = ('>', '-')
    EQUALS = ('=', ' ')
    DOTS = ('●', '○')
    PIPES = ('|', ' ')
    SQUARES = ('■', '□')
    CIRCLES = ('●', '○')
    DIAMONDS = ('♦', '♢')
    GRADIENT = ('█', '▓', '▒', '░')


class NotificationLevel(Enum):
    """Notification levels"""
    INFO = "info"
    SUCCESS = "success"  
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Theme(Enum):
    """Predefined color themes"""
    DEFAULT = "default"
    MATRIX = "matrix"
    CYBERPUNK = "cyberpunk"
    RETRO = "retro"
    MINIMAL = "minimal"
    OCEAN = "ocean"
    SUNSET = "sunset"
    NEON = "neon"


@dataclass
class TerminalSize:
    """Terminal size information"""
    width: int
    height: int


@dataclass 
class AnimationConfig:
    """Animation configuration"""
    duration: float = 1.0
    fps: int = 10
    repeat: int = 1
    reverse: bool = False


class TerminalUI:
    """Main Terminal UI class providing comprehensive terminal interface capabilities"""
    
    # Color themes
    THEMES = {
        'default': {
            'primary': Fore.WHITE,
            'secondary': Fore.CYAN,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'critical': Fore.RED + Style.BRIGHT,
            'info': Fore.BLUE,
            'accent': Fore.MAGENTA,
            'muted': Fore.LIGHTBLACK_EX,
            'highlight': Style.BRIGHT,
        },
        'matrix': {
            'primary': Fore.GREEN,
            'secondary': Fore.LIGHTGREEN_EX,
            'success': Fore.GREEN + Style.BRIGHT,
            'warning': Fore.YELLOW + Style.DIM,
            'error': Fore.RED + Back.BLACK,
            'critical': Fore.RED + Style.BRIGHT + Back.BLACK,
            'info': Fore.GREEN + Style.DIM,
            'accent': Fore.LIGHTGREEN_EX,
            'muted': Fore.LIGHTBLACK_EX,
            'highlight': Fore.GREEN + Style.BRIGHT,
        },
        'cyberpunk': {
            'primary': Fore.LIGHTCYAN_EX,
            'secondary': Fore.LIGHTMAGENTA_EX,
            'success': Fore.LIGHTGREEN_EX,
            'warning': Fore.LIGHTYELLOW_EX,
            'error': Fore.RED + Back.YELLOW,
            'critical': Fore.LIGHTRED_EX + Style.BRIGHT,
            'info': Fore.LIGHTBLUE_EX,
            'accent': Fore.LIGHTRED_EX,
            'muted': Fore.LIGHTBLACK_EX,
            'highlight': Fore.LIGHTCYAN_EX + Style.BRIGHT,
        },
        'retro': {
            'primary': Fore.YELLOW,
            'secondary': Fore.CYAN,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'critical': Fore.RED + Style.BRIGHT,
            'info': Fore.BLUE,
            'accent': Fore.MAGENTA,
            'muted': Fore.LIGHTBLACK_EX,
            'highlight': Fore.YELLOW + Style.BRIGHT,
        },
        'minimal': {
            'primary': Fore.WHITE,
            'secondary': Fore.WHITE,
            'success': Fore.WHITE,
            'warning': Fore.WHITE,
            'error': Fore.RED,
            'critical': Fore.RED,
            'info': Fore.LIGHTBLACK_EX,
            'accent': Fore.WHITE,
            'muted': Fore.LIGHTBLACK_EX,
            'highlight': Style.BRIGHT,
        },
        'ocean': {
            'primary': Fore.CYAN,
            'secondary': Fore.BLUE,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'critical': Fore.RED + Style.BRIGHT,
            'info': Fore.LIGHTBLUE_EX,
            'accent': Fore.LIGHTCYAN_EX,
            'muted': Fore.LIGHTBLACK_EX,
            'highlight': Fore.CYAN + Style.BRIGHT,
        },
        'sunset': {
            'primary': Fore.LIGHTYELLOW_EX,
            'secondary': Fore.LIGHTRED_EX,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'critical': Fore.RED + Style.BRIGHT,
            'info': Fore.LIGHTMAGENTA_EX,
            'accent': Fore.LIGHTYELLOW_EX,
            'muted': Fore.LIGHTBLACK_EX,
            'highlight': Fore.LIGHTYELLOW_EX + Style.BRIGHT,
        },
        'neon': {
            'primary': Fore.LIGHTMAGENTA_EX,
            'secondary': Fore.LIGHTCYAN_EX,
            'success': Fore.LIGHTGREEN_EX,
            'warning': Fore.LIGHTYELLOW_EX,
            'error': Fore.LIGHTRED_EX,
            'critical': Fore.LIGHTRED_EX + Style.BRIGHT,
            'info': Fore.LIGHTBLUE_EX,
            'accent': Fore.LIGHTMAGENTA_EX,
            'muted': Fore.LIGHTBLACK_EX,
            'highlight': Fore.LIGHTMAGENTA_EX + Style.BRIGHT,
        },
    }
    
    def __init__(self, theme: Union[str, Theme] = 'default', speed_factor: float = 1.0, 
                 debug: bool = False, width: Optional[int] = None):
        """Initialize TerminalUI with theme and configuration"""
        self.theme_name = theme.value if isinstance(theme, Theme) else theme
        self.theme = self.THEMES.get(self.theme_name, self.THEMES['default'])
        self.speed_factor = max(0.1, speed_factor)
        self.debug = debug
        self.terminal_size = self._get_terminal_size()
        self.width = width or self.terminal_size.width
        self._lock = threading.Lock()
        self._active_spinners = []
        self._setup_signal_handlers()
    
    def _get_terminal_size(self) -> TerminalSize:
        """Get current terminal size"""
        try:
            size = shutil.get_terminal_size()
            return TerminalSize(size.columns, size.lines)
        except:
            return TerminalSize(80, 24)  # Fallback
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self._cleanup()
            sys.exit(0)
        
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except:
            pass  # Ignore if signals not available
    
    def _cleanup(self):
        """Cleanup active spinners and restore cursor"""
        for spinner in self._active_spinners:
            spinner._stop()
        self.show_cursor()
    
    def hide_cursor(self):
        """Hide terminal cursor"""
        if not self.debug:
            sys.stdout.write('\033[?25l')
            sys.stdout.flush()
    
    def show_cursor(self):
        """Show terminal cursor"""
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
    
    def clear_line(self):
        """Clear current line"""
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()
    
    def move_up(self, lines: int = 1):
        """Move cursor up"""
        sys.stdout.write(f'\033[{lines}A')
        sys.stdout.flush()
    
    def timestamp(self) -> str:
        """Get formatted timestamp"""
        return f"[{datetime.now().strftime('%H:%M:%S')}]"
    
    def colorize(self, text: str, color_key: str) -> str:
        """Apply theme color to text"""
        color = self.theme.get(color_key, self.theme['primary'])
        return f"{color}{text}{Style.RESET_ALL}"
    
    # === TYPING EFFECTS ===
    
    def typewriter_effect(self, text: str, delay: float = 0.05, 
                         color_key: str = 'primary', newline: bool = True):
        """Display text with typewriter effect"""
        delay /= self.speed_factor
        color = self.theme.get(color_key, self.theme['primary'])
        
        for char in text:
            char_delay = delay + random.uniform(-0.01, 0.01)
            if char in ".,!?;:":
                char_delay *= 2
            elif char == ' ':
                char_delay *= 0.5
            
            sys.stdout.write(f"{color}{char}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(char_delay)
        
        if newline:
            print()
    
    def glitch_effect(self, text: str, intensity: int = 1, duration: float = 0.5):
        """Apply glitch effect to text"""
        glitch_chars = "░▒▓█▄▀▐▌"
        iterations = int(duration * 10 / self.speed_factor)
        
        for _ in range(intensity):
            for _ in range(iterations):
                corrupted = ""
                for char in text:
                    if random.random() < 0.1 * intensity:
                        corrupted += random.choice(glitch_chars)
                    else:
                        corrupted += char
                
                sys.stdout.write(f"\r{self.theme['error']}{corrupted}{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(0.05 / self.speed_factor)
        
        # Show original text
        sys.stdout.write(f"\r{self.theme['primary']}{text}{Style.RESET_ALL}\n")
    
    def rainbow_text(self, text: str):
        """Display text with rainbow colors"""
        colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
        
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            sys.stdout.write(f"{color}{char}{Style.RESET_ALL}")
        print()
    
    def breathing_animation(self, text: str, cycles: int = 3, duration: float = 2.0):
        """Breathing text animation"""
        duration /= self.speed_factor
        cycle_duration = duration / cycles
        
        for cycle in range(cycles):
            # Breathe in (fade in)
            for brightness in [Style.DIM, Style.NORMAL, Style.BRIGHT]:
                self.clear_line()
                sys.stdout.write(f"{self.theme['accent']}{brightness}{text}{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(cycle_duration / 6)
            
            # Breathe out (fade out)
            for brightness in [Style.BRIGHT, Style.NORMAL, Style.DIM]:
                self.clear_line()
                sys.stdout.write(f"{self.theme['accent']}{brightness}{text}{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(cycle_duration / 6)
        
        self.clear_line()
        print(f"{self.theme['accent']}{text}{Style.RESET_ALL}")
    
    def wave_text(self, text: str, duration: float = 2.0):
        """Wave animation effect"""
        duration /= self.speed_factor
        frames = int(duration * 10)
        
        for frame in range(frames):
            wave_text = ""
            for i, char in enumerate(text):
                # Create wave effect with different intensities
                wave_pos = math.sin((i + frame * 0.5) * 0.5) * 0.5 + 0.5
                if wave_pos > 0.7:
                    wave_text += f"{Style.BRIGHT}{char}"
                elif wave_pos > 0.4:
                    wave_text += f"{Style.NORMAL}{char}"
                else:
                    wave_text += f"{Style.DIM}{char}"
            
            self.clear_line()
            sys.stdout.write(f"{self.theme['accent']}{wave_text}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1 / self.speed_factor)
        
        self.clear_line()
        print(f"{self.theme['primary']}{text}{Style.RESET_ALL}")
    
    # === SPINNERS ===
    
    @contextmanager
    def spinner(self, message: str = "Loading...", style: SpinnerStyle = SpinnerStyle.DOTS,
                color_key: str = 'accent', suffix: str = ""):
        """Context manager for spinner animation"""
        spinner_obj = Spinner(self, message, style, color_key, suffix)
        self._active_spinners.append(spinner_obj)
        
        try:
            spinner_obj.start()
            yield spinner_obj
        finally:
            spinner_obj.stop()
            self._active_spinners.remove(spinner_obj)
    
    def simple_spinner(self, message: str, duration: float, 
                      style: SpinnerStyle = SpinnerStyle.DOTS,
                      color_key: str = 'accent'):
        """Simple spinner for fixed duration"""
        with self.spinner(message, style, color_key):
            time.sleep(duration)
    
    # === PROGRESS BARS ===
    
    @contextmanager
    def progress(self, message: str = "Progress", total: int = 100,
                style: ProgressStyle = ProgressStyle.BLOCKS, 
                width: Optional[int] = None, show_percentage: bool = True,
                show_eta: bool = True, color_key: str = 'accent'):
        """Context manager for progress bar"""
        pbar = ProgressBar(self, message, total, style, width, 
                          show_percentage, show_eta, color_key)
        try:
            yield pbar
        finally:
            pbar.finish()
    
    def simple_progress(self, message: str, total: int = 100, 
                       style: ProgressStyle = ProgressStyle.BLOCKS,
                       duration: float = 2.0):
        """Simple progress bar simulation"""
        with self.progress(message, total, style) as pbar:
            for i in range(total):
                time.sleep(duration / total)
                pbar.update(1)
    
    # === NOTIFICATIONS ===
    
    def notify(self, message: str, level: NotificationLevel = NotificationLevel.INFO,
              timestamp: bool = True, prefix: str = ""):
        """Display notification message"""
        color_map = {
            NotificationLevel.INFO: 'info',
            NotificationLevel.SUCCESS: 'success',
            NotificationLevel.WARNING: 'warning',
            NotificationLevel.ERROR: 'error',
            NotificationLevel.CRITICAL: 'critical'
        }
        
        icon_map = {
            NotificationLevel.INFO: "ℹ",
            NotificationLevel.SUCCESS: "✓",
            NotificationLevel.WARNING: "⚠",
            NotificationLevel.ERROR: "✗",
            NotificationLevel.CRITICAL: "💀"
        }
        
        color_key = color_map[level]
        icon = icon_map[level]
        
        parts = []
        if timestamp:
            parts.append(self.colorize(self.timestamp(), 'muted'))
        if prefix:
            parts.append(self.colorize(f"[{prefix}]", 'muted'))
        
        parts.append(self.colorize(icon, color_key))
        parts.append(self.colorize(message, color_key))
        
        print(" ".join(parts))
    
    def success(self, message: str, **kwargs):
        """Success notification"""
        self.notify(message, NotificationLevel.SUCCESS, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Warning notification"""
        self.notify(message, NotificationLevel.WARNING, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Error notification"""
        self.notify(message, NotificationLevel.ERROR, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Critical notification"""
        self.notify(message, NotificationLevel.CRITICAL, **kwargs)
        
    def info(self, message: str, **kwargs):
        """Info notification"""
        self.notify(message, NotificationLevel.INFO, **kwargs)
    
    # === VISUAL ELEMENTS ===
    
    def separator(self, char: str = "─", width: Optional[int] = None, 
                 color_key: str = 'muted'):
        """Print a separator line"""
        width = width or self.width
        line = char * width
        print(self.colorize(line, color_key))
    
    def header(self, title: str, subtitle: str = "", 
              char: str = "═", color_key: str = 'primary'):
        """Display a header with title"""
        width = self.width
        
        # Top border
        print(self.colorize(char * width, color_key))
        
        # Title
        title_line = f" {title} ".center(width)
        print(self.colorize(title_line, color_key))
        
        # Subtitle if provided
        if subtitle:
            subtitle_line = f" {subtitle} ".center(width)
            print(self.colorize(subtitle_line, 'secondary'))
        
        # Bottom border
        print(self.colorize(char * width, color_key))
    
    def box(self, content: List[str], title: str = "", 
           border_style: str = "single", color_key: str = 'primary'):
        """Draw a box around content"""
        borders = {
            "single": ("┌", "┐", "└", "┘", "─", "│"),
            "double": ("╔", "╗", "╚", "╝", "═", "║"),
            "rounded": ("╭", "╮", "╰", "╯", "─", "│"),
            "thick": ("┏", "┓", "┗", "┛", "━", "┃"),
        }
        
        tl, tr, bl, br, h, v = borders.get(border_style, borders["single"])
        
        # Calculate box width
        max_content_width = max(len(line) for line in content) if content else 0
        title_width = len(title) if title else 0
        box_width = max(max_content_width, title_width) + 4
        
        # Top border with title
        if title:
            title_line = f"{tl}{h}{h} {title} {h * (box_width - len(title) - 6)}{tr}"
        else:
            title_line = f"{tl}{h * (box_width - 2)}{tr}"
        
        print(self.colorize(title_line, color_key))
        
        # Content lines
        for line in content:
            padded_line = f"{v} {line:<{box_width-4}} {v}"
            print(self.colorize(padded_line, color_key))
        
        # Bottom border
        bottom_line = f"{bl}{h * (box_width - 2)}{br}"
        print(self.colorize(bottom_line, color_key))
    
    def table(self, headers: List[str], rows: List[List[str]], 
             title: str = "", color_key: str = 'primary'):
        """Display a simple table"""
        if not headers or not rows:
            return
        
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Table width
        table_width = sum(col_widths) + (len(headers) - 1) * 3 + 4
        
        # Title
        if title:
            print(self.colorize(title.center(table_width), color_key))
            self.separator("─", table_width, 'muted')
        
        # Header
        header_line = "│ " + " │ ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " │"
        print(self.colorize(header_line, color_key))
        
        # Separator
        sep_line = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        print(self.colorize(sep_line, 'muted'))
        
        # Rows
        for row in rows:
            padded_row = [str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)]
            row_line = "│ " + " │ ".join(padded_row) + " │"
            print(self.colorize(row_line, 'primary'))
        
        # Bottom border
        bottom_line = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
        print(self.colorize(bottom_line, 'muted'))
    
    # === PERFORMANCE MONITORING ===
    
    @contextmanager
    def monitor_performance(self, operation: str):
        """Monitor and display performance metrics"""
        start_time = time.time()
        self.info(f"Starting {operation}...")
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.success(f"{operation} completed in {duration:.3f}s")


class Spinner:
    """Spinner animation class"""
    
    def __init__(self, ui: TerminalUI, message: str, style: SpinnerStyle,
                 color_key: str, suffix: str):
        self.ui = ui
        self.message = message
        self.style = style
        self.color_key = color_key
        self.suffix = suffix
        self.running = False
        self.thread = None
        self.frames = style.value if isinstance(style.value, list) else [style.value]
    
    def start(self):
        """Start spinner animation"""
        if self.running:
            return
        
        self.running = True
        self.ui.hide_cursor()
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop spinner animation"""
        self._stop()
    
    def _stop(self):
        """Internal stop method"""
        if not self.running:
            return
        
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.1)
        
        self.ui.clear_line()
        self.ui.show_cursor()
    
    def _animate(self):
        """Animation loop"""
        frame_index = 0
        
        while self.running:
            if self.style == SpinnerStyle.MATRIX:
                # Special handling for matrix style
                frame = random.choice(self.frames)
            else:
                frame = self.frames[frame_index % len(self.frames)]
            
            # Build output line
            color = self.ui.theme.get(self.color_key, self.ui.theme['primary'])
            output = f"{color}{frame} {self.message}{self.suffix}{Style.RESET_ALL}"
            
            self.ui.clear_line()
            sys.stdout.write(output)
            sys.stdout.flush()
            
            time.sleep(0.1 / self.ui.speed_factor)
            frame_index += 1
    
    def update_message(self, message: str):
        """Update spinner message"""
        self.message = message
    
    def update_suffix(self, suffix: str):
        """Update spinner suffix"""
        self.suffix = suffix


class ProgressBar:
    """Progress bar class"""
    
    def __init__(self, ui: TerminalUI, message: str, total: int, 
                 style: ProgressStyle, width: Optional[int], 
                 show_percentage: bool, show_eta: bool, color_key: str):
        self.ui = ui
        self.message = message
        self.total = total
        self.style = style
        self.width = width or min(40, ui.width - 30)
        self.show_percentage = show_percentage
        self.show_eta = show_eta
        self.color_key = color_key
        
        self.current = 0
        self.start_time = time.time()
        self.last_update = self.start_time
        
    def update(self, amount: int = 1):
        """Update progress"""
        self.current = min(self.current + amount, self.total)
        current_time = time.time()
        
        # Throttle updates to avoid flicker
        if current_time - self.last_update < 0.05 and self.current < self.total:
            return
        
        self.last_update = current_time
        self._render()
    
    def set_progress(self, current: int):
        """Set absolute progress"""
        self.current = min(max(0, current), self.total)
        self._render()
    
    def finish(self):
        """Complete the progress bar"""
        self.current = self.total
        self._render()
        print()  # Move to next line
    
    def _render(self):
        """Render the progress bar"""
        if self.total == 0:
            percentage = 100
        else:
            percentage = int((self.current / self.total) * 100)
        
        # Calculate filled portion
        filled_width = int((self.current / self.total) * self.width) if self.total > 0 else 0
        
        # Get style characters
        if self.style == ProgressStyle.GRADIENT:
            fill_char, empty1, empty2, empty3 = self.style.value
            filled = fill_char * filled_width
            empty = empty3 * (self.width - filled_width)
        else:
            fill_char, empty_char = self.style.value
            filled = fill_char * filled_width
            empty = empty_char * (self.width - filled_width)
        
        # Build progress bar
        color = self.ui.theme.get(self.color_key, self.ui.theme['primary'])
        success_color = self.ui.theme['success']
        bar_color = success_color if self.current == self.total else color
        
        bar = f"[{bar_color}{filled}{empty}{Style.RESET_ALL}]"
        
        # Build complete line
        parts = [self.message + ":", bar]
        
        if self.show_percentage:
            parts.append(f"{percentage:3d}%")
        
        if self.show_eta and self.current > 0:
            elapsed = time.time() - self.start_time
            if self.current < self.total:
                eta = (elapsed / self.current) * (self.total - self.current)
                parts.append(f"ETA: {eta:.1f}s")
            else:
                parts.append(f"Done in {elapsed:.1f}s")
        
        # Progress info
        parts.append(f"({self.current}/{self.total})")
        
        line = " ".join(parts)
        self.ui.clear_line()
        sys.stdout.write(line)
        sys.stdout.flush()


class MultiProgress:
    """Multiple progress bars manager"""
    
    def __init__(self, ui: TerminalUI):
        self.ui = ui
        self.progress_bars = {}
        self.lock = threading.Lock()
    
    def add_progress(self, name: str, message: str, total: int, 
                    style: ProgressStyle = ProgressStyle.BLOCKS, **kwargs) -> 'ManagedProgressBar':
        """Add a new progress bar"""
        with self.lock:
            pbar = ManagedProgressBar(self.ui, name, message, total, style, **kwargs)
            self.progress_bars[name] = pbar
            return pbar
    
    def remove_progress(self, name: str):
        """Remove a progress bar"""
        with self.lock:
            if name in self.progress_bars:
                del self.progress_bars[name]
    
    def render_all(self):
        """Render all progress bars"""
        with self.lock:
            # Clear all lines
            for _ in range(len(self.progress_bars)):
                self.ui.move_up(1)
                self.ui.clear_line()
            
            # Render each progress bar
            for pbar in self.progress_bars.values():
                pbar._render()
                print()


class ManagedProgressBar(ProgressBar):
    """Progress bar managed by MultiProgress"""
    
    def __init__(self, ui: TerminalUI, name: str, *args, **kwargs):
        super().__init__(ui, *args, **kwargs)
        self.name = name


# === ADVANCED ANIMATIONS ===

class MatrixRain:
    """Matrix-style digital rain animation"""
    
    def __init__(self, ui: TerminalUI, duration: float = 5.0, 
                 density: float = 0.1, color_key: str = 'primary'):
        self.ui = ui
        self.duration = duration
        self.density = density
        self.color_key = color_key
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;:,./<>?"
        
    def run(self):
        """Run the matrix rain animation"""
        width = self.ui.width
        height = self.ui.terminal_size.height - 2
        
        # Initialize columns
        columns = []
        for _ in range(width):
            if random.random() < self.density:
                columns.append({
                    'chars': [random.choice(self.chars) for _ in range(height)],
                    'y': random.randint(0, height),
                    'speed': random.uniform(0.5, 2.0)
                })
            else:
                columns.append(None)
        
        self.ui.hide_cursor()
        start_time = time.time()
        
        try:
            while time.time() - start_time < self.duration / self.ui.speed_factor:
                # Clear screen
                sys.stdout.write('\033[2J\033[H')
                
                # Update and render columns
                for x, column in enumerate(columns):
                    if column is None:
                        continue
                    
                    # Update position
                    column['y'] += column['speed'] / self.ui.speed_factor
                    
                    # Render column
                    for y in range(height):
                        char_y = int(column['y'] - y)
                        if 0 <= char_y < len(column['chars']):
                            char = column['chars'][char_y]
                            
                            # Brightness based on position
                            if y == 0:
                                brightness = Style.BRIGHT
                            elif y < 3:
                                brightness = Style.NORMAL
                            else:
                                brightness = Style.DIM
                            
                            color = self.ui.theme.get(self.color_key, self.ui.theme['primary'])
                            sys.stdout.write(f'\033[{y+1};{x+1}H{color}{brightness}{char}{Style.RESET_ALL}')
                    
                    # Reset column when off screen
                    if column['y'] > height + len(column['chars']):
                        columns[x] = {
                            'chars': [random.choice(self.chars) for _ in range(height)],
                            'y': -random.randint(5, 15),
                            'speed': random.uniform(0.5, 2.0)
                        } if random.random() < self.density else None
                
                sys.stdout.flush()
                time.sleep(0.1 / self.ui.speed_factor)
        
        finally:
            self.ui.show_cursor()
            sys.stdout.write('\033[2J\033[H')  # Clear screen


class FireEffect:
    """Terminal fire effect animation"""
    
    def __init__(self, ui: TerminalUI, duration: float = 3.0, height: int = 10):
        self.ui = ui
        self.duration = duration
        self.height = height
        self.width = ui.width
        self.fire_chars = [' ', '.', ':', '^', '*', 'x', 's', 'S', '#', ']
        self.colors = [Fore.RED, Fore.YELLOW, Fore.LIGHTYELLOW_EX, Fore.WHITE]
    
    def run(self):
        """Run the fire effect"""
        # Initialize fire buffer
        fire = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Set bottom row to maximum heat
        for x in range(self.width):
            fire[self.height-1][x] = len(self.fire_chars) - 1
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < self.duration / self.ui.speed_factor:
                # Update fire
                for y in range(self.height - 1):
                    for x in range(self.width):
                        # Calculate new heat value
                        heat = 0
                        count = 0
                        
                        # Sample surrounding cells
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                ny, nx = y + dy, x + dx
                                if 0 <= ny < self.height and 0 <= nx < self.width:
                                    heat += fire[ny][nx]
                                    count += 1
                        
                        # Apply cooling and randomness
                        new_heat = max(0, (heat // count) - random.randint(0, 2))
                        fire[y][x] = new_heat
                
                # Render fire
                output = ""
                for y in range(self.height):
                    line = ""
                    for x in range(self.width):
                        heat = fire[y][x]
                        char_index = min(heat, len(self.fire_chars) - 1)
                        char = self.fire_chars[char_index]
                        
                        # Choose color based on heat
                        if heat > 7:
                            color = self.colors[3]  # White
                        elif heat > 5:
                            color = self.colors[2]  # Light yellow
                        elif heat > 3:
                            color = self.colors[1]  # Yellow
                        elif heat > 0:
                            color = self.colors[0]  # Red
                        else:
                            color = ""
                        
                        line += f"{color}{char}{Style.RESET_ALL}"
                    
                    output += line + "\n"
                
                # Display
                sys.stdout.write('\033[H' + output)
                sys.stdout.flush()
                time.sleep(0.1 / self.ui.speed_factor)
                
        finally:
            sys.stdout.write('\033[2J\033[H')  # Clear screen


# === UTILITY FUNCTIONS ===

def demo_all_features():
    """Demonstrate all terminal UI features"""
    ui = TerminalUI(theme='cyberpunk', speed_factor=2.0)
    
    # Header
    ui.header("Terminal UI Library Demo", "Comprehensive CLI Interface")
    
    # Notifications
    ui.info("Starting demonstration...")
    ui.success("Library loaded successfully!")
    ui.warning("This is a warning message")
    ui.error("This is an error message")
    
    ui.separator()
    
    # Text effects
    ui.typewriter_effect("This is typewriter effect text...", color_key='accent')
    ui.breathing_animation("Breathing animation text", cycles=2)
    ui.rainbow_text("Rainbow colored text!")
    ui.glitch_effect("Glitch effect text", intensity=2)
    ui.wave_text("Wave animation text")
    
    ui.separator()
    
    # Spinners
    with ui.spinner("Loading data", SpinnerStyle.DOTS, suffix=" (25%)"):
        time.sleep(1)
    
    with ui.spinner("Processing", SpinnerStyle.SNAKE, suffix=" (50%)"):
        time.sleep(1)
    
    with ui.spinner("Finalizing", SpinnerStyle.MATRIX, suffix=" (100%)"):
        time.sleep(1)
    
    ui.separator()
    
    # Progress bars
    with ui.progress("Downloading files", 100, ProgressStyle.BLOCKS) as pbar:
        for i in range(100):
            time.sleep(0.01)
            pbar.update(1)
    
    with ui.progress("Installing packages", 50, ProgressStyle.GRADIENT) as pbar:
        for i in range(50):
            time.sleep(0.02)
            pbar.update(1)
    
    ui.separator()
    
    # Box and table
    ui.box(["This is content inside a box", "Multiple lines are supported", "With proper padding"], 
           "Information Box", "rounded")
    
    headers = ["Name", "Value", "Status"]
    rows = [
        ["CPU Usage", "45%", "Normal"],
        ["Memory", "67%", "High"],
        ["Disk", "23%", "Low"]
    ]
    ui.table(headers, rows, "System Status")
    
    ui.separator()
    
    # Performance monitoring
    with ui.monitor_performance("Complex operation"):
        time.sleep(2)
    
    ui.separator()
    ui.success("Demo completed successfully!")


# === EXAMPLE USAGE ===

if __name__ == "__main__":
    """Example usage and testing"""
    
    # Basic usage examples
    def basic_examples():
        ui = TerminalUI(theme='matrix')
        
        # Simple notifications
        ui.info("Application started")
        ui.success("Connected to server")
        ui.warning("Low disk space")
        
        # Spinner with context manager
        with ui.spinner("Connecting to database...", SpinnerStyle.DOTS):
            time.sleep(2)
        
        # Progress bar
        with ui.progress("Uploading files", 100) as pbar:
            for i in range(100):
                time.sleep(0.05)
                pbar.update(1)
        
        # Text effects
        ui.typewriter_effect("Mission accomplished!", color_key='success')
    
    # Advanced examples
    def advanced_examples():
        ui = TerminalUI(theme='cyberpunk', speed_factor=1.5)
        
        # Multiple themed elements
        ui.header("Advanced Terminal UI", "Cyberpunk Theme Active")
        
        # Performance monitoring
        with ui.monitor_performance("Data processing"):
            with ui.progress("Analyzing data", 1000, ProgressStyle.ARROWS) as pbar:
                for i in range(1000):
                    if i % 100 == 0:
                        time.sleep(0.1)  # Simulate processing
                    pbar.update(1)
        
        # Matrix rain effect
        ui.info("Initiating matrix effect...")
        matrix = MatrixRain(ui, duration=3.0, density=0.15)
        matrix.run()
        
        # Fire effect
        ui.info("Showing fire effect...")
        fire = FireEffect(ui, duration=2.0, height=8)
        fire.run()
        
        ui.success("Advanced demo complete!")
    
    # Run demonstrations
    try:
        print("Choose demo:")
        print("1. Full feature demo")
        print("2. Basic examples")
        print("3. Advanced examples")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            demo_all_features()
        elif choice == "2":
            basic_examples()
        elif choice == "3":
            advanced_examples()
        else:
            print("Invalid choice, running full demo...")
            demo_all_features()
            
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Demo error: {e}")