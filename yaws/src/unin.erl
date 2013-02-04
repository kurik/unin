-module('unin').
-export([out/1]).

%%% -include("/usr/lib/yaws/include/yaws_api.hrl").
-include("/home/kurik/opt/yaws/lib/yaws/include/yaws_api.hrl").

out(Arg) ->
	Method = method(Arg),
	Resource = resource(Arg),
	% io:format("Resource: ~p~n", [Resource]),
	handle(Method, Resource, Arg).

method(Arg) ->
	Rec = Arg#arg.req,
	Rec#http_request.method.

resource(Arg) ->
	Resource = string:sub_word(Arg#arg.pathinfo, 1, $/),
	Resource.

handle(Method, Resource, Arg) ->
	case Resource of
		"temp" ->
			temp:handle(Method, Arg);
		_ ->
			{status, 404}
	end.

