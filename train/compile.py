import json, sys, random
from pathlib import Path
from glob import glob
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from memelang import MemePGSQL, syntax

groups = ('employees','invoices','movies','followers')

nat2meme_system_prompt = f"Convert user prompt into MEMELANG query. Output only MEMELANG query.\nMEMELANG Syntax:\n\t{syntax}\n\tWS (whitespace) ONLY after table or column.\nSchema: "
sql2meme_system_prompt = "Convert SQL to MEMELANG. Output only MEMELANG query."

if __name__ == "__main__":
	total = 0
	with open('./openai.jsonl', "w", encoding="utf-8") as w:
		for group in groups:
			schema = open(f'./{group}/_schema.meme',encoding="utf-8").read()

			for file in glob(f'./{group}/ex*.meme'):
				with open(file, encoding='utf-8') as f: lines = [l.rstrip() for l in f]
				for i in range(len(lines) - 1):
					if lines[i].startswith('""" '):
						total+=1
						print(f'{file} {i} {lines[i]}')
						meme = MemePGSQL(lines[i + 1])
						w.write(json.dumps({
							"messages": [
								{"role": "system", "content": nat2meme_system_prompt+schema},
								{"role": "user", "content": lines[i][3:].strip()},
								{"role": "assistant", "content": lines[i + 1]}
							]
						}, ensure_ascii=False) + "\n")

						if random.randint(1, 10)>0:
							w.write(json.dumps({
								"messages": [
									{"role": "system", "content": sql2meme_system_prompt},
									{"role": "user", "content": str(meme.select()[0])},
									{"role": "assistant", "content": lines[i + 1]}
								]
							}, ensure_ascii=False) + "\n")
	
	print(f"\nTOTAL {total}\n")
	