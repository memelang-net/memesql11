from flask import Flask, request, render_template_string
from openai import OpenAI
from memelang import syntax
import os

models = {
	'mini': "ft:gpt-4.1-mini-2025-04-14:holtwork:memelang-09-33:CSnfzaNz"
}

OPENAI_API_KEY=open('../../../openai.key',encoding="utf-8").read()
system_prompt = f'Convert user prompt into MEMELANG query. Output only MEMELANG query.\nMEMELANG Syntax: {syntax}\nTable schema:'
def_schema = '% mode tab;roles id :ROL=ID;:TYP=INT;>0;rating :DESC="Numeric 0-5 star rating of performance";:TYP=DEC;>0;<=5;actor :DESC="Actor\'s full name";:TYP=STR;movie :DESC="Movie\'s full name";:TYP=STR;;actors id :ROL=ID;:TYP=INT;>0;name :DESC="Actor\'s full name";:TYP=STR;age :DESC="Actor\'s age in years";:TYP=INT;>=0;<200;;movies id :ROL=ID;:TYP=INT;>0;description :DESC="Brief description of movie plot";:TYP=STR;year;:DESC="Year of production AD";>1800;<2100;genre scifi,drama,comedy,documentary;title;:DESC="Full movie title";:TYP=STR;;actors name _;roles actor @;;movies title _;roles movie @;;'
def_prompt = "Second page of movies ordered by title (25 per page)"

app = Flask(__name__)

HTML = '''
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Memelang from Natrual Language</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:800px;margin:40px auto;padding:0 16px}
label{display:block;margin-top:12px}
textarea{width:100%;padding:8px}
button{margin-top:12px;padding:8px 12px;cursor:pointer}
#out{white-space:pre-wrap;border:1px solid #ddd;padding:12px;border-radius:8px;margin-top:16px}
</style>
</head>
<body>
<h1>Memelang from Natrual Language</h1>
<form method="POST">
<label>Schema</label>
<textarea name="schema" rows="8">{{ schema|e }}</textarea>
<label>User query</label>
<textarea name="prompt" rows="3">{{ prompt|e }}</textarea>
<label>Memelang query</label>
<textarea name="memelang" disabled="true" rows="3">{{ output|e }}</textarea>
<button type="submit">Translate</button>
</form>
</body>
</html>
'''

@app.route('/', methods=['GET','POST'])
def index():
	client = OpenAI(api_key=OPENAI_API_KEY)
	schema = request.form.get('schema','') if request.method == 'POST' else def_schema
	prompt = request.form.get('prompt','') if request.method == 'POST' else def_prompt
	output = ''
	if request.method == 'POST':
		for model in models:
			r = client.chat.completions.create(
				model=models[model],
				messages=[
					{'role':'system','content':system_prompt+schema},
					{'role':'user','content':prompt}
				]
			)
			output += '% model ' + model + '; '
			output += r.choices[0].message.content if r.choices and r.choices[0].message and r.choices[0].message.content else ''
			output += "\n"
	return render_template_string(HTML, schema=schema, prompt=prompt, output=output)

if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.getenv('PORT','5000')), debug=False)
