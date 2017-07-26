/***************************
Basic idea behind the schema below
Every time someone votes yes or no on a pair of images, we record
their feedback in this table. This will keep track of

	- What browser session someone is voting in
	- The file path to the first image being shown
	- The file path to the second image being shown
	- Which CNN model judged these as similar
	- How the human voted (perhaps 'yes' they match, 
		'no' they dont, and an 'idk' option)?

Any of this is subject to clarification/refinement as 
we get a clearer idea of structure.

Figure out if and how to log sessions later
***************************/


drop table if exists user_feedback;
create table user_feedback(
	id integer primary key autoincrement,
	-- session text not null,
	pair_file_1 text not null,
	pair_file_2 text not null,
	model text not null,
	user_vote integer not null,
	comment text not null
	);