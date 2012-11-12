-module('unin').
-export([out/1]).

out(_Arg) ->
	io:format("Hello from Unin~n"),
	{html, "<p>Hello from Unin<p>"}.
