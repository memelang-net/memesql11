import sys, os, json, random, re, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from openai import OpenAI
from memelang import Grid

iterations = 4
experit = 30
exfiles = 3

def chat(model, content):
	chat = client.chat.completions.create(model=model, messages=[{"role":"user","content":content}])
	return chat.choices[0].message.content.strip()

def inc():
	files = Path(f'./{group}').glob('ex*.meme')
	vals = [int(m.group(1)) for f in files for m in [re.search(r'^ex(\d{3})\.meme$', f.name)] if m]
	n = max(vals) if vals else 0
	return f'{n+1:03d}'

def normalize(raw: str):
	return str(Grid(raw)).replace('; ',';')

if __name__ == "__main__":
	group = sys.argv[1]

	# Read files
	syntax = open('./prompt_syntax.md',encoding="utf-8").read()
	errcheck = open('./prompt_check.md',encoding="utf-8").read()
	schema = open(f'./{group}/_schema.meme',encoding="utf-8").read()
	paths = [p for p in Path(f'./{group}').glob('ex*.meme') if p.is_file()]
	examples = ''.join(p.read_text(encoding='utf-8') for p in paths[-4:])

	# OpenAI
	model_generate = 'gpt-5'
	model_check = 'gpt-5'
	OPENAI_API_KEY=open('../../../openai.key',encoding="utf-8").read()
	client = OpenAI(api_key=OPENAI_API_KEY)

	#task = f'demonstrating `@ @ @` self-join combined with other syntax elements'
	task = f'demonstrating two `@` joins with `:(min|max|sum|cnt|avg)` and `:grp` and `:(asc|des)(<|>|<=|>=)` syntax elements'

	prompt_generate = f'''
	Generate {experit} distinct LLM training examples for the following DSL, {task}. Use varied tables. Output only JSON as `[{{"input":"natural language query","output":"MEMELANG query"}}]`.
	* Use distinct phrasing and patterning for each input in the form a user's search query. Omit phrases like "Give me" or "Return".
	* NEVER use "capture" "remember" "bind" or any program instructions in user
	* Use only ASCII characters
	* Use only exampled rules - do not invent new rules
	* Use only exampled syntax - do not invent new syntax
	* Use only absolute dates - do not use relative dates
	* Avoid tokens that could trigger a warning like "die" or "dead"

	{syntax}

	{errcheck}

	DB SCHEMA:
	{schema}

	EXAMPLES (`""" nat lang """\\nmemelang\\n\\n`):
	```memelang
	{examples}
	```
	'''

	prompt_check = f'''
	This is LLM training data for a query language DSL. Check each example in *CHECK EXAMPLES*. Output only JSON as `[true,false,true,...]`, one for each example, with `true` for passed and `false` for erred. DO NOT WRITE CODE.

	{errcheck}

	{syntax}

	DB SCHEMA:
	{schema}

	CORRECT EXAMPLES (`""" nat lang """\\nmemelang\\n\\n`):
	```memelang
	{examples}
	```

	CHECK EXAMPLES (`""" nat lang """\\nmemelang\\n\\n`):
	```memelang
	'''

	for _ in range(100):
		nextfile = inc()
		print(f'./{group}/ex{nextfile}.meme', flush=True)
		with open(f'./{group}/ex{nextfile}.meme', "x", encoding="utf-8") as f:
			for _ in range(iterations):
				norm_exs = []
				raw_exs  = json.loads(chat(model_generate, prompt_generate))

				for i,ex in enumerate(raw_exs):
					try: norm_exs.append({'input':ex['input'], 'output':normalize(ex['output'])})
					except: pass

				checks  = json.loads(chat(model_check, prompt_check+json.dumps(norm_exs)+'```'))
				if len(checks)!=len(norm_exs): continue
				
				for i, ex in enumerate(norm_exs):
					if not checks[i]: continue
					print(f'""" {ex['input']} """\n{ex['output']}\n\n', flush=True)
					f.write(f'""" {ex['input']} """\n{ex['output']}\n\n')
					f.flush()
					os.fsync(f.fileno())

