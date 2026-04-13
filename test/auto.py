import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI
from memelang import MemePGSQL, syntax
import os
from .conf import *



OPENAI_API_KEY=open('../../../openai.key',encoding="utf-8").read()
meme_system_prompt = f'Convert user prompt into MEMELANG query. Output only MEMELANG query.\nSyntax: {syntax}\nSchema:'
sql_system_prompt = f'Convert user prompt into SQL query. Output only SQL.\nSchema:'

sqlize_prompt = f'Convert this DSL DDL into SQL: '+examples['employees']['schema']


if __name__ == "__main__":
	client = OpenAI(api_key=OPENAI_API_KEY)

	with open(f'./auto.meme', 'w', encoding="utf-8") as f:
		for scheme in examples:
			print(scheme)
			if not examples[scheme]['active']: continue
			for ex in examples[scheme]['examples']:
				print(ex['input'])
				print(ex['output'])

				for model in tmodels:
					r = client.chat.completions.create(
						temperature=0.1,
						model=tmodels[model],
						messages=[
							{'role':'system','content':meme_system_prompt+examples[scheme]['schema']},
							{'role':'user','content':ex['input']}
						]
					)
					query = r.choices[0].message.content if r.choices and r.choices[0].message and r.choices[0].message.content else ''

					try: MemePGSQL(query)
					except Exception as e:
						parse_error = str(e)
						print(f'{query} [ERROR] {parse_error}')
						r = client.chat.completions.create(
							model=models[model],
							messages=[
								{'role':'system','content':meme_system_prompt+examples[scheme]['schema']},
								{'role':'user','content':ex['input']},
								{'role':'assistant','content':query},
								{'role':'user','content':f'Previous response has syntax error: {parse_error}. Fix. Correct syntax is `{syntax}`\n'},
							]
						)
						query = r.choices[0].message.content if r.choices and r.choices[0].message and r.choices[0].message.content else ''

					print(query+"\n", flush=True)

					f.write(f"""" {ex['input']}\n{ex['output']}\n{query}\n\n") """
					f.flush()
					os.fsync(f.fileno())
