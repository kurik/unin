-module('temp').
-export([out/1]).

out(Arg) ->
	io:format("Hello from Unin/Temp~p").
