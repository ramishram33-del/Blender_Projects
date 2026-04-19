"""
Room Packing via Integer Linear Programming (ILP)
Uses PuLP with CBC solver (free, no licence needed).
  pip install pulp

For larger instances, swap to OR-Tools CP-SAT:
  pip install ortools
"""

from dataclasses import dataclass
from typing import Optional
import pulp

# ── Data classes ────────────────────────────────────────────────────────────

@dataclass
class Room:
    name: str
    w: int                        # width  in grid cells
    h: int                        # height in grid cells
    required: bool = True         # must be placed (hard constraint)
    min_x: Optional[int] = None   # fixed column  (None = free)
    min_y: Optional[int] = None   # fixed row     (None = free)
    max_x: Optional[int] = None
    max_y: Optional[int] = None
    adjacent_to: Optional[str] = None   # soft adjacency preference

@dataclass
class PackingConstraints:
    floor_w: int     # grid cells
    floor_h: int     # grid cells
    gap: int = 1     # cells of separation between rooms (0 = wall-sharing)
    allow_rotation: bool = True


# ── ILP Model ───────────────────────────────────────────────────────────────

def build_and_solve(rooms: list[Room], c: PackingConstraints,
                    adjacency_weight: float = 0.5,
                    time_limit_sec: int = 60) -> dict:
    """
    Builds and solves the ILP model.

    Decision variables
    ------------------
    place[i][r][c]  = 1  iff room i's top-left corner is at (col=c, row=r)
    placed[i]       = 1  iff room i is placed anywhere
    rot[i]          = 1  iff room i is rotated (swaps w and h)
    adj[i][j]       = 1  iff rooms i and j share at least one wall (soft)

    Objective
    ---------
    Maximise  Σ placed[i]*area[i]  +  adjacency_weight * Σ adj[i][j]
    """

    FW, FH, G = c.floor_w, c.floor_h, c.gap
    N = len(rooms)

    prob = pulp.LpProblem("RoomPacking", pulp.LpMaximize)

    # ── 1. Decision variables ────────────────────────────────────────────────

    # place[i][(r,c)] = 1 if top-left of room i is at row r, col c
    place = {}
    for i, room in enumerate(rooms):
        orientations = [(room.w, room.h)]
        if c.allow_rotation and room.w != room.h:
            orientations.append((room.h, room.w))

        place[i] = {}
        for (rw, rh) in orientations:
            for r in range(FH - rh + 1):
                for col in range(FW - rw + 1):
                    # Apply position constraints
                    if room.min_x is not None and col < room.min_x: continue
                    if room.max_x is not None and col > room.max_x: continue
                    if room.min_y is not None and r  < room.min_y:  continue
                    if room.max_y is not None and r  > room.max_y:  continue
                    key = (r, col, rw, rh)
                    place[i][key] = pulp.LpVariable(
                        f"place_{i}_{r}_{col}_{rw}_{rh}", cat="Binary")

    # placed[i] = 1 if room i is placed at all
    placed = [pulp.LpVariable(f"placed_{i}", cat="Binary") for i in range(N)]

    # adjacency variables (pairs)
    adj_pairs = {}
    for i in range(N):
        nm_i = rooms[i].adjacent_to
        for j in range(i+1, N):
            if nm_i == rooms[j].name or rooms[j].adjacent_to == rooms[i].name:
                adj_pairs[(i,j)] = pulp.LpVariable(f"adj_{i}_{j}", cat="Binary")

    # ── 2. Objective ─────────────────────────────────────────────────────────

    area_reward = pulp.lpSum(
        placed[i] * rooms[i].w * rooms[i].h for i in range(N))
    adj_reward  = pulp.lpSum(
        v for v in adj_pairs.values())

    prob += area_reward + adjacency_weight * adj_reward

    # ── 3. Constraints ───────────────────────────────────────────────────────

    # (a) Each room placed at most once
    for i in range(N):
        prob += pulp.lpSum(place[i].values()) == placed[i], f"at_most_once_{i}"

    # (b) Required rooms must be placed
    for i, room in enumerate(rooms):
        if room.required:
            prob += placed[i] == 1, f"required_{i}"

    # (c) No overlap + gap
    # For every grid cell (r, c): sum of rooms covering it ≤ 1
    for r in range(FH):
        for col in range(FW):
            covering = []
            for i in range(N):
                for (pr, pc, rw, rh), var in place[i].items():
                    # Does this placement cover cell (r, col)?
                    # With gap G, a placed room at (pr,pc) with size rw×rh
                    # "blocks" cells [pr, pr+rh+G) × [pc, pc+rw+G)
                    # but only the actual room cells matter for overlap check
                    if pr <= r < pr + rh + G and pc <= col < pc + rw + G:
                        covering.append(var)
            if covering:
                prob += pulp.lpSum(covering) <= 1, f"no_overlap_{r}_{col}"

    # (d) Soft adjacency: adj[i][j]=1 only if rooms share a wall
    #     Simplified: adj[i][j] <= placed[i] and <= placed[j]
    for (i,j), av in adj_pairs.items():
        prob += av <= placed[i], f"adj_pi_{i}_{j}"
        prob += av <= placed[j], f"adj_pj_{i}_{j}"
        # Could add: if they ARE adjacent then av CAN be 1 (encoded via big-M)
        # For simplicity we let the solver decide whether to set it

    # ── 4. Solve ─────────────────────────────────────────────────────────────

    solver = pulp.PULP_CBC_CMD(msg=1, timeLimit=time_limit_sec)
    status = prob.solve(solver)

    # ── 5. Extract solution ──────────────────────────────────────────────────

    result_placed = []
    result_failed = []

    for i, room in enumerate(rooms):
        found = False
        for (pr, pc, rw, rh), var in place[i].items():
            if pulp.value(var) and pulp.value(var) > 0.5:
                result_placed.append({
                    "name": room.name,
                    "x": pc, "y": pr,
                    "w": rw, "h": rh,
                    "area": rw * rh,
                    "rotated": (rw != room.w)
                })
                found = True
                break
        if not found:
            result_failed.append(room.name)

    total_area   = FW * FH
    used_area    = sum(r["area"] for r in result_placed)
    efficiency   = used_area / total_area * 100

    return {
        "status":       pulp.LpStatus[status],
        "placed":       result_placed,
        "failed":       result_failed,
        "efficiency":   efficiency,
        "used_area":    used_area,
        "total_area":   total_area,
        "objective":    pulp.value(prob.objective),
    }


def print_solution(sol: dict, c: PackingConstraints):
    print(f"\n{'='*55}")
    print(f"Status      : {sol['status']}")
    print(f"Floor       : {c.floor_w} × {c.floor_h} = {sol['total_area']} cells")
    print(f"Efficiency  : {sol['efficiency']:.1f}%  "
          f"({sol['used_area']}/{sol['total_area']} cells)")
    print(f"Rooms placed: {len(sol['placed'])}   "
          f"Failed: {len(sol['failed'])}")
    print(f"{'='*55}")
    for r in sorted(sol["placed"], key=lambda x: (x["y"], x["x"])):
        rot = " [rotated]" if r["rotated"] else ""
        print(f"  {r['name']:<18}  pos=({r['x']:>2},{r['y']:>2})  "
              f"size={r['w']}×{r['h']}{rot}")
    if sol["failed"]:
        print(f"\n  Could NOT place: {', '.join(sol['failed'])}")


def ascii_floor(sol: dict, c: PackingConstraints):
    """Simple ASCII art of the floor plan."""
    grid = [["·"] * c.floor_w for _ in range(c.floor_h)]
    labels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for idx, r in enumerate(sol["placed"]):
        ch = labels[idx % len(labels)]
        for row in range(r["y"], r["y"] + r["h"]):
            for col in range(r["x"], r["x"] + r["w"]):
                grid[row][col] = ch
    print("\n  Floor plan (each char = 1 cell):\n")
    for row in grid:
        print("  " + " ".join(row))
    print()
    for idx, r in enumerate(sol["placed"]):
        print(f"  {labels[idx]} = {r['name']}")


# ── Example ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Grid resolution: 1 cell = 0.5 m  →  20×15 m floor = 40×30 cells
    rooms = [
        Room("Living Room", w=10, h=8,  required=True,  adjacent_to="Dining"),
        Room("Master Bed",  w=8,  h=8,  required=True),
        Room("Kitchen",     w=6,  h=6,  required=True,  adjacent_to="Dining"),
        Room("Bed 2",       w=7,  h=6,  required=True),
        Room("Bathroom",    w=5,  h=4,  required=True),
        Room("Study",       w=6,  h=5,  required=False),
        Room("Dining",      w=7,  h=6,  required=True),
        Room("Laundry",     w=4,  h=4,  required=False),
    ]

    constraints = PackingConstraints(
        floor_w=40,
        floor_h=30,
        gap=1,              # 1-cell gap = 0.5 m corridor/wall
        allow_rotation=True,
    )

    print("Solving ILP room packing …")
    sol = build_and_solve(rooms, constraints,
                          adjacency_weight=0.5,
                          time_limit_sec=60)

    print_solution(sol, constraints)
    ascii_floor(sol, constraints)