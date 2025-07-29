import time
import os
import random
import sys
import argparse

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def rainbow_color(text, bold=False):
    """Apply rainbow colors to text."""
    colors = [
        '\033[91m',  # Red
        '\033[93m',  # Yellow
        '\033[92m',  # Green
        '\033[96m',  # Cyan
        '\033[94m',  # Blue
        '\033[95m',  # Magenta
    ]
    reset = '\033[0m'
    bold_code = '\033[1m' if bold else ''
    colored_text = ""
    for i, char in enumerate(text):
        if char != ' ':
            colored_text += bold_code + colors[i % len(colors)] + char + reset
        else:
            colored_text += ' '
    return colored_text

def generate_ascii_art(char):
    """Generate ASCII art for any character that doesn't have a predefined template."""
    # Skip Unicode characters that might cause display issues
    if ord(char) > 127:
        char = '•'
        
    # Create a 7-line ASCII art representation for any character
    try:
        return [
            f"   {char}{char}{char}   ",
            f"  {char}   {char}  ",
            f" {char}     {char} ",
            f" {char}     {char} ",
            f" {char}     {char} ",
            f"  {char}   {char}  ",
            f"   {char}{char}{char}   ",
        ]
    except:
        # Fallback for any problematic characters
        return [
            "   •••   ",
            "  •   •  ",
            " •     • ",
            " •     • ",
            " •     • ",
            "  •   •  ",
            "   •••   ",
        ]

def print_fancy_text(text, colorful=True):
    """Print text using large ASCII art characters."""
    # Create larger ASCII art for each letter
    ascii_letters = {
        'A': [
            "   AAA   ",
            "  AAAAA  ",
            " AAA AAA ",
            "AAA   AAA",
            "AAAAAAAAA",
            "AAA   AAA",
            "AAA   AAA",
        ],
        'B': [
            "BBBBBBB  ",
            "BBB   BB ",
            "BBB   BBB",
            "BBBBBBBB ",
            "BBB   BBB",
            "BBB   BBB",
            "BBBBBBBB ",
        ],
        'C': [
            " CCCCCCC ",
            "CCC   CCC",
            "CCC      ",
            "CCC      ",
            "CCC      ",
            "CCC   CCC",
            " CCCCCCC ",
        ],
        'D': [
            "DDDDDDD  ",
            "DDD  DDD ",
            "DDD   DDD",
            "DDD   DDD",
            "DDD   DDD",
            "DDD  DDD ",
            "DDDDDDD  ",
        ],
        'E': [
            "EEEEEEEEE",
            "EEE      ",
            "EEE      ",
            "EEEEEEE  ",
            "EEE      ",
            "EEE      ",
            "EEEEEEEEE",
        ],
        'F': [
            "FFFFFFFFF",
            "FFF      ",
            "FFF      ",
            "FFFFFFF  ",
            "FFF      ",
            "FFF      ",
            "FFF      ",
        ],
        'G': [
            " GGGGGGG ",
            "GGG   GGG",
            "GGG      ",
            "GGG  GGGG",
            "GGG   GGG",
            "GGG   GGG",
            " GGGGGGG ",
        ],
        'H': [
            "HHH   HHH",
            "HHH   HHH",
            "HHH   HHH",
            "HHHHHHHHH",
            "HHH   HHH",
            "HHH   HHH",
            "HHH   HHH",
        ],
        'I': [
            "IIIIIII",
            "  III  ",
            "  III  ",
            "  III  ",
            "  III  ",
            "  III  ",
            "IIIIIII",
        ],
        'J': [
            "JJJJJJJ",
            "   JJJ ",
            "   JJJ ",
            "   JJJ ",
            "JJJ JJJ",
            "JJJ JJJ",
            " JJJJJ ",
        ],
        'K': [
            "KKK  KKK ",
            "KKK KKK  ",
            "KKKKKK   ",
            "KKKKK    ",
            "KKK KKK  ",
            "KKK  KKK ",
            "KKK   KKK",
        ],
        'L': [
            "LLL      ",
            "LLL      ",
            "LLL      ",
            "LLL      ",
            "LLL      ",
            "LLL      ",
            "LLLLLLLLL",
        ],
        'M': [
            "MMM   MMM",
            "MMMM MMMM",
            "MMM M MMM",
            "MMM   MMM",
            "MMM   MMM",
            "MMM   MMM",
            "MMM   MMM",
        ],
        'N': [
            "NNN   NNN",
            "NNNN  NNN",
            "NNNNN NNN",
            "NNN NNNNN",
            "NNN  NNNN",
            "NNN   NNN",
            "NNN   NNN",
        ],
        'O': [
            " OOOOOOO ",
            "OOO   OOO",
            "OOO   OOO",
            "OOO   OOO",
            "OOO   OOO",
            "OOO   OOO",
            " OOOOOOO ",
        ],
        'P': [
            "PPPPPPPP ",
            "PPP    PP",
            "PPP    PP",
            "PPPPPPPP ",
            "PPP      ",
            "PPP      ",
            "PPP      ",
        ],
        'Q': [
            " QQQQQQQ ",
            "QQQ   QQQ",
            "QQQ   QQQ",
            "QQQ   QQQ",
            "QQQ QQ QQ",
            "QQQ  QQQ ",
            " QQQQQQQQ",
        ],
        'R': [
            "RRRRRRRR ",
            "RRR    RR",
            "RRR    RR",
            "RRRRRRRR ",
            "RRRRRR   ",
            "RRR  RRR ",
            "RRR   RRR",
        ],
        'S': [
            " SSSSSSS ",
            "SSS   SSS",
            "SSS      ",
            " SSSSSSS ",
            "      SSS",
            "SSS   SSS",
            " SSSSSSS ",
        ],
        'T': [
            "TTTTTTTTT",
            "   TTT   ",
            "   TTT   ",
            "   TTT   ",
            "   TTT   ",
            "   TTT   ",
            "   TTT   ",
        ],
        'U': [
            "UUU   UUU",
            "UUU   UUU",
            "UUU   UUU",
            "UUU   UUU",
            "UUU   UUU",
            "UUU   UUU",
            " UUUUUUU ",
        ],
        'V': [
            "VVV   VVV",
            "VVV   VVV",
            "VVV   VVV",
            " VVV VVV ",
            " VVV VVV ",
            "  VVVVV  ",
            "   VVV   ",
        ],
        'W': [
            "WWW   WWW",
            "WWW   WWW",
            "WWW   WWW",
            "WWW W WWW",
            "WWWWWWWWW",
            "WWW   WWW",
            "WW     WW",
        ],
        'X': [
            "XXX   XXX",
            " XXX XXX ",
            "  XXXXX  ",
            "   XXX   ",
            "  XXXXX  ",
            " XXX XXX ",
            "XXX   XXX",
        ],
        'Y': [
            "YYY   YYY",
            " YYY YYY ",
            "  YYYYY  ",
            "   YYY   ",
            "   YYY   ",
            "   YYY   ",
            "   YYY   ",
        ],
        'Z': [
            "ZZZZZZZZZ",
            "     ZZZ ",
            "    ZZZ  ",
            "   ZZZ   ",
            "  ZZZ    ",
            " ZZZ     ",
            "ZZZZZZZZZ",
        ],
        '0': [
            " 0000000 ",
            "000   000",
            "000  0000",
            "000 00000",
            "00000 000",
            "0000  000",
            " 0000000 ",
        ],
        '1': [
            "   111   ",
            "  1111   ",
            " 11 11   ",
            "    11   ",
            "    11   ",
            "    11   ",
            "  111111 ",
        ],
        '2': [
            " 2222222 ",
            "222   222",
            "      222",
            " 2222222 ",
            "222      ",
            "222      ",
            "222222222",
        ],
        '3': [
            "33333333 ",
            "     333 ",
            "     333 ",
            "33333333 ",
            "     333 ",
            "     333 ",
            "33333333 ",
        ],
        '4': [
            "444  444 ",
            "444  444 ",
            "444  444 ",
            "444444444",
            "     444 ",
            "     444 ",
            "     444 ",
        ],
        '5': [
            "555555555",
            "555      ",
            "555      ",
            "55555555 ",
            "     555 ",
            "555  555 ",
            " 555555  ",
        ],
        '6': [
            " 6666666 ",
            "666      ",
            "666      ",
            "66666666 ",
            "666   666",
            "666   666",
            " 6666666 ",
        ],
        '7': [
            "777777777",
            "     777 ",
            "    777  ",
            "   777   ",
            "  777    ",
            " 777     ",
            "777      ",
        ],
        '8': [
            " 8888888 ",
            "888   888",
            "888   888",
            " 8888888 ",
            "888   888",
            "888   888",
            " 8888888 ",
        ],
        '9': [
            " 9999999 ",
            "999   999",
            "999   999",
            " 99999999",
            "      999",
            "      999",
            " 9999999 ",
        ],
        ' ': [
            "       ",
            "       ",
            "       ",
            "       ",
            "       ",
            "       ",
            "       ",
        ],
        '.': [
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "   ..   ",
            "   ..   ",
        ],
        ',': [
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "   ,,   ",
            "    ,   ",
        ],
        '!': [
            "   !!   ",
            "   !!   ",
            "   !!   ",
            "   !!   ",
            "   !!   ",
            "        ",
            "   !!   ",
        ],
        '?': [
            " ?????? ",
            "?      ?",
            "      ? ",
            "    ?   ",
            "   ?    ",
            "        ",
            "   ?    ",
        ],
        '@': [
            " @@@@@@ ",
            "@      @",
            "@ @@@@ @",
            "@ @  @ @",
            "@ @@@@ @",
            "@       ",
            " @@@@@@ ",
        ],
        '#': [
            " #   #  ",
            " #   #  ",
            "#######",
            " #   #  ",
            "#######",
            " #   #  ",
            " #   #  ",
        ],
        '$': [
            "   $    ",
            " $$$$$$  ",
            "$  $     ",
            " $$$$$$  ",
            "    $  $ ",
            " $$$$$$  ",
            "   $    ",
        ],
        '%': [
            "%%    %%",
            "%%   %% ",
            "    %%  ",
            "   %%   ",
            "  %%    ",
            " %%   %%",
            "%%    %%",
        ],
        '^': [
            "   ^^   ",
            "  ^  ^  ",
            " ^    ^ ",
            "        ",
            "        ",
            "        ",
            "        ",
        ],
        '&': [
            " &&&&   ",
            "&    &  ",
            "&  &&   ",
            " &&     ",
            "&  && & ",
            "&    && ",
            " &&&& &&",
        ],
        '*': [
            "   *    ",
            " *   *  ",
            "  * *   ",
            "******* ",
            "  * *   ",
            " *   *  ",
            "*     * ",
        ],
        '(': [
            "    ((  ",
            "   ((   ",
            "  ((    ",
            "  ((    ",
            "  ((    ",
            "   ((   ",
            "    ((  ",
        ],
        ')': [
            "  ))    ",
            "   ))   ",
            "    ))  ",
            "    ))  ",
            "    ))  ",
            "   ))   ",
            "  ))    ",
        ],
        '-': [
            "        ",
            "        ",
            "        ",
            " ------- ",
            "        ",
            "        ",
            "        ",
        ],
        '_': [
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "________",
        ],
        '+': [
            "        ",
            "   ++   ",
            "   ++   ",
            "++++++++",
            "   ++   ",
            "   ++   ",
            "        ",
        ],
        '=': [
            "        ",
            "        ",
            "========",
            "        ",
            "========",
            "        ",
            "        ",
        ],
        '/': [
            "      //",
            "     // ",
            "    //  ",
            "   //   ",
            "  //    ",
            " //     ",
            "//      ",
        ],
        '\\': [
            "\\\\      ",
            " \\\\     ",
            "  \\\\    ",
            "   \\\\   ",
            "    \\\\  ",
            "     \\\\ ",
            "      \\\\",
        ],
        '|': [
            "   ||   ",
            "   ||   ",
            "   ||   ",
            "   ||   ",
            "   ||   ",
            "   ||   ",
            "   ||   ",
        ],
        ':': [
            "        ",
            "   ::   ",
            "   ::   ",
            "        ",
            "   ::   ",
            "   ::   ",
            "        ",
        ],
        ';': [
            "        ",
            "   ;;   ",
            "   ;;   ",
            "        ",
            "   ;;   ",
            "   ;;   ",
            "    ;   ",
        ],
        '"': [
            "  \"\"  \"\"  ",
            "  \"\"  \"\"  ",
            "  \"\"  \"\"  ",
            "        ",
            "        ",
            "        ",
            "        ",
        ],
        "'": [
            "   ''   ",
            "   ''   ",
            "   ''   ",
            "        ",
            "        ",
            "        ",
            "        ",
        ],
        '<': [
            "    <<  ",
            "   <<   ",
            "  <<    ",
            " <<     ",
            "  <<    ",
            "   <<   ",
            "    <<  ",
        ],
        '>': [
            "  >>    ",
            "   >>   ",
            "    >>  ",
            "     >> ",
            "    >>  ",
            "   >>   ",
            "  >>    ",
        ],
    }

    # Get the height of the ASCII art
    height = len(ascii_letters['A'])
    
    # Transpose the text to display vertically
    for h in range(height):
        line = ""
        for char in text:
            # Handle explicitly defined characters
            if char in ascii_letters:
                line += ascii_letters[char][h] + "   "
            else:
                # Generate ASCII art for any other character
                art = generate_ascii_art(char)
                line += art[h] + "   "
        
        # Print with or without color based on the colorful parameter
        if colorful:
            print(rainbow_color(line, bold=True))
        else:
            print(line)
    
    print("\n")

def generate_small_ascii_art(char):
    """Generate smaller ASCII art for any character."""
    # Skip Unicode characters that might cause display issues
    if ord(char) > 127:
        char = '•'
        
    # Create a 5-line ASCII art representation for any character
    try:
        return [
            f" {char}{char} ",
            f"{char}  {char}",
            f"{char}  {char}",
            f"{char}  {char}",
            f" {char}{char} ",
        ]
    except:
        # Fallback for any problematic characters
        return [
            " •• ",
            "•  •",
            "•  •",
            "•  •",
            " •• ",
        ]

def print_small_fancy_text(text, colorful=True):
    """Print text using smaller ASCII art characters for special cases."""
    # Create smaller ASCII art for each letter
    small_ascii_letters = {
        'A': [
            " AA ",
            "A  A",
            "AAAA",
            "A  A",
            "A  A",
        ],
        'B': [
            "BBB ",
            "B  B",
            "BBB ",
            "B  B",
            "BBB ",
        ],
        'C': [
            " CCC",
            "C   ",
            "C   ",
            "C   ",
            " CCC",
        ],
        'D': [
            "DDD ",
            "D  D",
            "D  D",
            "D  D",
            "DDD ",
        ],
        'E': [
            "EEEE",
            "E   ",
            "EEE ",
            "E   ",
            "EEEE",
        ],
        'F': [
            "FFFF",
            "F   ",
            "FFF ",
            "F   ",
            "F   ",
        ],
        'G': [
            " GGG",
            "G   ",
            "G GG",
            "G  G",
            " GGG",
        ],
        'H': [
            "H  H",
            "H  H",
            "HHHH",
            "H  H",
            "H  H",
        ],
        'I': [
            "III",
            " I ",
            " I ",
            " I ",
            "III",
        ],
        'J': [
            "  J",
            "  J",
            "  J",
            "J J",
            " J ",
        ],
        'K': [
            "K  K",
            "K K ",
            "KK  ",
            "K K ",
            "K  K",
        ],
        'L': [
            "L   ",
            "L   ",
            "L   ",
            "L   ",
            "LLLL",
        ],
        'M': [
            "M   M",
            "MM MM",
            "M M M",
            "M   M",
            "M   M",
        ],
        'N': [
            "N  N",
            "NN N",
            "N NN",
            "N  N",
            "N  N",
        ],
        'O': [
            " OO ",
            "O  O",
            "O  O",
            "O  O",
            " OO ",
        ],
        'P': [
            "PPP ",
            "P  P",
            "PPP ",
            "P   ",
            "P   ",
        ],
        'Q': [
            " QQ ",
            "Q  Q",
            "Q  Q",
            "Q Q ",
            " QQQ",
        ],
        'R': [
            "RRR ",
            "R  R",
            "RRR ",
            "R R ",
            "R  R",
        ],
        'S': [
            " SSS",
            "S   ",
            " SS ",
            "   S",
            "SSS ",
        ],
        'T': [
            "TTT",
            " T ",
            " T ",
            " T ",
            " T ",
        ],
        'U': [
            "U  U",
            "U  U",
            "U  U",
            "U  U",
            " UU ",
        ],
        'V': [
            "V  V",
            "V  V",
            "V  V",
            " VV ",
            "  V ",
        ],
        'W': [
            "W   W",
            "W   W",
            "W W W",
            "WW WW",
            "W   W",
        ],
        'X': [
            "X  X",
            " XX ",
            " XX ",
            " XX ",
            "X  X",
        ],
        'Y': [
            "Y  Y",
            " YY ",
            "  Y ",
            "  Y ",
            "  Y ",
        ],
        'Z': [
            "ZZZZ",
            "  Z ",
            " Z  ",
            "Z   ",
            "ZZZZ",
        ],
        ' ': [
            "    ",
            "    ",
            "    ",
            "    ",
            "    ",
        ],
        '!': [
            "!",
            "!",
            "!",
            " ",
            "!",
        ],
        '.': [
            " ",
            " ",
            " ",
            " ",
            ".",
        ],
    }

    # Get the height of the ASCII art
    height = len(small_ascii_letters['A'])
    
    # Transpose the text to display vertically
    for h in range(height):
        line = ""
        for char in text:
            # Handle explicitly defined characters
            if char in small_ascii_letters:
                line += small_ascii_letters[char][h] + "  "
            else:
                # Generate ASCII art for any other character
                art = generate_small_ascii_art(char)
                line += art[h] + "  "
        
        # Print with or without color based on the colorful parameter
        if colorful:
            print(rainbow_color(line, bold=True))
        else:
            print(line)
    
    print("\n")

def gradient_text(text):
    """Apply a gradient color effect to text."""
    gradient = [
        '\033[38;5;196m',  # Bright red
        '\033[38;5;202m',  # Orange-red
        '\033[38;5;208m',  # Orange
        '\033[38;5;214m',  # Yellow-orange
        '\033[38;5;220m',  # Yellow
        '\033[38;5;226m',  # Bright yellow
        '\033[38;5;190m',  # Yellow-green
        '\033[38;5;154m',  # Light green
        '\033[38;5;118m',  # Green
        '\033[38;5;82m',   # Bright green
        '\033[38;5;46m',   # Vivid green
        '\033[38;5;47m',   # Green-cyan
        '\033[38;5;48m',   # Cyan-green
        '\033[38;5;49m',   # Light cyan
        '\033[38;5;50m',   # Cyan
        '\033[38;5;51m',   # Bright cyan
        '\033[38;5;45m',   # Cyan-blue
        '\033[38;5;39m',   # Light blue
        '\033[38;5;33m',   # Blue
        '\033[38;5;27m',   # Bright blue
        '\033[38;5;21m',   # Vivid blue
        '\033[38;5;57m',   # Blue-violet
        '\033[38;5;93m',   # Violet
        '\033[38;5;129m',  # Purple
        '\033[38;5;165m',  # Pink
        '\033[38;5;201m',  # Magenta
        '\033[38;5;207m',  # Light magenta
        '\033[38;5;213m',  # Pink-magenta
    ]
    reset = '\033[0m'
    bold = '\033[1m'
    gradient_text = ""
    
    for i, char in enumerate(text):
        if char != ' ':
            gradient_text += bold + gradient[i % len(gradient)] + char + reset
        else:
            gradient_text += ' '
    
    return gradient_text

def print_border(width):
    """Print a decorative border."""
    # Create a more dramatic pattern using different symbols
    border_pattern = "★✦✧⭐✦★✧⭐"
    border = ""
    
    # Fill the border to width using the pattern
    while len(border) < width:
        border += border_pattern[len(border) % len(border_pattern)]
    
    # Print the border with gradient colors
    print(gradient_text(border))

def terminal_size():
    """Get the current terminal size."""
    try:
        columns, rows = os.get_terminal_size()
        return columns, rows
    except:
        return 80, 24  # default fallback

def print_centered(text):
    """Print text centered in the terminal."""
    columns, _ = terminal_size()
    print(text.center(columns))

def print_sparkles():
    """Display sparkle animation."""
    columns, rows = terminal_size()
    for _ in range(5):
        clear_screen()
        for _ in range(int(rows/2)):
            sparkles = ""
            for _ in range(columns//4):
                if random.random() > 0.8:
                    sparkles += random.choice(["✨", "⭐", "🌟", "✦", "✧", " ", " ", " ", " "])
                else:
                    sparkles += " "
            print_centered(gradient_text(sparkles))
        time.sleep(0.2)

def animate_text(text, colorful=True, small=False):
    """Display animated text with various effects."""
    columns, rows = terminal_size()
    
    # Start with sparkles animation
    print_sparkles()
    
    # Show final result directly after sparkles
    if colorful:
        # Final epic display
        clear_screen()
        print("\n" * (rows//6))
        print_border(columns)
        print("\n")
        
        # Use smaller text if requested
        if small:
            print_small_fancy_text(text)
        else:
            print_fancy_text(text)
            
        print_centered("✨ " + gradient_text("Congratulations!") + " ✨")
        print("\n")
        print_border(columns)
        print("\n")
    else:
        # Simple non-colorful display for special cases
        clear_screen()
        print("\n" * (rows//3))
        print("=" * columns)
        print("\n")
        
        # Use smaller text if requested
        if small:
            print_small_fancy_text(text, colorful=False)
        else:
            print_fancy_text(text, colorful=False)
            
        print("\n")
        print("=" * columns)
        print("\n")

def display_text(text=None):
    """Main function to display the fancy text."""
    try:
        if text is None:
            text = "YOU ARE GAY"
        animate_text(text)
        return True
    except KeyboardInterrupt:
        clear_screen()
        print("\nDisplay stopped. Goodbye!")
        return False

def main():
    """Entry point for the command-line script."""
    try:
        parser = argparse.ArgumentParser(description='Display a name with IS GAY in a fancy way')
        parser.add_argument('name', nargs='*', default=['YOU'], help='Name to display')
        args = parser.parse_args()
        
        # Convert args.name list to a single string
        if args.name:
            name = ' '.join(args.name).upper()
        else:
            name = "YOU"
        
        # Check for special cases - people who are NOT GAY
        name_lower = name.lower()
        not_gay_list = ["boaz", "yuval", "arad", "ilia", "maayan", "muhammad", "tal", "nadav"]
        
        # Special case for barak - he is SUPER GAY
        if name_lower == "barak":
            message = f"{name.upper()} IS SUPER GAY"
            animate_text(message, small=True)
        elif name_lower in not_gay_list:
            # Special message for these cases
            message = f"{name.upper()} IS NOT GAY"
            animate_text(message, colorful=False, small=True)
        else:    
            # Always add "IS GAY" to the name for other cases
            message = f"{name} IS GAY"
            animate_text(message)
            
    except KeyboardInterrupt:
        clear_screen()
        print("\nDisplay stopped. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main() 
