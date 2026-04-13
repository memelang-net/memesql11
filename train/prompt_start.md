These files are LLM training data for a DSL query language. Create new training data for a new schema.
* Output in markdown box as `""" user natural language query """\nMEMELANG\n\n`
* Each comment is a user's natural language search query. 
	* Phrase each distinctly - do not repeat a pattern
	* Phrase concisely - never use superfluous phrases like "Give," "Return," or "List."
	* Phrase humanly - never use program instructions, never use phrases like "capture," "remember," or "bind"
	* Never use "table.column"
	* Use only ASCII characters
	* Use only exampled rules - never invent new rules
	* Use only exampled syntax - never invent new syntax
	* Use only absolute dates - never use relative dates
	* Avoid terms that could trigger a warning like "die" or "dead"

SCHEMA:
```
% mode tab;users id :TYP=INT;>0;username :DESC="Unique handle";:TYP=STR;email :DESC="User email";:TYP=STR;password_hash :DESC="Hashed password";:TYP=STR;created_at :DESC="Signup timestamp";:TYP=TS;updated_at :DESC="Last profile change";:TYP=TS;;profiles id :TYP=INT;>0;user_id :DESC="Owner user id";:TYP=INT;>0;full_name :TYP=STR;bio :TYP=STR;location :TYP=STR;website :TYP=STR;avatar_url :TYP=STR;birthday :TYP=DATE;created_at :TYP=TS;updated_at :TYP=TS;;follows id :TYP=INT;>0;follower_id :DESC="User who follows";:TYP=INT;>0;followee_id :DESC="User being followed";:TYP=INT;>0;created_at :TYP=TS;;posts id :TYP=INT;>0;user_id :DESC="Author";:TYP=INT;>0;body :DESC="Post content";:TYP=STR;image_url :TYP=STR;visibility =public,friends,private;:TYP=STR;created_at :TYP=TS;updated_at :TYP=TS;;comments id :TYP=INT;>0;post_id :DESC="Parent post";:TYP=INT;>0;user_id :DESC="Author";:TYP=INT;>0;parent_comment_id :DESC="Threaded parent";:TYP=INT;body :DESC="Comment text";:TYP=STR;created_at :TYP=TS;updated_at :TYP=TS;;likes id :TYP=INT;>0;user_id :DESC="Who liked";:TYP=INT;>0;post_id :DESC="Liked post";:TYP=INT;>0;created_at :TYP=TS;;messages id :TYP=INT;>0;sender_id :DESC="From user";:TYP=INT;>0;recipient_id :DESC="To user";:TYP=INT;>0;body :DESC="Message text";:TYP=STR;created_at :TYP=TS;read_flag :DESC="Read state";:TYP=BOOL;; users id _;profiles user_id @;follows follower_id @;follows followee_id @;posts user_id @;comments user_id @;messages sender_id @;messages recipient_id @;likes user_id @;;posts id _;comments post_id @;likes post_id @;;comments id _;comments parent_comment_id @;;users id :pri;;users username :grp:cnt=1;;users email :grp:cnt=1;;profiles id :pri;;profiles user_id :grp:cnt=1;;follows id :pri;;posts id :pri;;comments id :pri;;likes id :pri;;messages id :pri;;follows follower_id :grp;followee_id :grp:cnt=1;;likes user_id :grp;post_id :grp:cnt=1;;
```

Create the following examples for the schema. Output in markdown box as `""" user natural language query """\nMEMELANG\n\n`.
* for each table, 3 examples that each select all columns
* for each table, for each column, 3 examples that each filter on just that column
	* use < > >= <= ~ <=> !~ != = where applicable
* for each table, for each column, 3 examples that each filter on just that column using TWO values such as =X,Y or !=X,Y or ~X,Y or !=X,Y


Now create the following examples for the schema. Output in markdown box as `""" user natural language query """\nMEMELANG\n\n`.
* for each table, for each column, 3 examples that sort asc on just that column
* for each table, for each column, 3 examples that sort asc on just that column
* for each table, 6 examples that sort on 2-3 columns, mixing :asc and :des
* for each table, for each int/date/dec column, 2 examples filter that column twice as col >=X;<=Y
* for each table, 4 examples that filter on 2-4 columns
* for each table, 2 examples that filter on 2-4 columns and sort on one column
* for each table, 4 examples that filter on 2-4 columns and sort on one column with a `;% lim X`
* for each table, 4 examples that filter on 2-4 columns and sort on one column with a` ;% lim X;% beg Y`


Now create the following examples for the schema. Output in markdown box as `""" user natural language query """\nMEMELANG\n\n`.
* 10 examples using :grp for distinct
	* use non-unique columns
* 10 examples using :sum and :grp
* 10 examples using :min and :grp
* 10 examples using :max and :grp
* 10 examples using :avg and :grp
* 10 examples using :cnt and :grp


Now create the following examples for the schema. Output in markdown box as `""" user natural language query """\nMEMELANG\n\n`.
* 10 examples using :cnt|sum|min|max|avg and :grp and a filter column
* 10 examples using group-filter :grp[<|>|=|!=|~|!~|<=>]X with a :cnt|sum|min|max|avg
* 10 examples using group :grp and a filter on :cnt|sum|min|max|avg<>=X
* 10 examples using group-filter-sort :grp:asc|des[<|>|=|!=|~|!~|<=>]X with a :cnt|sum|min|max|avg
* 10 examples using group :grp and a filter-sort on :cnt|sum|min|max|avg:asc|des<>=X
* 10 join examples using @, projecting two column value not available in one table


Now create the following examples for the schema. Output in markdown box as `""" user natural language query """\nMEMELANG\n\n`.
* 20 multi-hop join examples
* 20 examples that include :cnt|sum|min|max|avg and :grp and :asc|des and a filter and an @ join
* 20 examples that assign a variable :$x[!=|~|!~|>|<|>=|<=] to an unknown value, then join _ to @, then reference the variable as col $x or col !$x.