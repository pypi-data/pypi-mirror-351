use strict;
# use warnings;
use Globals;

my %PRESCAN = ();
my %PRESCAN_INFO = ();

delete $Globals::ENV{PRESCAN};
delete $Globals::ENV{CONFIG};

my $MR = new Common::MiscRoutines(MESSAGE_PREFIX => 'GREEN_SRC_HOOKS', DEBUG_FLAG => 1);
my $CFG_POINTER = undef;
my $sql_parser = '';
my @conversion_catalog_add = ();   # Things that we will add to the conversion catalog

sub greenplum_prescan
{
	my $td_source_ref = shift;
	$MR->log_msg("Begin greemplum_prescan");

	$Globals::ENV{PRESCAN}->{PROC_NAME} = '';

	my $td_source_lines = join("\n", @$td_source_ref);
	
    $Globals::ENV{CONFIG} = $CFG_POINTER;

	if ($Globals::ENV{CONFIG}->{add_create_for_not_precedure_scripts})
	{
        $td_source_lines =~ s/(\bfunction\b|\bprocedure\b)/ $1/gis;
		$td_source_lines =~ s/(?<![CREATE|REPLACE])\s+(\bFUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\))/\bRETURNS\b $1/gis;
		$td_source_lines =~ s/CREATE\s+CREATE/CREATE $1/gis;
		$td_source_lines =~ s/REPLACE\s+CREATE/REPLACE /gis;
	}
	
	#	remove all comments
	$td_source_lines =~ s/\-\-.*$//gim;
	$sql_parser = $Globals::ENV{SQL_PARSER};
	$td_source_lines = $sql_parser->remove_c_style_comments($td_source_lines);


	if($td_source_lines =~ /\bCREATE\s+FUNCTION\s+/is ||
		$td_source_lines =~ /\bCREATE\s+OR\b\s+REPLACE\s+FUNCTION\s+/is)
	{
		prescan_function_stmt($td_source_lines);
	}
}

sub prescan_function_stmt 
{
	my $function_stmt = shift;
	$MR->log_msg("Begin prescan_function_stmt: $function_stmt");

	my $function_name = '';
	my $function_args = '';
	
	if ($function_stmt =~ /\bCREATE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURNS\b/is)
	{
		$function_name = $1;
		$function_args = $2;
	}
	elsif($function_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURNS\b/gis)
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
		
	}
	elsif($function_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURNS\b/gis)
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
		
	}
	elsif($function_stmt =~ /FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURNS\b/gis)
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
	}
	
	$Globals::ENV{PRESCAN}->{FUNCTION_NAME} = $function_name;

	my $prescan_function_args = ();

	# Save the "before" in case we need to search through it or report it
	$prescan_function_args->{ORIGINAL_SOURCE} = $function_args;

	$MR->log_msg("greenplum function params: $function_args");
	
	my @arg_defs = split(',', $function_args);
	my $arg_num = 0;
	foreach my $arg (@arg_defs)
	{
		$arg = $MR->trim($arg);
		if($arg =~ /(\w+)\s+(.*)/is)
		{
			my $args->{NAME}   = $MR->trim($1);     # No longer converting to upper case
			#$args->{ARG_TYPE}  = uc($MR->trim($2));
			my $last_part = $MR->trim($2);
			
			if ($last_part =~ /(\w+)\s+DEFAULT\s+(.*)/gis)
			{
                $args->{DATA_TYPE} = $1;
				$args->{VALUE} = $2;
            }
            else
			{
				$args->{DATA_TYPE} = $last_part;
			}
			
			push (@{$Globals::ENV{PRESCAN}->{FUNCTION_ARGS}}, $args);
			push (@conversion_catalog_add, "function_args,$function_name,$arg_num" . ':::' . "$1,$2,$3");
			$arg_num++;
		}
	}

	if ($arg_num == 0)
	{
		push (@conversion_catalog_add, "functions_args,$function_name,x" . ':::');
	}
}