Check for errors:
* Syntax errors
	* Example not ending in `;;`
* Logical misalignment of natural language and MEMELANG
* Columns
	* Spurious columns
	* Redundant use of table.column name such as `col :x;col >y;col <z`
		* Same column name on *different* tables is allowed
* Joins
	* Failure to join when needed
	* Errant joins
		* `@` not referencing immediate prior value, check for errant clauses in between
		* Joining on two columns of different domains
	* Needless joins
		* Getting coloumn whose value is known
		* Hopping back-and-forth from a table
* Variables
	* Use of `$var` when `@` would work
* Aggregation
	* `:min|:max|:cnt|:sum|:avg|:last` is not eventually followed by `:grp`
	* Using `:sum` or `:avg` illogically on a column (i.e. ID or date)
	* Applying `:grp` to a unique column
	* Invalid `:functions`
