#!/usr/bin/env python3
from datetime import timedelta as td
from datetime import datetime as dt
from rich.console import Console
from rich.table import Column
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.style import Style
from rich.text import Text
from rich.live import Live
from rich import box
from pathlib import Path
import subprocess
import inspect
import shutil
import psutil
import time
import tty
import sys
import os
import re

import iterm2

async def restartSession(connection):
    app = await iterm2.async_get_app(connection)
    # window = app.current_window
    # print(app.pretty_str())
    # r = re.search(r'Session ".*" id=(?P<session_id>[A-Z0-9-]+)', window.pretty_str())
    # session_id = r.groupdict()["session_id"]
    # session = app.get_session_by_id(session_id)
    session = app.current_window.current_tab.current_session
    await session.async_restart()
    return

async def resizeShell(connection):
    app = await iterm2.async_get_app(connection)
    window = app.current_window
    frame = iterm2.Frame()
    frame.load_from_dict({'origin': {'x': 3, 'y': 0}, 'size': {'width': 1080, 'height': 830}})
    await window.async_set_frame(frame)

import termios, tty, sys, os

def getkey():
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            if len(b) == 3:
                k = ord(b[2])
            else:
                k = ord(b)
            key_mapping = {
                127: 'backspace',
                10: 'return',
                13: 'enter',
                32: 'space',
                9: 'tab',
                27: 'esc',
                65: 'up',
                66: 'down',
                67: 'right',
                68: 'left'
            }
            return key_mapping.get(k, chr(k))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def run():
    try:
        while True:
            k = getkey()
            if k == 'esc':
                break
            else:
                print(k)
    except (KeyboardInterrupt, SystemExit):
        os.system('stty sane')
        print('stopping.')

def get_py_path(verbose=False):
    # return Path(globals()['_dh'][0]) if globals().get('_dh') else Path(__file__)
    print('starting at currentframe().f_back') if verbose else ''
    env = inspect.currentframe().f_back.f_locals
    if ((not env.get('_dh')) and (not env.get('__file__'))):
        print('going deeper: currentframe().f_back.f_back') if verbose else ''
        env = inspect.currentframe().f_back.f_back.f_locals
        if ((not env.get('_dh')) and (not env.get('__file__'))):
            print('even deeper: currentframe().f_back.f_back.f_back') if verbose else ''
            env = inspect.currentframe().f_back.f_back.f_back.f_locals
    if env.get('_dh'):
        print('==ipython shell==') if verbose else ''
        if env.get('__file__'):
            return Path(env["_dh"][0], env["__file__"]).resolve().parent

        if verbose:
            print('<File.py>: NOT FOUND!')
            print('Next time run with:\n  ipython -i -- <File.py>')
            print('using cwd()')
        return Path(env["_dh"][0])

    print(f'env = {env}') if verbose else ''
    return Path(env["__file__"]).resolve().parent

def setup():
    old = get_py_path()
    extractTheme()
    cwd = Path.home().joinpath("Library", "Application Support")
    if shutil.get_terminal_size().columns >= 96:
        os.chdir(cwd)
    elif shutil.get_terminal_size().columns >= 76:
        cwd = Path.home().joinpath("Library")
        os.chdir(cwd)
    else:
        iterm2.run_until_complete(resizeShell)
    return old, cwd

def cleanup(old):
    os.chdir(old)

def spawnShell():
    comment = Text.from_markup('[yellow]Run: [/] "[green]exec $SHELL[/]" to update the terminal.')
    c.print(Align.center(Panel(comment)))

    time.sleep(1)
    if os.environ["LC_TERMINAL"] == 'iTerm2':
        comment = Text.from_markup('[yellow]iTerm2 Detected![/]\n[red bold]Attempting to Restart iTerm2 Session...[/]')
        c.print(Align.center(Panel(comment)))
        time.sleep(3)
        iterm2.run_until_complete(restartSession)

    # os.system("exec zsh")
    # # cmd = "exec /usr/local/bin/zsh -c 'sleep 1 && exit'"
    # cmd = 'zle && zle .reset-prompt && zle -R'
    # os.system(cmd)
    # out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # print(out.stdout)
    # print(out.stderr)

def escape_ansi(line):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)

def get(value):
    cmd = str(Path.home().joinpath("bin", "get.zsh")) + " " + value
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout
    return out

def convertBytes(number_in_bytes):
    tags = [ "B", "K", "M", "G", "T" ]

    i = 0
    double_bytes = number_in_bytes

    while (i < len(tags) and  number_in_bytes >= 1024):
            double_bytes = number_in_bytes / 1024.0
            i = i + 1
            number_in_bytes = number_in_bytes / 1024

    return str(round(double_bytes, 2)).zfill(2) + tags[i]

def getRam():
    p = psutil.virtual_memory()
    return convertBytes(p.inactive)

def getBattery():
    p = psutil.sensors_battery()
    return f'{p.percent}%'

def getParams():
    def parseKeys(key):
        if '{' in key:
            prefix = key.split('{')[0]
            suffix = key.split('}')[1]
            keywords = key.split('{')[1].split('}')[0].split(',')
            return [f'{prefix}{k}{suffix}' for k in keywords]
        return [key]

    def keepUnicode(val):
        val = re.sub(r'\\U([0-9A-F]{5})', r'\\U' + str(rf'\1').rjust(5, '0'), val)
        val = re.sub(r'\%([0-9]{3})F', '\x1b[38;5;' + r'\1m', val)
        return eval(val) if ((r'\u' in val) or (r"'" in val) or (val.isdigit())) else val
        #return re.sub(r'\%([0-9]{3})F', '\x1b[38;5;' + r'\1m', val)

    p10k = Path.home().joinpath('.p10k.zsh').read_text()
    r = re.compile(r'  typeset -g (?P<key>[A-Z0-9{,_}]+)=(?P<val>.+)')
    params = {}
    for p in r.finditer(p10k):
        for key in parseKeys(p.groupdict()["key"]):
            params[key] = keepUnicode(p.groupdict()["val"])
    return params

def extractTheme():
    params = getParams()

    # -- prompt bg='234'
    globals()["prompt_bg"] = params["POWERLEVEL9K_BACKGROUND"]

    # -- icons '' '' '' ''
    globals()["os_icon"]        = "\uF179"
    globals()["dir_icon"]       = "\uF07C"
    globals()["ram_icon"]       = "\uF0e4"
    globals()["exec_time_icon"] = "\uF252"
    globals()["clock_icon"]     = "\uF017"

    # -- os colors '255
    globals()["os_icon_fg"]     = params["POWERLEVEL9K_OS_ICON_FOREGROUND"]

    # -- dir colors '31' '103', '39
    globals()["dir_fg"]        = params["POWERLEVEL9K_DIR_FOREGROUND"]
    globals()["dir_short_fg"]  = params["POWERLEVEL9K_DIR_SHORTENED_FOREGROUND"]
    globals()["dir_anchor_fg"] = params["POWERLEVEL9K_DIR_ANCHOR_FOREGROUND"]

    # -- ram colors '66'
    globals()["ram"]           = getRam()
    globals()["ram_fg"]        = params["POWERLEVEL9K_RAM_FOREGROUND"]

    # -- time colors format '66' '248' ( '%D{%I:%M:%S %p}' == '10:35:40 AM' )
    globals()["time_fg"]      = params["POWERLEVEL9K_TIME_FOREGROUND"]
    globals()["exec_time_fg"] = params["POWERLEVEL9K_COMMAND_EXECUTION_TIME_FOREGROUND"]
    globals()["time_format"]  = dt.now().strftime(params["POWERLEVEL9K_TIME_FORMAT"].strip('%D').strip('{}'))

    # -- separators '%242F' '%242F' '%244Ftook ' '%244Fat '
    globals()["left_sep"]         = params["POWERLEVEL9K_LEFT_SUBSEGMENT_SEPARATOR"]
    globals()["right_sep"]        = params["POWERLEVEL9K_RIGHT_SUBSEGMENT_SEPARATOR"]
    globals()["exec_time_prefix"] = params["POWERLEVEL9K_COMMAND_EXECUTION_TIME_PREFIX"]
    globals()["time_prefix"]      = params["POWERLEVEL9K_TIME_PREFIX"]

    # -- endings '' ''
    globals()["left_end"]  = params["POWERLEVEL9K_LEFT_SEGMENT_SEPARATOR"]
    globals()["right_end"] = params["POWERLEVEL9K_RIGHT_SEGMENT_SEPARATOR"]

    # -- end cap
    globals()["end"] = '\033[0m'

    # -- dots in-between '[ LEFT > ... < RIGHT ]'
    globals()["gap_char"]      = params["POWERLEVEL9K_MULTILINE_FIRST_PROMPT_GAP_CHAR"]
    globals()["prompt_gap_fg"] = params["POWERLEVEL9K_MULTILINE_FIRST_PROMPT_GAP_FOREGROUND"]

    # -- shell prompt '❯'
    globals()["prompt_char"]   = params["POWERLEVEL9K_PROMPT_CHAR_OK_VIINS_CONTENT_EXPANSION"]
    globals()["content_ok"]    = params["POWERLEVEL9K_PROMPT_CHAR_OK_VIINS_FOREGROUND"]
    globals()["content_error"] = params["POWERLEVEL9K_PROMPT_CHAR_ERROR_VIINS_FOREGROUND"]

    # -- battery info
    globals()["battery"]                = getBattery()
    globals()["battery_icon"]           = params["POWERLEVEL9K_BATTERY_STAGES"][-1]
    globals()["battery_charging_icon"]  = params["POWERLEVEL9K_BATTERY_STAGES"][-5]
    globals()["battery_low_icon"]       = params["POWERLEVEL9K_BATTERY_STAGES"][-9]
    globals()["battery_disc_icon"]      = params["POWERLEVEL9K_BATTERY_STAGES"][-11]
    globals()["battery_charged_fg"]     = params["POWERLEVEL9K_BATTERY_CHARGED_FOREGROUND"]
    globals()["battery_charging_fg"]    = params["POWERLEVEL9K_BATTERY_CHARGING_FOREGROUND"]
    globals()["battery_low_fg"]         = params["POWERLEVEL9K_BATTERY_LOW_FOREGROUND"]
    globals()["battery_disc_fg"]        = params["POWERLEVEL9K_BATTERY_DISCONNECTED_FOREGROUND"]

def updateSetting(item='', color=-1, save=True):
    value = color
    if item == "l_background":
        key = "POWERLEVEL9K_BACKGROUND"
    if item == "l_os":
        key = "POWERLEVEL9K_OS_ICON_FOREGROUND"
    if item == "l_sep":
        key = "POWERLEVEL9K_LEFT_SUBSEGMENT_SEPARATOR"
        value = re.sub(r'(\x1b\[(38|48);5;[0-9]{3}m)', rf'%{str(color).zfill(3)}F', eval(item))
    if item == "l_icon":
        key = "POWERLEVEL9K_DIR_FOREGROUND"
    if item == "l_home":
        key = "POWERLEVEL9K_DIR_ANCHOR_FOREGROUND"
    if item == "l_parent":
        key = "POWERLEVEL9K_DIR_FOREGROUND"
    if item == "l_anchor":
        key = "POWERLEVEL9K_DIR_ANCHOR_FOREGROUND"
    if item == "l_ram":
        key = "POWERLEVEL9K_RAM_FOREGROUND"
    if item == "l_ram_icon":
        key = "POWERLEVEL9K_RAM_FOREGROUND"
    if item == "m_gap_char":
        key = "POWERLEVEL9K_MULTILINE_FIRST_PROMPT_GAP_FOREGROUND"
    if item == "r_background":
        key = "POWERLEVEL9K_BACKGROUND"
    if item == "r_e_prefix":
        key = "POWERLEVEL9K_COMMAND_EXECUTION_TIME_PREFIX"
        value = re.sub(r'(\x1b\[(38|48);5;[0-9]{3}m)', rf'%{str(color).zfill(3)}F', eval(item))
    if item == "r_e_time":
        key = "POWERLEVEL9K_COMMAND_EXECUTION_TIME_FOREGROUND"
    if item == "r_e_icon":
        key = "POWERLEVEL9K_COMMAND_EXECUTION_TIME_FOREGROUND"
    if item == "r_sep":
        key = "POWERLEVEL9K_RIGHT_SUBSEGMENT_SEPARATOR"
        value = re.sub(r'(\x1b\[(38|48);5;[0-9]{3}m)', rf'%{str(color).zfill(3)}F', eval(item))
    if item == "r_c_prefix":
        key = "POWERLEVEL9K_TIME_PREFIX"
        value = re.sub(r'(\x1b\[(38|48);5;[0-9]{3}m)', rf'%{str(color).zfill(3)}F', eval(item))
    if item == "r_c_time":
        key = "POWERLEVEL9K_TIME_FOREGROUND"
    if item == "r_c_icon":
        key = "POWERLEVEL9K_TIME_FOREGROUND"
    if item == "r_battery":
        key = "POWERLEVEL9K_BATTERY_{CHARGING,CHARGED}_FOREGROUND"
    if item == "r_battery_icon":
        key = "POWERLEVEL9K_BATTERY_{CHARGING,CHARGED}_FOREGROUND"
    if item == "r_battery_charging":
        key = "POWERLEVEL9K_BATTERY_{CHARGING,CHARGED}_FOREGROUND"
    if item == "r_battery_low":
        key = "POWERLEVEL9K_BATTERY_LOW_FOREGROUND"
    if item == "r_battery_disc":
        key = "POWERLEVEL9K_BATTERY_DISCONNECTED_FOREGROUND"
    if item == "prompt_ok":
        key = "POWERLEVEL9K_PROMPT_CHAR_OK_{VIINS,VICMD,VIVIS,VIOWR}_FOREGROUND"
    if item == "prompt_error":
        key = "POWERLEVEL9K_PROMPT_CHAR_ERROR_{VIINS,VICMD,VIVIS,VIOWR}_FOREGROUND"

    if save:
        if value == -1:
            printError(error=f'COLOR VALUE: {value}', title='ERROR: BAD COLOR VALUE')
            sys.exit(0)

        # config_file = Path.home().joinpath('.tmp.zsh')
        config_file = Path.home().joinpath('.p10k.zsh')
        backup_file = Path.home().joinpath('.p10k_backup.zsh')
        raw = config_file.read_text()
        backup_file.write_text(raw)
        if str(value).isdigit():
            comment = f"Applying Settings: [cyan bold]{key}={value}[/]" + f'\nBackup File: [blue bold]{str(backup_file)}[/]'
            c.print(Align.center(Panel(Text.from_markup(comment))))
            config_file.write_text(re.sub(rf'typeset -g {key}=(.*)', f"typeset -g {key}={value}", raw))
        else:
            comment = f"Applying Settings: [cyan bold]{key}='{value}'[/]" + f'\nBackup File: [blue bold]{str(backup_file)}[/]'
            c.print(Align.center(Panel(Text.from_markup(comment))))
            config_file.write_text(re.sub(rf'typeset -g {key}=(.*)', f"typeset -g {key}='{value}'", raw))
        return
    return key

def wrap(text='', fg='', bg='', bold=False):
    fg = str(fg)
    bg = str(bg)
    if fg:
        text = f'\033[38;5;{fg}m' + text
    if bg:
        text = f'\033[48;5;{bg}m' + text
    if bold:
        text = '\033[1m' + text + end
    return text

def combineParts(*args):
    parts = ''
    for part in args:
        parts += part
    return parts

def extractLeft(parent, anchor):
    _os     = wrap(f' {os_icon} ', fg=os_icon_fg, bg=prompt_bg)
    _sep    = wrap(left_sep, bg=prompt_bg)
    _icon   = wrap(f' {dir_icon} ', fg=dir_fg, bg=prompt_bg)
    _home   = wrap('~', fg=dir_anchor_fg, bold=True)
    _parent = wrap(parent, fg=dir_fg, bg=prompt_bg)
    _anchor = wrap(f'{anchor} ', fg=dir_anchor_fg, bold=True)
    _ram_icon = wrap(f' {ram_icon} ', fg=ram_fg, bg=prompt_bg)
    _ram      = wrap(f'{ram} '+end, fg=ram_fg, bg=prompt_bg)
    _arrow    = wrap(left_end, fg=prompt_bg)
    l_background = wrap(' '*10+end, bg=prompt_bg)
    l_arrow      = wrap(left_end, fg=prompt_bg)
    globals()["l_background"] = l_background + l_arrow
    globals()["l_os"]         = wrap(os_icon, fg=os_icon_fg)
    globals()["l_sep"]        = left_sep
    globals()["l_icon"]       = wrap(dir_icon, fg=dir_fg)
    globals()["l_home"]       = wrap('~', fg=dir_anchor_fg, bold=True)
    globals()["l_parent"]     = wrap(parent, fg=dir_fg)
    globals()["l_anchor"]     = wrap(anchor, fg=dir_anchor_fg, bold=True)
    globals()["l_ram"]      = wrap(ram, fg=ram_fg)
    globals()["l_ram_icon"] = wrap(ram_icon, fg=ram_fg)
    return combineParts(_os, _sep, _icon, _home, _parent, _anchor, _sep, _ram_icon, _ram, _arrow, end)

def parseTime(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return {'d': days, 'h': hours, 'm': minutes, 's': seconds}

def getTime(seconds):
    elapsed = parseTime(seconds)
    took = ''
    for k,v in elapsed.items():
        if v:
            took += f'{v}{k} '
    return took

def extractMiddle(width, num_gaps=0):
    num_gaps = num_gaps if num_gaps else (width - len(escape_ansi(left)) - len(escape_ansi(right)) - 4)
    globals()["m_gap_char"] = wrap((gap_char*num_gaps), fg=prompt_gap_fg)
    return combineParts(m_gap_char, end)

def extractRight(seconds):
    exec_time = getTime(seconds)
    _arrow    = wrap(right_end, fg=prompt_bg)
    _e_prefix = wrap(f' {exec_time_prefix}', fg=exec_time_fg, bg=prompt_bg)
    _e_time   = wrap(exec_time, fg=exec_time_fg, bg=prompt_bg)
    _e_icon   = wrap(f'{exec_time_icon} ', fg=exec_time_fg, bg=prompt_bg)
    _sep      = wrap(right_sep, bg=prompt_bg)
    # _sep2     = wrap(right_sep, bg=prompt_bg)
    _c_prefix = wrap(f' {time_prefix}', fg=time_fg, bg=prompt_bg)
    _c_time   = wrap(time_format, fg=time_fg, bg=prompt_bg)
    _c_icon   = wrap(f' {clock_icon} ', fg=time_fg, bg=prompt_bg)
    _battery      = wrap(f' {battery} ', fg=battery_charged_fg, bg=prompt_bg)
    _battery_icon = wrap(f'{battery_icon} ', fg=battery_charged_fg, bg=prompt_bg)
    r_background = wrap(' '*10+end, bg=prompt_bg)
    r_arrow      = wrap(right_end, fg=prompt_bg)
    globals()["r_background"] = r_arrow + r_background
    globals()["r_e_prefix"] = exec_time_prefix
    globals()["r_e_time"]   = wrap(exec_time, fg=exec_time_fg)
    globals()["r_e_icon"]   = wrap(exec_time_icon, fg=exec_time_fg)
    globals()["r_sep"]      = right_sep
    globals()["r_c_prefix"] = time_prefix
    globals()["r_c_time"]   = wrap(time_format, fg=time_fg)
    globals()["r_c_icon"]   = wrap(clock_icon, fg=time_fg)
    globals()["r_battery"]          = wrap(battery, fg=battery_charged_fg)
    globals()["r_battery_icon"]     = wrap(battery_icon, fg=battery_charged_fg)
    globals()["r_battery_charging"] = wrap(battery_charging_icon, fg=battery_charging_fg)
    globals()["r_battery_low"]      = wrap(battery_low_icon, fg=battery_low_fg)
    globals()["r_battery_disc"]     = wrap(battery_disc_icon, fg=battery_disc_fg)
    return combineParts(_arrow, _e_prefix, _e_time, _e_icon, _sep, _c_prefix, _c_time, _c_icon, _sep, _battery, _battery_icon, end)

def extractBLeft():
    globals()["prompt_ok"] = wrap(prompt_char, fg=content_ok)
    globals()["prompt_error"] = wrap(prompt_char, fg=content_error)
    return combineParts(prompt_ok, end)

def extractBRight():
    _arrow        = wrap(right_end, fg=prompt_bg)
    _battery      = wrap(f' {battery} ', fg=battery_charged_fg, bg=prompt_bg)
    _battery_icon = wrap(battery_icon, fg=battery_charged_fg, bg=prompt_bg)
    br_background = wrap(' '*10+end, bg=prompt_bg)
    br_arrow      = wrap(right_end, fg=prompt_bg)
    globals()["br_background"]       = br_arrow + br_background
    globals()["br_battery"]          = wrap(battery, fg=battery_charged_fg)
    globals()["br_battery_icon"]     = wrap(battery_icon, fg=battery_charged_fg)
    globals()["br_battery_charging"] = wrap(battery_charging_icon, fg=battery_charging_fg)
    globals()["br_battery_low"]      = wrap(battery_low_icon, fg=battery_low_fg)
    globals()["br_battery_disc"]     = wrap(battery_disc_icon, fg=battery_disc_fg)

    return combineParts(_arrow, _battery, _battery_icon, end)

def printPrompt(left, middle, right, b_left, b_right):
    title = Text("Your Current Shell Prompt", style="bold", justify="center")
    text = Text.from_ansi(left + middle + right + "\n" + b_left + b_right)
    c.print(Panel(text, title=title))

def printSegment(row, segment):
    segments = ["Left", "Middle", "Right", "Bottom Left", "Bottom Right"]
    # title = Text("Modifying: " + segments[row] + " Prompt")
    title = Text("Modifying: " + segments[row] + " Prompt\n\n", style="bold", justify="center")
    text = Text.from_ansi(segment)

    # c.print(Align.center(Panel(text, title=title)))
    c.print(Panel(title+text, box=box.HORIZONTALS))


def printInfo(info='', item='', title=''):
    if item:
        item_color = re.search(r'(?:\x1B\[\d+;\d+;)(?P<color>\d+)', eval(item)).groupdict()["color"]
        item_key = updateSetting(item=item, save=False)
        bold = True if '\x1b[1m' in eval(item) else False
        ns = int((len(item_key)-2-3)/2)    # -2 (color-key), -3 (color_ID), /2 (left and right spaces)
        c_id = item_color.zfill(3)
        info = f'Key: {item_key}\nColor: {wrap(" "*ns + f"{c_id}" + " "*ns+end, fg=c_id, bg=c_id, bold=bold)}'

    title = Text.from_ansi(title)
    text = Text.from_ansi('\n\n' + info)
    c.print(Panel(Align.center(title+text), box=box.HORIZONTALS))

def printError(error, title=''):
    text = Text(error, style="red bold", justify="center")
    title = Text(title, style="red bold")
    c.print()
    c.print(Panel(text, title=title))
    c.print()

def generateTable(*args, row=0, title='', width=None):
    max_width = shutil.get_terminal_size().columns - 9
    table = Table(title=Panel(title), width=width, show_edge=False)
    table.add_column("", justify="right")
    table.add_column("Segments", justify="left", no_wrap=True, max_width=max_width)
    for i, elem in enumerate(args):
        if i == row:
            table.add_row(Text("=>", style=Style(color="yellow", bold=True)), Text.from_ansi(elem))
        else:
            table.add_row(None, Text.from_ansi(elem))
    return table

def selectRow(*args, title='', width=None):
    n = len(args) - 1
    with Live(console=c, auto_refresh=False) as live:
        row = 0
        live.update(Align.center(generateTable(*args, row=row, title=title, width=width)), refresh=True)
        try:
            while True:
                k = getkey()
                if k in ['enter', 'return']:
                    break
                elif k == 'up':
                    row = (row - 1) if (row > 0) else 0
                elif k == 'down':
                    row = (row + 1) if (row < n) else n
                live.update(Align.center(generateTable(*args, row=row, title=title, width=width)), refresh=True)
        except KeyboardInterrupt:
            os.system('stty sane')
            sys.exit(1)
        os.system('stty sane')
    if width:
        return row
    width = generateTable(*args, row=row, title=title, width=width).__rich_measure__(c, c.options).maximum
    return row, width

def selectItem(row, segment, width=None):
    if row == 0:        # -- Left Prompt Items
        items = ["l_background", "l_os", "l_sep", "l_icon", "l_home", "l_parent", "l_anchor", "l_ram", "l_ram_icon"]
    if row == 1:        # -- Middle Prompt Items
        items = ["m_gap_char"]
    if row == 2:        # -- Right Prompt Items
        items = ["r_background", "r_e_prefix", "r_e_time", "r_e_icon", "r_sep", "r_c_prefix", "r_c_time", "r_c_icon", "r_battery", "r_battery_icon", "r_battery_charging", "r_battery_low", "r_battery_disc"]
    if row == 3:        # -- Bottom Left Items
        items = ["prompt_ok", "prompt_error"]
    if row == 4:        # -- Bottom Right Items
        items = ["br_background", "br_battery", "br_battery_icon", "br_battery_charging", "br_battery_low", "br_battery_disc"]

    item = selectRow(*map(eval, items), title='Select Item to Modify', width=width)
    return items[item]

def generateColorTable(col, row, num_cols, num_rows, bold=False):
    count = 0
    color_id = (col) + (row*num_cols)
    title = Text.from_ansi('Select Color: '+wrap('   '+str(color_id).zfill(3)+'  _'+end, bg=color_id, bold=bold))
    table = Table(title=Panel(title), box=None, padding=(0, 1, 0, 0), expand=True)
    # table = Table(box=None, padding=(0, 1, 0, 0), expand=True)

    for j in range(num_cols*2):
        table.add_column("")
    for i in range(num_rows):
        row_items = []
        for j in range(num_cols):
            color = wrap('  '+end, bg=count, bold=bold)
            if ((i == row) and (j == col)):
                row_items.append(Text(">", style=Style(color="yellow", bold=True)))
                row_items.append(Text.from_ansi(color))
                # title = Text.from_ansi('Select Color: '+wrap('   '+str(count).zfill(3)+'  _'+end, bg=count, bold=bold))
                # table.title = (Align.center(Panel(title)))
            else:
                row_items.append("")
                row_items.append(Text.from_ansi(color))
            count += 1
        table.add_row(*row_items)
    return Align.center(table)

def getDimensions():
    term_width = shutil.get_terminal_size().columns
    if (term_width > 128):
        num_cols, num_rows = 32, 8
    if ((term_width > 64) and (term_width <= 128)):
        num_cols, num_rows = 16, 16
    if ((term_width > 32) and (term_width <= 64)):
        num_cols, num_rows = 8, 32
    if ((term_width > 16) and (term_width <= 32)):
        num_cols, num_rows = 4, 64
    return num_cols, num_rows

def selectColor(bold=False):
    with Live(console=c, auto_refresh=False) as live:
        num_cols, num_rows = getDimensions()
        col, row = 0, 0
        live.update(generateColorTable(col, row, num_cols, num_rows, bold=bold), refresh=True)
        try:
            while True:
                num_cols, num_rows = getDimensions()
                k = getkey()
                if k in ['enter', 'return']:
                    break
                elif k == 'up':
                    # row = (row - 1) if (row > 0) else 0
                    row = (row - 1) if (row > 0) else (num_rows-1) # 0
                elif k == 'down':
                    # row = (row + 1) if (row < num_rows) else num_rows
                    row = (row + 1) if (row < (num_rows-1)) else 0 # num_rows
                elif k == 'left':
                    # col = (col - 1) if (col > 0) else 0
                    col = (col - 1) if (col > 0) else (num_cols-1) # 0
                elif k == 'right':
                    # col = (col + 1) if (col < num_cols) else num_cols
                    col = (col + 1) if (col < (num_cols-1)) else 0 # num_cols
                live.update(generateColorTable(col, row, num_cols, num_rows, bold=bold), refresh=True)
        except KeyboardInterrupt:
            os.system('stty sane')
            sys.exit(1)
        os.system('stty sane')
    color = (col) + (row*num_cols)
    return col, row, color


def main():
    global c
    global left
    global right
    global middle
    global b_left
    global b_right
    global prompt
    global item

    c = Console()
    old, cwd = setup()
    parent = '/' if cwd.parent == cwd.home() else f'/{cwd.parent.relative_to(cwd.home())}/'
    anchor = cwd.relative_to(cwd.home()).parts[-1]

    left    = extractLeft(parent, anchor)
    right   = extractRight(seconds=229)
    middle  = extractMiddle(width=shutil.get_terminal_size().columns)
    b_left  = extractBLeft()
    b_right = '' # extractBRight()
    prompt = [left, middle, right, b_left, b_right]
    cleanup(old)

    # -- Print Current Shell Prompt
    printPrompt(left, middle, right, b_left, b_right)

    # -- Select Prompt Segment (left, middle, right, b_left)
    # row = selectRow(left, middle, right, b_left, b_right, title="What segment do you want to modify?")
    right_size, left_size = len(escape_ansi(right)), len(escape_ansi(left))
    num_gaps = int((len(escape_ansi(left)) + len(escape_ansi(right))) / 2)
    middle = extractMiddle(width=shutil.get_terminal_size().columns, num_gaps=num_gaps)
    row, width = selectRow(left, middle, right, b_left, title="What segment do you want to modify?")
    segment = prompt[row]
    printSegment(row, segment)

    # -- Select Prompt Segment Item
    item = selectItem(row, segment, width=width)
    bold = True if '\x1b[1m' in eval(item) else False
    printInfo(item=item, title=f'\x1b[1mSelected Item:{end} {eval(item)} ')

    # -- Select Color Option
    col, row, color = selectColor(bold)

    # -- Update Settings File
    updateSetting(item, color)

    # -- Spawn New Shell
    exit(spawnShell())


if __name__ == '__main__':
    main()
