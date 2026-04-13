
SFT = 'ft:gpt-4.1-mini-2025-04-14:holtwork:memelang-09-43:CYK3dI7P'

examples={
	'movies':{
		'active': True,
		"schema": open('../train/movies/_schema.meme',encoding="utf-8").read(),
		"examples": [
			{"input":"Actors named Anna in films from 2012 to 2014","output":"movies year >=2012;<=2014;title _;roles movie @;actor ~\"Anna\";;"},
			{"input":"Comedies in 1995 ranked by highest average role rating (top 3)","output":"movies genre comedy;year 1995;title :grp;roles movie @;rating :avg:des;% lim 3;;"},
			{"input":"Actors with 4 to 9 roles inclusive, alphabetical","output":"roles actor :grp:asc;id :cnt>=4;:cnt<=9;;"},
			{"input":"Movies released after 2000 whose title equals an actor name","output":"movies year >2000;title _;actors name @;;"},
			{"input":"Actors aged 25 to 35 with average role rating at least 4.1","output":"actors age >=25;<=35;name :grp;roles actor @;rating :avg>=4.1;;"},
			{"input":"Films from 2012 with \"ocean\" in description, titles Z-A","output":"movies year 2012;description ~\"ocean\";title :des;_;;"},
			{"input":"Top 5 actors by minimum rating in robot-themed films","output":"movies description <=>\"robot\">=$sim;title _;roles movie @;actor :grp;rating :min:des;% lim 5;;"},
			{"input":"Roles in Alien or Aliens where actor name equals the movie title","output":"roles movie \"Alien\",\"Aliens\";actor @;;"},
			{"input":"Role counts per actor for documentaries in 2010, high to low","output":"movies genre documentary;year 2010;title _;roles movie @;id :cnt:des;actor :grp;;"},
			{"input":"Space exploration movies from 2000 and later: largest casts first, top 10","output":"movies year >=2000;description <=>\"space exploration\">=$sim;title :grp;roles movie @;id :cnt:des;% lim 10;;"},
			{"input":"Dramas from 1980 to 1989 ordered by title A-Z","output":"movies year >=1980;<=1989;genre drama;title :asc;_;;"},
			{"input":"Actors with most roles in 1999, top 7","output":"movies year 1999;title _;roles movie @;actor :grp;id :cnt:des;% lim 7;;"},
			{"input":"Average role rating per movie in 2001, high to low","output":"movies year 2001;title :grp;roles movie @;rating :avg:des;;"},
			{"input":"Actors with \"Lee\" in name sorted by youngest first","output":"actors name ~\"Lee\";age :asc;_;;"},
			{"input":"Movie titles equal to an actor name in 1985","output":"movies year 1985;title _;actors name @;_;;"},
			{"input":"Space-themed films in 2016 ranked by max role rating, top 5","output":"movies year 2016;description <=>\"space\">=$sim;title :grp;roles movie @;rating :max:des;% lim 5;;"},
			{"input":"Actors aged 30 to 50 with average role rating at least 4.5","output":"roles actor :grp;actors name @;age >=30;<=50;rating :avg>=4.5;;"},
			{"input":"1977 releases most similar to \"rebellion\", similarity high to low","output":"movies year 1977;description <=>\"rebellion\":des;_;;"},
			{"input":"Roles where actor includes \"Smith\" in 2003 movies","output":"movies year 2003;title _;roles movie @;actor ~\"Smith\";_;;"},
			{"input":"Role counts per movie in 1994, lowest to highest","output":"movies year 1994;title :grp;roles movie @;id :cnt:asc;;"},
			{"input":"Sci-fi releases from 1980 through 1999 mentioning robot or android; list co-stars of people named like Mark with strictly higher role ratings (A-Z), cap 12","output":"movies genre scifi;year >=1980;<=1999;description ~\"robot\",\"android\";title _;roles movie @;actor :$a~\"Mark\";rating :$r=_;movie _;@ @ @;actor :asc=!$a;rating >$r;% lim 12;;"},
			{"input":"Films from 2000 and later with the strongest average role ratings and largest casts, show by movie (both metrics descending, top 10)","output":"movies year >=2000;title :grp;roles movie @;rating :avg:des;id :cnt:des;% lim 10;;"},
			{"input":"Actors whose name includes Ann and age between 25 and 60 appearing in politically intriguing films, most relevant first","output":"actors name ~\"Ann\";age >=25;<=60;roles actor @;movie _;movies title @;description <=>\"political intrigue\":des;_;;"},
			{"input":"Movies after 1995 where casts are mid-sized (5–12) and average role rating is at least 3.5; break ties by max rating desc then title asc","output":"movies year >1995;title :grp;roles movie @;id :cnt>=5;:cnt<=12;rating :avg>=3.5;:max:des;movie :asc;;"},
			{"input":"Drama titles since 2000 about artificial intelligence, newest releases first, page 3 with 30 per page","output":"movies genre drama;year :des>=2000;description <=>\"artificial intelligence\">=$sim;_;% lim 30;% beg 60;;"},
			{"input":"Youngest five co-stars who appeared with Harrison Ford in films released before 1990","output":"roles actor :$a~\"Harrison Ford\";movie _;movies title @;year <1990;title _;roles movie @;actor !$a;actors name @;age :asc;% lim 5;;"},
			{"input":"People whose name exactly matches a movie title and whose roles from 2010 to 2015 average at least 3, ordered by that average descending","output":"actors name :$x:grp;movies title $x;roles actor $x;rating :avg:des>=3;movie _;movies title @;year >=2010;<=2015;;"},
			{"input":"Space exploration films from 1960–1975 ranked by cast size, tie-break by highest role rating then title A-Z (top 10)","output":"movies description <=>\"space exploration\">=$sim;year >=1960;<=1975;title :grp;roles movie @;id :cnt:des;rating :max:des;movie :asc;% lim 10;;"},
			{"input":"Comedies after 2000 where a role rating is at least 3.5 performed by actors under 18; list movie titles with actor names","output":"movies genre comedy;year >2000;title _;roles movie @;rating >=3.5;actor _;actors name @;age <18;_;;"},
			{"input":"Year buckets after 1977 for space opera movies, ascending by year with film counts","output":"movies description <=>\"space opera\">=$sim;year :grp:asc>1977;id :cnt;;"},
		]
	},
	'employees':{
		'active': True,
		"schema": open('../train/employees/_schema.meme',encoding="utf-8").read(),
		"examples": [
			{"input":"Active full-time hires in 2024 with department name and country","output":"employees status active;full_time 1;hire_date >=2024-01-01;<=2024-12-31;department_id _;departments id @;name _;location_id _;locations id @;country _;;"},
			{"input":"Managers with at least 5 direct reports, names included, sorted by headcount","output":"employees manager_id :grp;id :cnt:des>=5;employees id @;first_name _;last_name _;;"},
			{"input":"Top 12 net pay results in payroll run 2002 with employee names","output":"payroll_runs id 2002;id _;payroll_entries payroll_run_id @;net_pay :des;employee_id _;employees id @;_;% lim 12;;"},
			{"input":"Reviews since 2024-01-01 most similar to mentorship with rating 4 or higher","output":"performance_reviews review_date >=2024-01-01;rating >=4;comments <=>\"mentorship\":des;_;;"},
			{"input":"Comments close to collaboration with similarity >= 0.6 between 2023-01-01 and 2025-12-31","output":"performance_reviews comments <=>\"collaboration\">=0.6;review_date >=2023-01-01;<=2025-12-31;_;;"},
			{"input":"Employees under manager 5 with first and last names","output":"employees manager_id 5;first_name _;last_name _;;"},
			{"input":"USD payroll entries in June 2025 with department name for employees paid at least 2500","output":"payroll_entries currency \"USD\";created >=2025-06-01;<=2025-06-30;net_pay >=2500;employee_id _;employees id @;department_id _;departments id @;name _;;"},
			{"input":"Job grades where avg min_salary >= 70000 ordered by average descending","output":"jobs grade :grp;min_salary :avg:des>=70000;;"},
			{"input":"Employees in departments located in US-NY ordered by hire_date desc, page 2 of 20","output":"locations country \"US\";region \"NY\";id _;departments location_id @;id _;employees department_id @;hire_date :des;_;% lim 20;% beg 20;;"},
			{"input":"Employees with expert Data skills last used in 2024, sort last name A-Z","output":"skills category \"Data\";id _;employee_skills skill_id @;level expert;last_used >=2024-01-01;<=2024-12-31;employee_id _;employees id @;last_name :asc;;"},
			{"input":"Average hours worked per employee for submitted timesheets in February 2025 with last names","output":"timesheets submitted 1;week_start >=2025-02-01;<=2025-02-28;employee_id :grp;hours_worked :avg;employees id @;last_name _;;"},
			{"input":"USD payroll net pay totals per employee in July 2025 with last name A-Z where sum >= 3000","output":"payroll_entries currency \"USD\";employee_id :grp;net_pay :sum>=3000;payroll_run_id _;payroll_runs id @;pay_date >=2025-07-01;<=2025-07-31;employees id @;last_name :asc;;"},
			{"input":"Department headcount for locations in US-CA with department name, count desc","output":"employees id :cnt:des;department_id :grp;departments id @;name _;location_id _;locations id @;country \"US\";region \"CA\";;"},
			{"input":"Denied or canceled time off in 2025-09 with employee names, sorted by start date","output":"time_off_requests status denied,canceled;start_date :asc>=2025-09-01;<=2025-09-30;employee_id _;employees id @;first_name _;last_name _;_;;"},
			{"input":"Approver names for timesheets with overtime > 5 during 2025-06, week_start desc","output":"timesheets overtime_hours >5;week_start :des>=2025-06-01;<=2025-06-30;approver_id _;employees id @;last_name _;first_name _;;"},
			{"input":"Latest week_start per employee for submitted timesheets with employee last name","output":"timesheets submitted 1;employee_id :grp;week_start :last;employees id @;last_name _;;"},
			{"input":"Non-terminated employees with salary 60000..150000, order by salary desc then hire_date asc, limit 50 offset 50","output":"employees status !=terminated;salary :des>=60000;<=150000;hire_date :asc;_;% lim 50;% beg 50;;"},
			{"input":"Approved parental leave in Q1 2025 with hours >= 40 and employee names, hours desc","output":"time_off_requests type parental;status approved;start_date >=2025-01-01;<=2025-03-31;hours :des>=40;employee_id _;employees id @;first_name _;last_name _;;"},
			{"input":"Medical benefit plans with enrollment counts sorted high to low, show plan name","output":"employee_benefits id :cnt:des;benefit_plan_id :grp;benefit_plans id @;type medical;name _;;"},
			{"input":"Gross pay totals per payroll run during 2025-06, sort by total desc with pay_date","output":"payroll_entries gross_pay :sum:des;payroll_run_id :grp;payroll_runs id @;pay_date >=2025-06-01;<=2025-06-30;;"}
		]
	}
}
