#!/usr/bin/env python3
"""Double-booking experiment: many buyers race for a few rooms (or seats, or tickets).

    python runner/tools/sim_booking.py                       # 5 rooms, 20 buyers
    python runner/tools/sim_booking.py --rooms 3 --buyers 30

Three strategies, each run with real threads against a SQLite file:
  check-then-act     : read the remaining count, decide in the application, write back  -> oversells
  conditional-update : UPDATE ... SET remaining = remaining - 1 WHERE remaining > 0     -> exact
  unique-insert      : one row per (room, night) with a UNIQUE constraint, insert wins  -> exact
The unsafe variant sleeps 5 ms between the read and the write to make the race reliable; real races
need no sleep, they only happen less often, which is exactly why they reach production.
"""
import os
import sqlite3
import sys
import tempfile
import threading
import time


def setup(path, rooms):
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE inventory(id INTEGER PRIMARY KEY, remaining INTEGER)")
    db.execute("INSERT INTO inventory VALUES (1, ?)", (rooms,))
    db.execute("CREATE TABLE booking(room INTEGER, night TEXT, buyer INTEGER, UNIQUE(room, night))")
    db.execute("CREATE TABLE unit_booking(unit INTEGER PRIMARY KEY, buyer INTEGER)")
    db.commit()
    db.close()


def check_then_act(path, buyer, rooms):
    db = sqlite3.connect(path, timeout=30)
    left = db.execute("SELECT remaining FROM inventory WHERE id=1").fetchone()[0]
    if left > 0:
        time.sleep(0.005)
        db.execute("UPDATE inventory SET remaining=? WHERE id=1", (left - 1,))
        db.execute("INSERT INTO unit_booking(buyer) VALUES (?)", (buyer,))
        db.commit()
    db.close()


def conditional_update(path, buyer, rooms):
    db = sqlite3.connect(path, timeout=30)
    cur = db.execute("UPDATE inventory SET remaining = remaining - 1 WHERE id=1 AND remaining > 0")
    if cur.rowcount == 1:
        db.execute("INSERT INTO unit_booking(buyer) VALUES (?)", (buyer,))
    db.commit()
    db.close()


def unique_insert(path, buyer, rooms):
    db = sqlite3.connect(path, timeout=30)
    for room in range(1, rooms + 1):       # try each concrete room for the same night until one insert succeeds
        try:
            db.execute("INSERT INTO booking(room, night, buyer) VALUES (?, '2026-12-24', ?)", (room, buyer))
            db.execute("INSERT INTO unit_booking(buyer) VALUES (?)", (buyer,))
            db.commit()
            break
        except sqlite3.IntegrityError:
            db.rollback()
    db.close()


STRATEGIES = {"check-then-act": check_then_act, "conditional-update": conditional_update, "unique-insert": unique_insert}


def run(strategy, rooms=5, buyers=20):
    d = tempfile.mkdtemp()
    path = os.path.join(d, "hotel.db")
    setup(path, rooms)
    fn = STRATEGIES[strategy]
    ts = [threading.Thread(target=fn, args=(path, b, rooms)) for b in range(buyers)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    db = sqlite3.connect(path)
    booked = db.execute("SELECT COUNT(*) FROM unit_booking").fetchone()[0]
    db.close()
    os.remove(path)
    os.rmdir(d)
    return booked


def main():
    a = sys.argv[1:]
    rooms, buyers = 5, 20
    for i in range(0, len(a), 2):
        if a[i] == "--rooms":
            rooms = int(a[i + 1])
        elif a[i] == "--buyers":
            buyers = int(a[i + 1])
    print("%d rooms, %d buyers racing" % (rooms, buyers))
    for s in STRATEGIES:
        booked = run(s, rooms, buyers)
        print("  %-20s bookings made: %-3d %s" % (s, booked, "OVERSOLD by %d" % (booked - rooms) if booked > rooms else "ok"))


if __name__ == "__main__":
    main()
