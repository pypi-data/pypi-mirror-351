use strict;
# use warnings;
use Globals;

my %PRESCAN = ();
my %PRESCAN_INFO = ();

delete $Globals::ENV{PRESCAN};
delete $Globals::ENV{CONFIG};



my @conversion_catalog_add = ();   # Things that we will add to the conversion catalog

sub snowflake_prescan
{
	my $td_source_ref = shift;
	$MR->log_msg("Begin snowflake_prescan");

	$Globals::ENV{PRESCAN}->{PROC_NAME} = '';

	my $td_source_lines = join("\n", @$td_source_ref);


    $Globals::ENV{CONFIG} = $CFG_POINTER;

	if ($td_source_lines =~ /\bCREATE\s+PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*\(/is or
		$td_source_lines =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*\(/is
		or	$td_source_lines =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*\.*?\bRETURNS\b/is)
	{
		prescan_procedure_stmt($td_source_lines);
	}
	elsif($td_source_lines =~ /\bCREATE\s+FUNCTION\s+/is or
		$td_source_lines =~ /\bCREATE\s+OR\b\s+REPLACE\s+FUNCTION\s+/is)
	{
		prescan_function_stmt($td_source_lines);
	}
}

sub prescan_procedure_stmt 
{
	my $procedure_stmt = shift;
	$MR->log_msg("Begin prescan_procedure_stmt");

	my $procedure_name = '';
	my $procedure_args = '';
	my $procedure_vars = '';
	if ($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*IS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\(?(.*?)\)?\s*RETURNS\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		#$procedure_vars = $3;
	}
    $procedure_name =~s/\"//gis;
	
	if ($Globals::ENV{CONFIG}->{change_procedure_to_function})
	{
		$Globals::ENV{PRESCAN}->{FUNCTION_NAME} = $procedure_name;
	}
	else
	{
		$Globals::ENV{PRESCAN}->{PROC_NAME} = $procedure_name;
	}

	my $prescan_proc_args = ();

	# Save the "before" in case we need to search through it or report it
	$prescan_proc_args->{ORIGINAL_SOURCE} = $procedure_args;

	$MR->log_msg("snowflake proc params: $procedure_name");
	
	my @arg_defs = split(',', $procedure_args);
	my @var_defs = split(';', $procedure_vars);
	my $arg_num = 0;
	foreach my $arg (@arg_defs)
	{

		$arg = $MR->trim($arg);
		if($arg =~ /\"?(\w+)\"?\s+(\w+)\s*(.*)/is)
		{
			my $args->{NAME}   = $MR->trim($1);     # No longer converting to upper case
			$args->{ARG_TYPE} = 'IN';
			$args->{DATA_TYPE}  = uc($MR->trim($2));
			my $last_part = $MR->trim($3);
			
			if ($Globals::ENV{CONFIG}->{change_procedure_to_function})
			{
				push (@{$Globals::ENV{PRESCAN}->{FUNCTION_ARGS}}, $args);
			}
			else
			{
				push (@{$Globals::ENV{PRESCAN}->{PROC_ARGS}}, $args);
			}

			push (@conversion_catalog_add, "stored_procedure_args,$procedure_name,$arg_num" . ':::' . "$1,$2,$3");
			$arg_num++;
		}
	}
	
	foreach my $var (@var_defs)
	{
		$MR->log_msg("snowflake proc vars: $var");
		$var = $MR->trim($var);
		if($var =~ /(\w+)\s+(.*)/is)
		{
			my $vars->{NAME} = $MR->trim($1);
			my $data_type = $MR->trim($2);
			if($data_type =~ /\s*(.*?)\s*\:\=\s*(.*)/is)
			{
				$vars->{DATA_TYPE} = $1;
				my $val = $2;
				$vars->{VALUE} = $val;
				$vars->{DEFAULT_VALUE} = $val;
			}
			else
			{
				$vars->{DATA_TYPE} = $data_type;
			}
			if ($Globals::ENV{CONFIG}->{change_procedure_to_function})
			{
				push (@{$Globals::ENV{PRESCAN}->{FUNCTION_VARS}}, $vars);
			}
			else
			{
				push (@{$Globals::ENV{PRESCAN}->{PROC_VARS}}, $vars);
			}			
			
			push (@{$Globals::ENV{PRESCAN}->{VARIABLES}}, $vars);
		}
	}
	
	if ($arg_num == 0)
	{
		push (@conversion_catalog_add, "stored_procedure_args,$procedure_name,x" . ':::');
	}
}

sub prescan_function_stmt 
{
	my $function_stmt = shift;
	$MR->log_msg("Begin prescan_function_stmt");

	my $function_name = '';
	my $function_args = '';

	if ($function_stmt =~ /\bCREATE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\(?(.*?)\)?\s*RETURNS\b/is)
	{
		$function_name = $1;
		$function_args = $2;
	}
	elsif($function_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\(?(.*?)\)?\s*RETURNS\b/is)
	{
		$function_name = $1;
		$function_args = $2;
	}
    $function_name =~s/\"//gis;
	
	$Globals::ENV{PRESCAN}->{FUNCTION_NAME} = $function_name;

	my $prescan_function_args = ();

	# Save the "before" in case we need to search through it or report it
	$prescan_function_args->{ORIGINAL_SOURCE} = $function_args;

	$MR->log_msg("snowflake function params: $function_name");
	
	my @arg_defs = split(',', $function_args);
	my $arg_num = 0;
	foreach my $arg (@arg_defs)
	{
		$arg = $MR->trim($arg);
		if($arg =~ /\"?(\w+)\"?\s+(\w+)\s*(.*)/is)
		{
			my $args->{NAME}   = $MR->trim($1);
			$args->{ARG_TYPE} = 'IN';
			$args->{DATA_TYPE}  = uc($MR->trim($2));
			my $last_part = $MR->trim($3);
			
			push (@{$Globals::ENV{PRESCAN}->{FUNCTION_ARGS}}, $args);

			push (@conversion_catalog_add, "stored_procedure_args,$function_name,$arg_num" . ':::' . "$1,$2,$3");
			$arg_num++;
		}
	}
	
	if ($arg_num == 0)
	{
		push (@conversion_catalog_add, "stored_procedure_args,$function_name,x" . ':::');
	}
}