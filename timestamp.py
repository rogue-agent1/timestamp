#!/usr/bin/env python3
"""Timestamp converter — Unix epoch, ISO 8601, RFC 2822, relative."""
import sys, time
from datetime import datetime, timezone
def now():
    t = time.time(); dt = datetime.fromtimestamp(t, timezone.utc)
    print(f"Unix:   {int(t)}")
    print(f"Millis: {int(t*1000)}")
    print(f"ISO:    {dt.isoformat()}")
    print(f"UTC:    {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Local:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
def from_unix(ts):
    dt = datetime.fromtimestamp(float(ts), timezone.utc)
    print(f"Unix {ts} = {dt.isoformat()}")
    print(f"  {dt.strftime('%A, %B %d, %Y at %H:%M:%S UTC')}")
    diff = time.time() - float(ts)
    if abs(diff) < 3600: print(f"  {abs(diff):.0f}s {'ago' if diff > 0 else 'from now'}")
    elif abs(diff) < 86400: print(f"  {abs(diff)/3600:.1f}h {'ago' if diff > 0 else 'from now'}")
    else: print(f"  {abs(diff)/86400:.1f}d {'ago' if diff > 0 else 'from now'}")
if __name__ == "__main__":
    if len(sys.argv) < 2: now()
    else: from_unix(sys.argv[1])
