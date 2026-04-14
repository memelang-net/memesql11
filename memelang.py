# info@memelang.net | (c)2026 HOLTWORK LLC | Patented
# MEMELANG is a terse query DSL IR for LLM text-to-SQL
# Axial grammar: Axis2 -> Axis1 -> Axis0 -> Cell
# Whitespaces are syntactic and trigger "new Cell"
# Never space between operator/comparator/comma/flag and values

MEMELANG_VER = 11.04

basic_syntax = '[table WS] [column WS] [":$" var][":" ("min"|"max"|"cnt"|"sum"|"avg"|"last"|"grp")] [":" ("asc"|"des")] ["<=>" "\"" string "\""] [("="|"!="|">"|"<"|">="|"<="|"~"|"!~") (string|int|float|("$" var)|"@"|"_")] ";"'

examples = '''
%mode=tab;
roles id :int>0; rating :DESC="Decimal 0-5 star rating of performance";:dec>0.0;<=5; actor :DESC="Actor's full name";:str; movie :DESC="Movie's full name";:str; character :DESC="Character's full name";:str;;
actors id :int>0; name :DESC="Actor's full name";:str; age :DESC="Actor's age in years";:int>=0;<200;;
movies id :int>0; description :DESC="Brief description of movie plot";:str; year :DESC="Year of production AD";:int>1800;<2100; genre scifi,drama,comedy,documentary;:str; title :DESC="Full movie title";:str;;
actors name _; roles actor @;;
movies title _; roles movie @;;
roles id :gct=1;;
roles movie :grp; actor :grp; character :gct=1;;
actors id :gct=1;;
movies id :gct=1;;

%mode=qry;
""" All movies """
movies _ _;;

""" Every role """
roles _ _;;

""" Titles and descriptions for movies """
movies title _; description _;;

""" Actor name and ages """
actors name _; age _;;

""" Actors age 41 years or older """
actors age >=41; _;;

""" Role 567 and 8901 """
roles id 567,8901; _;;

""" Films with dystopian society narratives sim>.33 """
movies description <=>"dystopian"<0.33; _;;

""" Movies titled with Star released in 1977 or 1980 """
movies title ~"Star"; year 1977,1980; _;;

""" Actors named like Ana aged 20 to 35 inclusive """
actors name ~"Ana"; age >=20;<=35; _;;

""" Roles rated below 1.5 for movies before 1980 """
movies year <1980; title _; roles movie @; rating <1.5; _;;

""" Roles sort rating descending, movie descending """
roles rating :des; movie :des;;

""" All movies before 1970 ordered by year ascending """
movies year :asc<1970; _;;

""" Average performer rating at least 4.2 """
roles rating :avg>=4.2; actor :grp;;

""" Minimum role rating by actor, low to high """
roles rating :min:asc; actor :grp;;

""" Roles in movies mentioning robot rated 3+ """
movies description <=>"robot"<=$sim; title _; roles movie @; rating >=3;;

""" Costars seen with Bruce Willis or Uma Thurman """
roles actor :$a~"Bruce Willis","Uma Thurman"; movie _;@ @ @; actor !$a;;

""" War stories before 1980: top 12 movies by minimum role rating """
movies year <1980; description <=>"war"<=$sim; title :grp; roles movie @; rating :min:des;%beg=0;%lim=12;;

""" Roles for movies Hero or House of Flying Daggers where actor name includes Li, actor A-Z """
movies title "Hero","House of Flying Daggers"; roles movie @; actor :asc~"Li";;

""" Titles containing Here about robots between 1900 and 2000 """
movies title ~"Hero"; description <=>"robot"; year >=1900; <=2000;;
%tab=movies;  #%val; %col=title; ~"Hero"; %col=description; <=>"robot"; %col=year; >=1900; <=2000;;
%tab=movies; #title #description #year; ~"Hero" <=>"robot" >=1900; <=2000;;
%tab=movies; #title; ~"Hero"; #description; <=>"robot"; #year; >=1900; <=2000;;
#%tab #%val; movies :#title~"Hero"; :#description<=>"robot"; :#year>=1900; <=2000;;
'''

import re, sys, json
from typing import Optional, Union, List, Iterator, Pattern, Any
Err = SyntaxError

### SYNTAX ###

CELL_PATTERN = (
	('QUO',   	r'"(?:[^"\\\n\r]|\\.)*"'),
	('EMB',		r'\[(?:-?\d+(?:\.\d+)?)(?:\s*,\s*-?\d+(?:\.\d+)?)*\]'),
	('MOD',		r'<->|<=>|<#>'),
	('CMP', 	r'>=|<=|!~|!=|=|>|<|~|!'),
	('BIND',	r':\$\w+'),
	('FLAG',	r':[a-zA-Z]+'),
	('VAR',		r'\$\w+'),
	('REL',  	r'@\d?|\^'),
	('WLD', 	r'_'),
	('EVAR', 	r'%[a-zA-Z0-9_]+'),
	('SLOT', 	r'#%?[a-zA-Z0-9_]+'),
	('ASSN', 	r':#[a-zA-Z0-9_]+'),
	('TIM',		r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'),
	('DEC',		r'-?\d*\.\d+'),
	('INT',		r'-?\d+'),
	('ALN',		r'[A-Za-z][A-Za-z0-9_]*'),
	('OR',		r','),
	('WS',		r'\s+'),
	('MISMATCH', r'.'),
)

CANON = {'!':'!='}

CELL_REGEX=re.compile("|".join(f"(?P<{k}>{p})" for k, p in CELL_PATTERN))

PAD_MODES = {'qry','tab'}
FLAG_KINDS = {'FLAG','BIND','EVAR','ASSN'}
LIT_KINDS = {'TIM','DEC','INT','ALN','QUO','EMB'}
VAR_KINDS = {'VAR','WLD','REL','EVAR','SLOT'}
DAT_KINDS = LIT_KINDS | VAR_KINDS
RELCOORD = {
	'@0': ['-1','-1'],
	'@1': ['-1','-2'],
	'@2': ['-1','-3'],
	'@3': ['-1','-4'],
	'@4': ['-1','-5'],
	'@'  : ['-1','+0'],
	'^'  : ['-1','end','+0'],
}


# Atomic token
class Tok:
	def __init__(self, kind: str, src: str, canon: Optional[str] = None):
		self.kind = kind
		self.src = src
		canon = src if canon is None else canon
		self.canon = CANON.get(canon) or canon
		parser = {'QUO': json.loads, 'EMB': json.loads, 'DEC': float, 'INT': int}.get(kind)
		self.dat = parser(src) if parser else src
	def __str__(self): return self.src
	def __repr__(self): return self.canon
	def __eq__(self, other): return repr(self) == repr(other)
	def __hash__(self): return hash(self.src)
	def __bool__(self): return bool(self.src)


TOK_NULL = Tok('NULL', '')

# Sequence of tokens
class Seq(list[Tok]):
	opr: Tok = TOK_NULL
	def __init__(self, *items):
		super().__init__(items)
		self.opr = TOK_NULL
	def __str__(self): return self.opr.src.join([str(t) for t in self if len(str(t)) or t.kind=='HOLD'])
	def __repr__(self): return self.opr.src.join([repr(t) for t in self])


# Predicate expression
class Cell:
	flag: Seq
	left: Seq
	comp: Tok
	right: Seq
	padded = False

	def __init__(self, src: str):
		self.left = Seq()
		self.flag = Seq()
		self.comp = Tok('EQL', '', '=')
		self.right = Seq(Tok('WLD', '', '_'))

		toks = []
		for m in CELL_REGEX.finditer(src):
			kind = m.lastgroup
			text = m.group()
			if kind == 'WS': continue
			if kind == 'MISMATCH': raise Err(f'E_TOK {text!r}')
			toks.append(Tok(kind, text))

		i, n = 0, len(toks)

		def peek(): return toks[i].kind if i < n else ''

		def take():
			nonlocal i
			if i >= n: raise Err('E_EOF')
			t = toks[i]
			i += 1
			return t

		# FLAGS
		while peek() in FLAG_KINDS:
			self.flag.append(take())

		# LEFT (prefix MOD)
		if peek() == 'MOD':
			self.left.opr = take()
			self.left.append(Tok('HOLD', ''))
			t = take()
			if not t.kind in DAT_KINDS: raise Err('E_TERM_DAT')
			self.left.append(t)

		# COMPARATOR
		if peek() == 'CMP':
			self.comp = take()
			if not peek() in DAT_KINDS: raise Err('E_DAT')

		# RIGHT (values, OR-joined)
		if peek() in DAT_KINDS:
			self.right.clear()
			while peek() in DAT_KINDS:
				self.right.append(take())
				if peek() == 'OR':
					self.right.opr = take()
					if not peek() in DAT_KINDS: raise Err('E_OR_TRAIL')

		if i != n: raise Err(f'E_EXPR_TRAIL {toks[i:]}')

	# PLACEHOLDER: OVERWRITE WITH YOUR EMBEDDING FUNCTION
	def vectorize(self, tok: Tok) -> Tok:
		if tok.kind == 'EMB': return tok
		if tok.kind not in {'QUO', 'ALN'}: raise Err('E_EMBED')
		return Tok('EMB', json.dumps([0.1, 0.2]))

	@property
	def single(self) -> Tok:
		return self.right[0] if self.comp.canon == '=' and len(self.right) == 1 else TOK_NULL

	@property
	def literal(self) -> Tok:
		tok = self.single
		return tok if tok.kind in LIT_KINDS else TOK_NULL

	def find(self, kind:str) -> Tok:
		return next((flag for flag in self.flag if flag.kind == kind), TOK_NULL)


	def bind(self, tok: Tok):
		if tok not in self.flag: self.flag.append(tok)

	def __str__(self) -> str: return f"{self.flag}{self.left}{self.comp}{self.right}"

	def __repr__(self) -> str: return f"{self.flag!r}{self.left!r}{self.comp!r}{self.right!r}"

	def __bool__(self) -> bool: return bool(self.flag or self.left or self.right)


### GRAMMAR ###

class Axis(list):
	src: str = ''
	sep: str = None			# SEPERATOR TOKEN
	sepreg: str = None		# SEPERATOR REG EXP
	sepstr: str = None		# SEPERATOR OUT
	empt: bool = False		# ALLOW EMPTY SUB-AXES?
	sub = None				# SUB-AXIS NAME

	def __init__(self, src: str):
		if self.sep is None: raise Err('E_AXIS_SEP')
		if not self.sepreg: self.sepreg = re.escape(self.sep)
		if not self.sepstr: self.sepstr = self.sep + ' '
		self.src= src
		self.parse(src.strip())

	@property
	def regex(self) -> Pattern[str]:
		return re.compile(rf'''
		(?P<COMM>"""(?:(?!""")[^\n\r\\]|\\.)*""")|
		(?P<EXPQ>"(?:[^"\\\n\r]|\\.)*")|
		(?P<SEP>{self.sepreg})|
		(?P<EXPM>[^"{re.escape(self.sep[0])}]+)|
		(?P<EXPS>.)
		''', re.VERBOSE)

	def parse(self, src: str):
		exprs: List[str] = []

		for m in self.regex.finditer(src):
			if m.lastgroup == 'SEP':
				if exprs or self.empt:
					self.append(self.sub("".join(exprs)))
					exprs.clear()
			elif m.lastgroup != 'COMM': exprs.append(m.group())

		# debuffer expression
		if exprs: self.append(self.sub("".join(exprs)))

	def pull(self, coords):
		value = self
		for coord in coords: value = value[coord]
		return value

	def __str__(self) -> str:
		items = [str(t) for t in self]
		return self.sepstr.join([s for s in items if (s or self.empt)])


# "Table column value" semantic sequence of Cell predicates
class Axis0(Axis):
	sep = ' '
	sepstr = ' '
	sepreg = r'\s+'
	sub = Cell

# AND-joined sequence of Axis0
class Axis1(Axis):
	sep = ';'
	sub = Axis0

# OR-joined sequence of Axis1
class Axis2(Axis):
	sep = ';;'
	sub = Axis1

	@staticmethod
	def coordrel(coords, rel):
		rel = ["+0"] * max(0, len(coords) - len(rel)) + [str(op) for op in rel]
		out = []

		for coord, op in zip(coords, rel):
			if op == "end": v=-1
			elif (v:=(coord + int(op)))<0: raise ValueError('E_REL_BIND')
			out.append(v)

		return out

	# Rectangularize
	# Left-pad Axis0
	# Replace relatives `@` with coordinate vars `$x_y_z`
	# Assign slots
	def rect(self):
		env = {'mode':'qry'}
		slots = [Tok('EVAR','','%tab'),  Tok('EVAR','','%col'), Tok('EVAR','','%val')]

		for idx2, axis1 in enumerate(self):
			idx = [idx2, None, None]

			for idx1, axis0 in enumerate(axis1):
				if not axis0: continue
				idx[1:] = [idx1, None]

				# %KEY=VAL %KEY=VAL
				if bool(axis0[0].find('EVAR')):
					for cell in axis0:
						if not bool(cell.find('EVAR')): raise Err('E_AXIS_MET')
						env[cell.find('EVAR').canon[1:]] = cell.single.dat
					continue

				#SLOT #SLOT #SLOT
				if axis0[0].single.kind=='SLOT':
					slots=[]
					for cell in axis0:
						if cell.single.kind!='SLOT': raise Err('E_AXIS_SLOT')
						if cell.single.canon[1]=='%': slots.append(Tok('EVAR', '', cell.single.canon[1:]))
						else: slots.append(Tok('ASSN','',':'+cell.single.canon))
					continue
	
				if env['mode'] not in PAD_MODES: continue

				# Pad Axis0
				axis0len=len(slots)
				if len(axis0) > axis0len: raise Err('E_AXIS0_LONG')
				for _ in range(axis0len - len(axis0)):
					cell = axis0.sub('@')
					cell.padded=True
					axis0.insert(0, cell)

				for idx0, cell in enumerate(axis0):
					idx[2] = idx0

					# Assign slot
					cell.bind(slots[idx0])

					# Replace relative tokens with coordinate vars
					for seq in (cell.left, cell.right):
						for n, tok in enumerate(seq):
							if tok.kind!='REL': continue

							coords=self.coordrel(idx, RELCOORD[tok.canon])
							src=self.pull(coords)

							if src.literal.kind != 'NULL':
								seq[n] = src.literal
								continue

							name = '$'+'_'.join(map(str, coords)).replace('-1','E')
							seq[n] = Tok('VAR', '', name)
							src.bind(Tok('BIND', '', ':'+name))

### PG SQL ###

PH = '%s'
Param = List[Union[int, float, str, list]]

class SQL:
	def __init__(self, sql: str = '', param: Optional[Param] = None):
		self.sql = sql
		self.param = [] if param is None else list(param)

	def sql_value(self) -> "SQL":
		return self

	def __str__(self) -> str:
		sql = self.sql
		for p in self.param: sql = sql.replace(PH, json.dumps(p), 1)
		return sql

	def __repr__(self) -> str: return str((self.sql, self.param))

	@staticmethod
	def uniq(terms: "SQL") -> list["SQL"]:
		out, seen = [], set()
		for term in terms:
			if term is None: continue
			key = (term.sql, tuple(map(repr, term.param)))
			if key in seen: continue
			seen.add(key)
			out.append(term)
		return out


class CellSQL(Cell):
	flag2agg = {':cnt':'COUNT', ':sum':'SUM', ':avg':'AVG', ':min':'MIN', ':max':'MAX', ':last':'MAX'}
	cmp2sql  = {'~':' ILIKE ', '!~':' NOT ILIKE '}
	mod2sql  = {}

	def __init__(self, src: str):
		super().__init__(src)
		self.base = self.alias = ''
		self.param = []
		flags = {t.canon for t in self.flag if t.kind == 'FLAG'}
		self.agg = next((sql for flag, sql in self.flag2agg.items() if flag in flags), '')
		self.grouped = ':grp' in flags
		self.sort = 'ASC' if ':asc' in flags else 'DESC' if ':des' in flags else ''

	def deref(self, bind: dict[str, SQL], with_agg: bool = True) -> Iterator[SQL]:
		for t in self.right:
			if t.kind == 'VAR':
				key = t.canon[1:]
				if key not in bind: raise Err(f'E_VAR_BIND {key}')
				ref = bind[key]
			else:
				yield SQL(PH, [t.dat])
				continue

			if isinstance(ref, CellSQL): yield ref.sql_value(with_agg=with_agg)
			else: yield ref.sql_value()

	@property
	def sql_groupby(self) -> Optional[SQL]:
		if not self.grouped: return None
		if self.agg: raise Err('E_GRP_AGG')
		return SQL(self.base, self.param)

	def sql_value(self, grouped: bool = False, alias: bool = False, order: bool = False, with_agg: bool = True) -> SQL:
		sql, param = self.base, list(self.param)
		if self.left.opr.kind == 'MOD':
			sql = f'({sql}{self.left.opr.canon}{PH}::VECTOR)'
			param.append(self.vectorize(self.left[1]).canon)
		agg = self.agg or ('MAX' if grouped and not self.grouped else '') if with_agg else ''
		if agg: sql = f'{agg}({sql})'
		if alias and self.alias: sql = f'{sql} AS {self.alias}'
		if order and self.sort: sql = f'{sql} {self.sort}'
		return SQL(sql, param)

	def sql_clause(self, bind: dict[str, SQL]) -> Optional[tuple[str, SQL]]:
		if not self.right or self.single.canon == '_': return None

		left = self.sql_value()
		rights = list(self.deref(bind, with_agg=bool(self.agg)))
		comp = self.comp.canon
		sqlcomp = self.cmp2sql.get(self.comp.canon) or self.comp.canon

		if comp in {'>', '<', '>=', '<='} and len(rights) != 1: raise Err('E_COMP_OR')

		items, params = [], []
		for right in rights:
			items.append(f"CONCAT('%', {right.sql}, '%')" if comp in {'~', '!~'} else right.sql)
			params.extend(right.param)

		if len(items) == 1: beg, end = '', ''
		elif comp in {'=', '~'}: beg, end = 'ANY(ARRAY[', '])'
		elif comp in {'!=', '!~'}: beg, end = 'ALL(ARRAY[', '])'
		else: raise Err('E_COMP_OR2')

		return ('having' if self.agg else 'where'), SQL(f"{left.sql}{sqlcomp}{beg}{','.join(items)}{end}", left.param + params)


class Grid(Axis2):

	def select(self) -> List[SQL]:
		self.rect()
		out = []
		env = {'mode':'qry', 'sim':0.5,'tab':'','taba':'','cola':''}

		for axis1 in self:
			env['lim'], env['beg'] = 0, 0
			bind = {k: SQL(PH, [v]) for k, v in env.items()}
			tab_cnt = 0
			qry = {'select':[], 'from':[], 'fromall':[], 'groupby':[], 'where':[], 'having':[], 'orderby':[]}
			grouped = False
			allselected = False

			for axis0 in axis1:

				if env['mode']!='qry': continue

				if axis0.src == '_':
					allselected = True
					continue
	
				for idx0, cell in enumerate(axis0):
					#print(repr(cell))
					single = cell.single.dat
					if cell.padded or cell.single.kind=='SLOT': continue

					# EVAR for TAB/COL
					evarval = cell.find('EVAR').canon
					if evarval=='%val': pass
					elif evarval:
						env[evarval[1:]] = cell.single.dat
						bind[evarval[1:]]=SQL(PH, [cell.single.dat])

						if evarval=='%tab':
							if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_$]{0,62}', single): raise Err('E_TAB_NAME')
							tab_cnt += 1
							env['tab']=single
							env['taba']=f"t{tab_cnt}"
							qry['from'].append(SQL(f"{env['tab']} AS {env['taba']}"))
							qry['fromall'].append(env['taba'])

						elif evarval=='%col':
							if single == '_': allselected = True
							elif not re.fullmatch(r'[A-Za-z_]+[A-Za-z0-9_$]{0,62}', single): raise Err('E_COL_NAME')
							env['cola'] = single

						continue

					# SLOT for COL
					assnval = cell.find('ASSN').canon
					if assnval: env['cola'] = assnval[2:]

					if not env['taba']: raise Err('E_TAB_REQ')
					
					valcell = CellSQL(repr(cell))
					valcell.base = f"{env['taba']}.{env['cola']}"

					qry['select'].append(valcell)

					if valcell.grouped:
						grouped = True
						qry['groupby'].append(valcell)

					if valcell.sort: qry['orderby'].append(valcell)

					clause = valcell.sql_clause(bind)
					if clause:
						key, term = clause
						qry[key].append(term)

					for flag in valcell.flag:
						if flag.kind != 'BIND': continue
						if flag.canon[2:] in env: raise Err('E_ENV_BIND')
						bind[flag.canon[2:]] = valcell

			if not qry['from']:
				out.append(SQL())
				continue

			parts = (
				('SELECT', ', ', [SQL(f"{a}.*") for a in qry['fromall']] if allselected else SQL.uniq(t.sql_value(grouped, True) for t in qry['select'])),
				('FROM', ', ', qry['from']),
				('WHERE', ' AND ', qry['where']),
				('GROUP BY', ', ', SQL.uniq(t.sql_groupby for t in qry['groupby'])),
				('HAVING', ' AND ', qry['having']),
				('ORDER BY', ', ', SQL.uniq(t.sql_value(grouped, False, True) for t in qry['orderby'])),
			)

			sql, param = [], []
			for keyword, sep, terms in parts:
				if not terms: continue
				sql.append(f"{keyword} " + sep.join(t.sql for t in terms))
				for t in terms: param.extend(t.param)

			if env['lim']: sql.append(f"LIMIT {int(env['lim'])}")
			if env['beg']: sql.append(f"OFFSET {int(env['beg'])}")

			out.append(SQL(' '.join(sql), param))

		return out


### CLI ###

if __name__ == "__main__":
	if len(sys.argv)>1: lines=[' '.join(sys.argv[1:])]
	else: lines = examples.splitlines()
	if not lines: exit()
	for i in range(len(lines)):
		line=lines[i].strip()
		if not line: continue
		if line.startswith('"""'): print(f'{line}')
		else:
			grid=Grid(line)
			print(str(grid))
			sel = grid.select()
			if sel: print(str(sel[0]))
			print()