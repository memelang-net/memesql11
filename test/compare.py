import sys, os, json, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve()))

from openai import OpenAI
from memelang import MemePGSQL, syntax
from conf import *

OPENAI_API_KEY = open('../../../openai.key',encoding="utf-8").read()
schema = examples['employees']['schema']
meme_system_prompt = f'Convert user prompt into MEMELANG query. Output only MEMELANG query.\nSyntax: {syntax}\nTable schema:'
sql_system_prompt = f'Convert user prompt into SQL query. Output only SQL, NO MARKDOWN.\nSchema:'
sqlize_prompt = 'Convert this DSL DDL into SQL. Use comments for description. Output only SQL, NO MARKDOWN.'

if __name__ == "__main__":
	client = OpenAI(api_key=OPENAI_API_KEY)

	chat = client.chat.completions.create(model='gpt-5-mini', messages=[
		{'role':'system','content':sqlize_prompt},
		{"role":"user","content":schema}
	])
	sql_schema = re.sub(r'\s+', ' ', chat.choices[0].message.content).strip()

	print('""" SCHEMA') """
	print(sql_schema)
	print(schema)
	print('',flush=True)

	for ex in examples['employees']['examples']:
		print('""" '+ex['input']) """

		chat = client.chat.completions.create(model='gpt-4.1-mini', messages=[
			{'role':'system','content':sql_system_prompt+sql_schema},
			{"role":"user","content":ex['input']}
		])
		print(re.sub(r'\s+', ' ', chat.choices[0].message.content).strip())
		print(str(chat.usage.prompt_tokens) +' '+ str(chat.usage.completion_tokens) +' '+ str(chat.usage.total_tokens))

		chat2 = client.chat.completions.create(model=SFT, messages=[
			{'role':'system','content':meme_system_prompt+schema},
			{"role":"user","content":ex['input']}
		])
		print(chat2.choices[0].message.content.strip())
		print(str(chat2.usage.prompt_tokens) +' '+ str(chat2.usage.completion_tokens) +' '+ str(chat2.usage.total_tokens))

		print('',flush=True)
