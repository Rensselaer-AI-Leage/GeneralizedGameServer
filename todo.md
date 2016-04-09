~/* threading for multiple connections
bracket / round robin support
elo system
meta elo system (over many competitions)
~/* "destructor" to close connections and terminate threads
make server handle poll_input (for token support) [message does this now]
unique names? (yes)

~/* replace all sending and things with message.py's funcitons
replace all tuples with structs (dictionaries) [note: ethan likes tuples better even though indexing is awful]

~/* write exception logging function to call whenever an exception is caught

redo poll() and poll_all() so they aren't spaghetti

create program for easily traversing logs

playerlist class

system independence
