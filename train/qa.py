import json, sys, re
from pathlib import Path
from itertools import permutations
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from memelang import Grid

groups = ('employees','invoices','movies','followers')


if __name__ == "__main__":
	paths = sorted(Path(".").glob("*/*.meme"))
	for p in paths:
		lines=open(p, "r", encoding="utf-8", errors="replace").readlines()
		for i in range(len(lines)):
			if lines[i].startswith('"""'):
				print(f'""" FILE {p} """')
				print(lines[i][:-1])
				grid=Grid(lines[i+1])
				sel = grid.select()
				print(str(grid))
				if sel: print(str(sel[0]))
				print()
