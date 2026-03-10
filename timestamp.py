#!/usr/bin/env python3
"""timestamp - Convert between time formats.

One file. Zero deps. Speaks time.

Usage:
  timestamp.py now                        → all formats
  timestamp.py 1741638000                 → epoch to human
  timestamp.py "2026-03-10T14:00:00"      → ISO to epoch
  timestamp.py "March 10, 2026"           → human to epoch
  timestamp.py diff 1741638000 1741724400 → time between
  timestamp.py add 1741638000 2h30m       → add duration
"""

import argparse
import calendar
import re
import sys
import time
from datetime import datetime, timedelta, timezone


def parse_time(s: str) -> datetime:
    s = s.strip()

    # Epoch (seconds or milliseconds)
    if re.match(r'^\d{10}$', s):
        return datetime.fromtimestamp(int(s))
    if re.match(r'^\d{13}$', s):
        return datetime.fromtimestamp(int(s) / 1000)
    if re.match(r'^\d+\.?\d*$', s):
        return datetime.fromtimestamp(float(s))

    # Try common formats
    formats = [
        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M", "%Y-%m-%d",
        "%m/%d/%Y %H:%M:%S", "%m/%d/%Y",
        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y",
        "%B %d, %Y", "%b %d, %Y",
        "%B %d %Y", "%b %d %Y",
        "%d %B %Y", "%d %b %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue

    raise ValueError(f"Cannot parse: {s}")


def parse_duration(s: str) -> timedelta:
    total = timedelta()
    m = re.findall(r'(\d+)\s*(d|h|m|s|ms|w)', s.lower())
    if not m:
        raise ValueError(f"Cannot parse duration: {s}")
    for val, unit in m:
        v = int(val)
        if unit == 'w': total += timedelta(weeks=v)
        elif unit == 'd': total += timedelta(days=v)
        elif unit == 'h': total += timedelta(hours=v)
        elif unit == 'm': total += timedelta(minutes=v)
        elif unit == 's': total += timedelta(seconds=v)
        elif unit == 'ms': total += timedelta(milliseconds=v)
    return total


def fmt_duration(td: timedelta) -> str:
    total_secs = int(abs(td.total_seconds()))
    days = total_secs // 86400
    hours = (total_secs % 86400) // 3600
    mins = (total_secs % 3600) // 60
    secs = total_secs % 60
    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if mins: parts.append(f"{mins}m")
    if secs or not parts: parts.append(f"{secs}s")
    prefix = "-" if td.total_seconds() < 0 else ""
    return prefix + " ".join(parts)


def show_time(dt: datetime):
    epoch = int(dt.timestamp())
    epoch_ms = int(dt.timestamp() * 1000)
    iso = dt.isoformat()
    human = dt.strftime("%A, %B %d, %Y at %H:%M:%S")
    relative = fmt_duration(timedelta(seconds=time.time() - dt.timestamp()))

    print(f"  Epoch:    {epoch}")
    print(f"  Epoch ms: {epoch_ms}")
    print(f"  ISO 8601: {iso}")
    print(f"  Human:    {human}")
    print(f"  Relative: {relative} ago" if dt.timestamp() < time.time() else f"  Relative: in {relative}")
    print(f"  Day:      {dt.strftime('%A')} (day {dt.timetuple().tm_yday} of {365 + calendar.isleap(dt.year)})")
    print(f"  Week:     {dt.isocalendar()[1]}")


def cmd_now(args):
    show_time(datetime.now())


def cmd_convert(args):
    try:
        dt = parse_time(args.time)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    show_time(dt)


def cmd_diff(args):
    try:
        t1 = parse_time(args.time1)
        t2 = parse_time(args.time2)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    delta = t2 - t1
    print(f"  Duration:  {fmt_duration(delta)}")
    print(f"  Seconds:   {int(delta.total_seconds())}")
    print(f"  Minutes:   {delta.total_seconds()/60:.1f}")
    print(f"  Hours:     {delta.total_seconds()/3600:.1f}")
    print(f"  Days:      {delta.total_seconds()/86400:.2f}")


def cmd_add(args):
    try:
        dt = parse_time(args.time)
        dur = parse_duration(args.duration)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    result = dt + dur
    show_time(result)


def main():
    argv = sys.argv[1:]
    subcmds = {"now", "diff", "add"}

    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        return 0

    if argv[0] == "now":
        cmd_now(None)
        return 0

    if argv[0] == "diff" and len(argv) >= 3:
        class A: pass
        a = A(); a.time1 = argv[1]; a.time2 = argv[2]
        cmd_diff(a)
        return 0

    if argv[0] == "add" and len(argv) >= 3:
        class A: pass
        a = A(); a.time = argv[1]; a.duration = argv[2]
        cmd_add(a)
        return 0

    # Default: convert
    class A: pass
    a = A(); a.time = " ".join(argv)
    return cmd_convert(a)


if __name__ == "__main__":
    sys.exit(main() or 0)
