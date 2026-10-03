import time
import statistics
import msvcrt
import sys

WINDOW_SIZE = 32
# How many multiples of your mean interval count as a burst break?
THRESHOLD_FACTOR = 2.0

def format_number(x, digits=2):
    return f"{x:.{digits}f}"

def main():
    print("Tap Tracker — press any key to tap, ESC to quit.")
    timestamps = []

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\x1b':  # ESC
                print("\nExiting. Stay tuned!")
                break

            now = time.time() * 1000  # current time in ms

            # Compute dynamic threshold
            if len(timestamps) >= 2:
                # Calculate mean interval of existing burst
                intervals = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])]
                mean_interval = statistics.mean(intervals[-WINDOW_SIZE:])
                burst_threshold_ms = THRESHOLD_FACTOR * mean_interval
            else:
                # Fallback threshold before we have enough data
                burst_threshold_ms = 1000.0

            # Burst reset logic
            if timestamps and (now - timestamps[-1] > burst_threshold_ms):
                # too long since last tap → new burst
                timestamps = [now]
            else:
                timestamps.append(now)
                if len(timestamps) > WINDOW_SIZE + 1:
                    timestamps.pop(0)

            # Compute stats once we have at least two taps in the current burst
            if len(timestamps) >= 2:
                intervals = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])]
                recent = intervals[-WINDOW_SIZE:]
                mean_interval = statistics.mean(recent)
                bpm = 15000.0 / mean_interval
                stdev = statistics.pstdev(recent) if len(recent) > 1 else 0.0
                ur = 10 * stdev

                sys.stdout.write(
                    f"\rBPM: {format_number(bpm)} | UR: {format_number(ur)}    "
                )
                sys.stdout.flush()
            else:
                sys.stdout.write("\rWaiting for burst...   ")
                sys.stdout.flush()

        time.sleep(0.005)

if __name__ == "__main__":
    main()
