-module('temp').
-export([handle/2]).

% -define(SENSORS, "/sys/bus/w1/devices").
-define(SENSORS, "/home/kurik/tmp").
-define(SENSOR_DATA, "/w1_slave").

handle('GET', Arg) ->
	io:format("Temp -> Arg: ~p~n", [Arg]),
	{html, "<p>Hello from temp<p>"};

handle(Method, _Arg) ->
	io:format("Temp -> Unsupported method: ~p~n", [Method]),
	{html, "<p>Unsupported method in temp module<p>"}.

temp_list() ->
	case file:list_dir(?SENSORS) of
		{ok, Filenames} ->
			walk_through(Filenames);
		Err ->
			Err
	end.

is_sensor(File) ->
	case file:read_file_info(string:concat(File, ?SENSOR_DATA) of
		{ok, _} ->
			File;
		_ ->
			[];
	end.

walk_through([]) ->
	[];

walk_through([File | []]) ->
	is_sensor(File);

walk_through([File | Tail]) ->
	[is_sensor(File) | walk_through(Tail)].

