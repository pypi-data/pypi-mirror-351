use strict;
# use warnings;
use Globals;

my %PRESCAN = ();
my %PRESCAN_INFO = ();

delete $Globals::ENV{PRESCAN};
delete $Globals::ENV{CONFIG};



my @conversion_catalog_add = ();   # Things that we will add to the conversion catalog

sub redshift_prescan
{
	my $td_source_ref = shift;
	$MR->log_msg("Begin redshift_prescan");

	$Globals::ENV{PRESCAN}->{PROC_NAME} = '';

	my $td_source_lines = join("\n", @$td_source_ref);
	
    $Globals::ENV{CONFIG} = $CFG_POINTER;
    $MR->log_msg("Begin oracle_prescan1 $td_source_lines"); 
	if ($Globals::ENV{CONFIG}->{add_create_for_not_precedure_scripts})
	{
        $td_source_lines =~ s/(function|procedure)/ $1/gis;
		$td_source_lines =~ s/(?<![CREATE|REPLACE])\s+(FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\))/\nCREATE $1/gis;
		$td_source_lines =~ s/(?<![CREATE|REPLACE])\s+(PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\))/\nCREATE $1/gis;
		$td_source_lines =~ s/(?<![CREATE|REPLACE])\s+(PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?))/\nCREATE $1/gis;
		$td_source_lines =~ s/CREATE\s+CREATE/CREATE $1/gis;
	}
	$MR->log_msg("Begin oracle_prescan2 $td_source_lines"); 
	#	remove all comments
	$td_source_lines =~ s/\-\-.*$//gim;
	$td_source_lines = $sql_parser->remove_c_style_comments($td_source_lines);


    $Globals::ENV{CONFIG} = $CFG_POINTER;

	if ($td_source_lines =~ /\bCREATE\s+PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*\(/is or
		$td_source_lines =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*\(/is
		or	$td_source_lines =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*\.*?\bRETURNS\b/is
		or $td_source_lines =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+\"?\w+\"?\.?\"?\w*\"?\s*\.*?\bIS\b/is)
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
		if($procedure_stmt =~ /\bCREATE\s+OR\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\(\s*\)\s*AS\b.*?BEGIN\b/is)
	{
		
		$procedure_name = $1;
		#$procedure_args = $2;
		#$procedure_vars = $3;
	}
	
	elsif ($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*IS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
		
	}
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\(?(.*?)\)?\s*RETURNS\b/is)
	{
		
		$procedure_name = $1;
		$procedure_args = $2;$MR->log_msg("Begin prescan_procedure_stmt_create");
		$procedure_vars = $3;
		
	}
		elsif($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\(?(.*?)\)?\s*RETURNS\b/is)
	{
		
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
		
	}
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\(?(.*?)\)?\s*IS(.*?)BEGIN\b/is)
	{
		
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
		$MR->log_msg("redshift proc paramsbeso: $procedure_vars");
		
	}
	elsif($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*AS\b\s*\$\$\s+\bDECLARE\b(.*?\bBEGIN\b)\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*AS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s+LANGUAGE\s+plpgsql\s+AS\b\s*\$\$\s+DECLARE(.*?)BEGIN\b/is)
	{$MR->log_msg("redshift proc paramspaata: $procedure_vars");
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s+AS\s+\$\$\s+DECLARE(.*?)BEGIN\b/is)
	{$MR->log_msg("redshift proc paramspaata: $procedure_vars");
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}	
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s+LANGUAGE\s+plpgsql\s+AS\s*\$\$\s+BEGIN\b/is)
	{$MR->log_msg("redshift proc paramspaata: $procedure_vars");
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
    elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s+AS\s+\$\$\s+BEGIN\b/is)
	{$MR->log_msg("redshift proc paramspaata: $procedure_vars");
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s+AS\b\s*\$\$\s+DECLARE(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		$procedure_args = $2;
		$procedure_vars = $3;
	}
	elsif($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*IS\b(.*?)BEGIN\b/is)
	{
		$procedure_name = $1;
		#$procedure_args = $2;
		#$procedure_vars = $3;$MR->log_msg("oracle proc params: $procedure_name");
	}
	elsif($procedure_stmt =~ /\bCREATE\s+PROCEDURE\s+(\"?\w+\"?\.?\"?\w*\"?)\s*AS\b(.*?)BEGIN\b/is)
	{
		
		$procedure_name = $1;
		#$procedure_args = $2;
		#$procedure_vars = $3;
	}
	
	
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

	
	$MR->log_msg("Begin prescan_procedure_stmt_create1".Dumper($procedure_vars));
	my @arg_defs = split(',', $procedure_args);
	my @var_defs = split(';', $procedure_vars);
	my $arg_num = 0;
	foreach my $arg (@arg_defs)
	{
		$MR->log_msg("oracle proc params: $arg");

		$arg = $MR->trim($arg);
		my $args = {};
		my $last_part = '';
		if($arg =~ /(\w+)\s+(\w+)\s+(.*)/is)
		{
			$args->{NAME} = $MR->trim($1);     # No longer converting to upper case
			$args->{ARG_TYPE}  = uc($MR->trim($2));
			$last_part = $MR->trim($3);
			
			if ($last_part =~ /(\w+)\s+DEFAULT\s+(.*)/gis)
			{
                $args->{DATA_TYPE} = $1;
				$args->{VALUE} = $2;
            }
            else
			{
				$args->{DATA_TYPE} = $last_part;
			}
			
			#$args->{DATA_TYPE} = uc($MR->trim($3));
			#$MR->log_msg("redshift proc vars_patr_start:".Dumper(@{$Globals::ENV{PRESCAN}->{PROC_ARGS}}));
			#push (@{$Globals::ENV{PRESCAN}->{PROC_ARGS}}, $args);
			#$MR->log_msg("redshift proc vars_patr_end:".Dumper(@{$Globals::ENV{PRESCAN}->{PROC_ARGS}}));
			#push (@conversion_catalog_add, "stored_procedure_args,$procedure_name,$arg_num" . ':::' . "$1,$2,$3");
			#$arg_num++;
		}
		elsif($arg =~ /(\w+)\s+(\w+)/is)
		{
			
			$args->{NAME} = $MR->trim($1);     # No longer converting to upper case
			$args->{ARG_TYPE} = 'IN';
			$last_part = $MR->trim($2);
			
			$args->{DATA_TYPE} = $last_part;
		}
		
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
	
	foreach my $var (@var_defs)
	{
		
		$var = $MR->trim($var);
		if($var =~ /(\w+)\s+(.*)/is)
		{
			my $vars->{NAME} = $MR->trim($1);
			my $data_type = $MR->trim($2);
			
			if($data_type =~ /\s*(.*?)\s*\:\=\s*(.*)/is)
			{
				$vars->{DATA_TYPE} = $1;
				my $val = $2;
				
				if ($Globals::ENV{CONFIG}->{change_complex_assignment_to_select})
				{
					if ($val =~/\w+\(/is and $val !~ /(select|insert|Update|delete|alter|drop|merge)/is)
					{
						$val = "SELECT ".$val;
						$MR->log_msg("redshift proc vars: $data_type".$val);
					}
				}
				
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
		
	}if ($arg_num == 0)
	{
		push (@conversion_catalog_add, "stored_procedure_args,$procedure_name,x" . ':::');
	}
	

}



sub prescan_function_stmt 
{
	my $function_stmt = shift;
	$MR->log_msg("Begin prescan_function_stmt: $function_stmt");

	my $function_name = '';
	my $function_args = '';
	my $function_vars = '';
	
	if ($function_stmt =~ /\bCREATE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURN\b.*?\bIS\b(.*?)\bBEGIN\b\b/is)
	{
		$function_name = $1;
		$function_args = $2;
		$function_vars = $3;
	}
	elsif($function_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURN\b.*?\bIS\b(.*?)\bBEGIN\b/gis)
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
		$function_vars = $MR->trim($3);
		
	}
	elsif($function_stmt =~ /\bCREATE\s+OR\b\s+REPLACE\s+FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURN\b.*?\bAS\b(.*?)\bBEGIN\b/gis)
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
		$function_vars = $MR->trim($3);
		
	}
	elsif($function_stmt =~ /FUNCTION\s+(\"?\w+\"?\.?\"?\w*\"?)\s*\((.*?)\)\s*RETURN\b.*?\bIS\b(.*?)\bBEGIN\b/gis)
	{
		$function_name = $MR->trim($1);
		$function_args = $MR->trim($2);
		$function_vars = $MR->trim($3);
	}
	
	$Globals::ENV{PRESCAN}->{FUNCTION_NAME} = $function_name;

	my $prescan_function_args = ();

	# Save the "before" in case we need to search through it or report it
	$prescan_function_args->{ORIGINAL_SOURCE} = $function_args;

	$MR->log_msg("oracle function params: $function_args");
	
	my @arg_defs = split(',', $function_args);
	my @var_defs = split(';', $function_vars);
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
			
			#$args->{DATA_TYPE} = uc($MR->trim($3));
			
			push (@{$Globals::ENV{PRESCAN}->{FUNCTION_ARGS}}, $args);
			push (@conversion_catalog_add, "function_args,$function_name,$arg_num" . ':::' . "$1,$2,$3");
			$arg_num++;
		}
	}

	foreach my $var (@var_defs)
	{
		$MR->log_msg("redshift function vars: $var");
		$var = $MR->trim($var);
		if($var =~ /(\w+)\s+(.*)/is)
		{
			my $vars->{NAME} = $MR->trim($1);
			my $data_type = $MR->trim($2);
			if($data_type =~ /\s*(.*?)\s*\:\=\s*(.*)/is)
			{
				$vars->{DATA_TYPE} = $1;
				my $val = $2;
				if ($Globals::ENV{CONFIG}->{change_complex_assignment_to_select})
				{
					if ($val =~/\w+\(/is and $val !~ /(select|insert|Update|delete|alter|drop|merge)/is)
					{
						$val = "SELECT ".$val;
					}
				}
				$vars->{VALUE} = $val;
				$vars->{DEFAULT_VALUE} = $val;
			}
			else
			{
				$vars->{DATA_TYPE} = $data_type;
			}
			push (@{$Globals::ENV{PRESCAN}->{FUNCTION_VARS}}, $vars);
			push (@{$Globals::ENV{PRESCAN}->{VARIABLES}}, $vars);
		}
	}

	if ($arg_num == 0)
	{
		push (@conversion_catalog_add, "functions_args,$function_name,x" . ':::');
	}

}
