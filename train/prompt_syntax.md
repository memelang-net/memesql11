MEMELANG:
* Syntax
	* [table WS] [column WS] ["<=>" "\"" string "\""] [":" "$" var] [":" ("min"|"max"|"cnt"|"sum"|"avg"|"last"|"grp")][":" ("asc"|"des")] [("="|"!="|">"|"<"|">="|"<="|"~"|"!~") (string|int|float|("$" var)|"@"|"_")] ";"
	* WS (whitespace) ONLY after table or column
	* Final should end in `;;`
* Columns
	* Leftward table/columns are curried forward so `table col val1;val2` means `table col val1;table col val2`
	* Each table.column should only appear once, `tab col :x;col >y;col <z` should be consolidated into `tab col :x>y;<z`; same column name for distinct tables such as `tab1 col;tab2 col` is allowed
* Wildcard
	* `_` is wild card 
	* `col _` filters/projects any value for col
	* `;_` and `table _ _` project all columns for prior table
	* `;_` should NOT appear in `:grp` queries
* Aggregation
	* `:sum|min|max|cnt|avg|last` may appear before `:grp`
	* Do not `:sum` ID or date columns
* Projection
	* ***Every*** clause's column value is automatically projected, including `col :grp` and `col ~"x"`
	* If not already in the query, project the target row name column:
		* In non `:grp` queries, `;_` or `;_;` or `name _` should appear in the desired table, before any following tables
		* In `:grp` the name column should be projected as `name _` such as `name _;x_id :grp`
* Same
	* `@` references the to-be-retrieved value in that position in prior clause such as `x _;y @` or `x :grp;y @`
	* `"@"` is literal when inside quotes, ignore
	* `@ @ @` is a self-join, referencing prior/carried table, prior/carried column, and to-be-retrieved prior value
* Variables 
	* Assign as `:$x>1`, reference as `>$x`
	* Avoid assigning variable a known value like `:$x=1`, `:$x=_` is NOT known
	* Only use var when `@` will not work
* Joins
	* Avoid needless joining
	* Do all filtering and sorting for a table continuously before joining to another table
	* Incorrect `tab1 col1 val1;...;tab2 col2 @;...;tab1 col3 val3` should be `tab1 col1 val1;col3 val3;...;tab2 col2 @;...`
* Embedding operator `<=>"xyz"` 
	* Only followed by `:des` when ordering by similarity
	* Only followed by `>=MIN` when NOT ordering by similarity, default `>=$sim` is populated by compiler
	* Query may explicitly specify a numeric `>[=]MIN`
	* Query may specify both `:des` and `>=MIN`
* `% lim X;% beg Y` triggers pagination