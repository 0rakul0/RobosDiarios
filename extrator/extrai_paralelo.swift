import files;
import string;
import unix;
import io;
import sys;

app (file o) f(string commandline)
{
  "sh" "-c" commandline @stdout=o;
}

/*
app (file o) get_files(string diario)
{
  "./extrator/list_not_processed_files.sh diario" @stdout=o;
}*/


app call_extrator(string commandline)
{
  "sh" "-c" commandline;
}

string diario = argp(1);

get_files = ["extrator/list_not_processed_files.sh", diario];

file files <"files.txt"> = f(string_join(get_files, " "));

string lines[] = file_lines(files);

foreach line in lines
{
    //printf(line);
    commandline = ["extrator/call_extrator.sh", line];
    call_extrator(string_join(commandline, " "));
}
