use strict;
use Data::Dumper;
use Common::MiscRoutines;

my $PKG_INFO = undef; #holds normalized package info
my $SQL_PARSER = undef; #poiner to SQLParser module to convert sql statements
my $PROCEDURE_PARSER = undef; #poiner to SQL_PROCEDURE_PARSER module to convert sql procedures
my $ETL_PARSER = undef;
my $CONFIG = undef; #pointer to config
my $PKG_VARS = undef; #poiner to a hash with vars
my $PKG_PARAMS = undef; #poiner to a hash with params
my $OUTPUT_FOLDER = undef;
my $MAPPED_TABLES = {};
my $MAPPED_ALL_TABLES = {};
my $INDENT = 0;
my $FILE_NAME = undef;
my $HEADER_CONTENT = '';
my $FOOTER_CONTENT = '';
my $ERROR_MESSAGE_FINAL_COUNT = 0;
my $ERROR_MESSAGE_CURRENT_COUNT = 0;
my $ERROR_IF_LAST_STATEMENT = '';
my $EVERY_STATEMENTS_HEADER = '';
my $EVERY_STATEMENTS_FOOTER = '';
my $SQL_CONTENT = '';
my $WRITER = {};
my $LINK_NAME = {};

my $NO_WRAP_PREFIX = '# Processing Variable';
my $CUSTOM_WRITER_VERSION = "2022-06-16";
my @proc_cont = ();
my $MR = new Common::MiscRoutines(MESSAGE_PREFIX => 'BBCONV');
my $COMMENT_PEFIX = '#';

my @all_tables = ();
my $last_temp_table_index = 1;
my $DELIM = ';';
my $WITH_PREFIX = "WITH____";

sub init_writer #initialize content and vars
{
	my $h = shift;
	$PKG_INFO = $h->{PKG_INFO};
	$PKG_VARS = $h->{PACKAGE_VARIABLES};
	$PKG_PARAMS = $h->{PACKAGE_PARAMETERS};
	$CONFIG = $h->{CONFIG};
	$WRITER = $h->{WRITER};
	$LINK_NAME = $h->{LINK_NAME};
	$OUTPUT_FOLDER = $h->{OUTPUT_FOLDER};
	$SQL_PARSER = $h->{SQL_PARSER};
	$PROCEDURE_PARSER = $h->{PROCEDURE_PARSER};
	$ETL_PARSER = $h->{ETL_PARSER};
	$INDENT = 0;
	$FILE_NAME = $h->{FILE_NAME};
	$HEADER_CONTENT = $h->{HEADER_CONTENT};
	$FOOTER_CONTENT = $h->{FOOTER_CONTENT};
	$ERROR_MESSAGE_FINAL_COUNT = 0;
	$ERROR_MESSAGE_CURRENT_COUNT = 0;
	
	$SQL_CONTENT = '';
	
	delete $CONFIG->{override_sql_statement_variable_list}; #this will be populated by sub parse_sql_params_in_script. but we want to reset it for every job
	
	if($CONFIG->{error_if_last_statement})
	{
		$ERROR_IF_LAST_STATEMENT = $MR->read_file_content($CONFIG->{error_if_last_statement});
	}
	if($CONFIG->{every_statements_header})
	{
		$EVERY_STATEMENTS_HEADER = $MR->read_file_content($CONFIG->{every_statements_header});
	}
	if($CONFIG->{every_statements_footer})
	{
		$EVERY_STATEMENTS_FOOTER = $MR->read_file_content($CONFIG->{every_statements_footer});
	}
	if ($CONFIG->{generate_only_sql_convert})
	{
		$COMMENT_PEFIX = $CONFIG->{sql_comment};
	}
	$MAPPED_ALL_TABLES = {};
	@all_tables = ();
	$last_temp_table_index = 1;
	@proc_cont = ();
	$MR->log_msg("init_writer kicked off for CUSTOM_WRITER_VERSION: $CUSTOM_WRITER_VERSION, Package $PKG_INFO->{NAME}");
}

sub start_script
{
	my $node = shift;
	
	if ($CONFIG->{need_package_variable_and_component_mapping})
	{
		delete $CONFIG->{override_sql_statement_variable_list}; #this will be populated by sub parse_sql_params_in_script. but we want to reset it for every job
	}
	
	$INDENT++;
	#my $start = $HEADER_CONTENT.$CONFIG->{commands}->{BEGIN_TRY};
	my $start = $HEADER_CONTENT.declare_variables_and_params().$CONFIG->{commands}->{BEGIN_TRY};
	#my $start = $CONFIG->{header}.declare_variables_and_params().$CONFIG->{commands}->{BEGIN_TRY};
	$INDENT++;
	return $start;
}

sub finalize_content
{
	my $ar = shift;
	$MR->log_msg("finalize_content:");
	my $content = join("\n", @$ar);
	#my $footer = $CONFIG->{footer};
	$content .= $FOOTER_CONTENT;
	save_content($SQL_CONTENT, 'orig');

	if($CONFIG->{generate_only_sql_convert})
	{
		my $script = join("\n", @proc_cont);
		$script =~ s/\;\s*\;/;/gis;
		while ($script =~ /\;\s*\;/gis)
		{
            $script =~ s/\;\s*\;/;/gis;
        }
        #$script =~ s/^\;\s*//g;
		$script =~  s/\#/$CONFIG->{sql_comment}/gis;

		create_script($script);
		return '';
    }

	@$ar = split(/\n/,$content);
	return $ar;
}

sub declare_variables_and_params
{
	my $return_value = "";

		foreach my $item (keys %$PKG_PARAMS)
	{
		if($CONFIG->{restricted_vars}->{$item})
		{
			next;
		}
		my $value = $PKG_PARAMS->{$item};
		$value =~ s/\n/ /g;
		$value =~ s/\@\[User\:\:(\w+)\]/{V_$1}/g;
		$value =~ s/\@\[System\:\:(\w+)\]/"{$1}"/g;
		$value =~ s/\@\[\$Package\:\:(\w+)\]/"{$1}"/g;

		my $set_var_value = $CONFIG->{commands}->{SET_VAR_VALUE};
		$set_var_value =~ s/\%NAME\%/V_$item/g;
		$set_var_value =~ s/\%VALUE\%/$value/g;
		$return_value .= $set_var_value;
	}
	
	foreach my $item (keys %$PKG_VARS)
	{
		if($CONFIG->{restricted_vars}->{$item})
		{
			next;
		}
		my $value = $PKG_VARS->{$item};
		$value =~ s/\n/ /g;

		$value = change_ternary_operator_to_case_when($value);
		$value = $SQL_PARSER->convert_sql_fragment($value);

		$value =~ s/\@\[User\:\:(\w+)\]/{V_$1}/g;
		$value =~ s/\@\[System\:\:(\w+)\]/"{$1}"/g;
		$value =~ s/\@\[\$Package\:\:(\w+)\]/"{V_$1}"/g;
		

		my $set_var_value = $CONFIG->{commands}->{SET_VAR_VALUE};
		$set_var_value =~ s/\%NAME\%/V_$item/g;
		$set_var_value =~ s/\%VALUE\%/$value/g;
		$return_value .= $set_var_value;
	}
	
	return $return_value."\n\n";
}

# ?: to case when
sub change_ternary_operator_to_case_when
{
	my $expr = shift;
	if ($expr =~ /(.*)\?(.*)\:(.*)/is)
	{
        $expr = "CASE WHEN $1 THEN $2 ELSE $3 END";
    }
    return $expr;
}

sub query_work_unit
{
	my $node = shift;
	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n";
	my @param_vars = get_param_names($node->{PARAM_BINDING});
	my @result_vars = get_param_names($node->{RESULT_BINDING});

	$ret .= "$COMMENT_PEFIX input parameters :\n";

	my $param_names = '';
	my $param_values = '';
	foreach(@param_vars)
	{
		$ret .= "	$COMMENT_PEFIX $_ \n";
		if ($param_names ne '')
		{
            $param_names .= ',';
			$param_values .= ',';
        }

		$param_values .= $PKG_INFO->{PACKAGE_VARIABLE_DETAILS}->{$_}->{VALUE};
		$param_names .= "$_ = $PKG_INFO->{PACKAGE_VARIABLE_DETAILS}->{$_}->{VALUE}";
	}

    
	#$MR->log_error(Dumper($PKG_INFO->{PACKAGE_VARIABLE_DETAILS}->{$_}->{VALUE}));
	
	$ret .= "$COMMENT_PEFIX output parameters :\n";
	foreach(@result_vars)
	{
		$ret .= "	$COMMENT_PEFIX $_ \n";
	}
	my $wrap_templaet = $CONFIG->{commands}->{WRAP};
	if ($#result_vars > -1)
	{
        $wrap_templaet = $CONFIG->{commands}->{SET_WRAP};
    }
    
	if ($node->{SQL_STATEMENT} && $node->{SQL_STATEMENT} =~ /^\s*\w+\.?\w*\s*$/)
	{
		
		$ret .= "# $param_names\n";
		$ret .="spark.sql(f\"\"\"CALL $node->{SQL_STATEMENT}($param_values)\"\"\")"
    }
	elsif($node->{PROPERTY_EXPRESSION})
	{
		if ($CONFIG->{generate_only_sql_convert})
		{
			push(@proc_cont,$ret);
			push(@proc_cont,"\n".$PROCEDURE_PARSER->convert_sql_fragment($node->{PROPERTY_EXPRESSION}[0]->{content}).';');
			$ret = '';
		}
		$wrap_templaet =~ s/\%SQL\%/$node->{PROPERTY_EXPRESSION}[0]->{content}/gis;
		$wrap_templaet =~ s/\%VARIABLE\%/$result_vars[0]/gis;
		$ret .= $wrap_templaet;
		if ($#result_vars > -1)
		{
			$ret .= ".collect()[0][0]";
		}
		$ret .= "\n\n".'"""" expression  :'. $node->{PROPERTY_EXPRESSION}[0]->{content} .'""'. "\n";
		$SQL_CONTENT .= $node->{PROPERTY_EXPRESSION}[0]->{content}."\n";

	}
	else
	{
		if ($CONFIG->{generate_only_sql_convert})
		{
			push(@proc_cont,$ret);
			push(@proc_cont,"\n".$PROCEDURE_PARSER->convert_sql_fragment($node->{SQL_STATEMENT}).';');
			$ret = '';
		}
		
		$node->{SQL_STATEMENT} = $SQL_PARSER->preprocess_add_delimiters($node->{SQL_STATEMENT});
		$node->{SQL_STATEMENT} = mark_separators($node->{SQL_STATEMENT});
		
		#$node->{SQL_STATEMENT} =~ s/\bIF OBJECT_ID\b/;\nIF OBJECT_ID/g;
		$node->{SQL_STATEMENT} =~ s/\/\*.*?\*\///gs;
		$node->{SQL_STATEMENT} =~ s/\/\*\*.*?\*\*\///gs;
		$node->{SQL_STATEMENT} =~ s/\;WITH\b/\;\nWITH/gs;
		$node->{SQL_STATEMENT} =~ s/\;\s*\;/;/gs;

		my @fragments = split_sql_into_fragments($node->{SQL_STATEMENT});
		$MR->log_msg("Number of sql fragments: " . scalar(@fragments) . " Content: " . ref($node->{SQL_STATEMENT}) . " len: " . length($node->{SQL_STATEMENT}));

		if ($#fragments > 0)
		{
            foreach my $fr (@fragments)
			{
				my $frag = join("\n", @$fr);
				$frag =~ s/\s*\;\s*$//s;
				$frag =~ s/^\s*\;//s;
				if ($MR->trim($frag) eq '')
				{
                    next;
                }
				
				my $is_converted = 0;
				foreach my $stmt_category (@{$CONFIG->{stmt_categorization_patterns}})
				{
					foreach my $pattern (@{$stmt_category->{patterns}})
					{
						if ($frag =~ /$pattern/is)
						{
							my $func_name = $CONFIG->{fragment_handling}->{$stmt_category->{category}};
							my $func_call = $func_name . '($frag);';
							my $result = eval($func_call);
							my $f_ret = $@;
							if ($f_ret)
							{
								$MR->log_error("ERROR EXECUTING FUNCTION generate_$func_call, Eval Returned:\n$f_ret");
								$result = "# ---------- No handler defined for type $func_call, node $node->{NAME}, ---------- #";
								$MR->log_error($result);
							}
							else
							{
								$ret .= $result;
							}
							$is_converted = 1;
                            last;
                        }
					}
					if ($is_converted)
					{
                        last;
                    }
				}
				
				if (!$is_converted)
				{
					$frag = $SQL_PARSER->convert_sql_fragment(@$fr);
	
					$frag =~ s/\s*\;\s*$//s;
					$frag =~ s/^\s*\;//s;
					if ($MR->trim($frag) eq '')
					{
						next;
					}
	
					$wrap_templaet = $CONFIG->{commands}->{WRAP};
					$wrap_templaet =~ s/\%SQL\%/$frag/gis;
					$ret .= $wrap_templaet;
                }
			}
        }
        else
		{
			$wrap_templaet =~ s/\%SQL\%/$node->{SQL_STATEMENT}/gis;
			$wrap_templaet =~ s/\%VARIABLE\%/$result_vars[0]/gis;
			$wrap_templaet = $SQL_PARSER->convert_sql_fragment($wrap_templaet);
			$ret .= $wrap_templaet;
			if ($#result_vars > -1)
			{
				$ret .= ".collect()[0][0]";
			}
			#$ret .= "\n\n".'""" expression  :'. $node->{SQL_STATEMENT} .'"""'. "\n";			
		}

		$SQL_CONTENT .= $node->{SQL_STATEMENT}."\n";
	}
	$ret =~ s/\"\"\"\"/"""/gis;
	$ret =~ s/$WITH_PREFIX//gim;
	return code_indent($ret);
}

sub code_indent
{
	my $code = shift;
	return $code unless $CONFIG->{code_indent};
	my @lines = split(/\n/, $code);
	foreach my $ln (@lines)
	{
		my $spaces = '';
		my $cfg_indents = $CONFIG->{code_indent} =~ tr/\t//;
		$MR->log_msg("code_indent1:: ''''$INDENT''''");
		$cfg_indents--;
		for(my $i=0; $i<$INDENT + $cfg_indents; $i++)
		{
			$spaces .= "\t";
		}
		$ln = $spaces . $ln;
	}
	my $ret = join("\n", @lines);
	#pop(@lines) if $lines[-1] =~ //
	$ret =~ s/\;\s*$//gis; #get rid of trailing semicolon
	$ret =~ s/\s*$//gis;
	$MR->log_msg("code_indent:: ''''$ret''''");
	return $ret;
}

my $iter = 1;
#looks for certain attributes in VB or C# script and tries to parse them
sub parse_sql_params_in_script
{
	my $node = shift;
	my $script = get_script_content($node);
	return "" unless $script;

	#look for all assignments into src_SQL variable
	my @assignment_list = ($script =~ /(src_SQL\s*\=\s*.*?;)/gis);
	if ($#assignment_list >= 0)
	{
		$MR->log_msg("Assignments in VB Script Found : " . Dumper(\@assignment_list));
	}
	else
	{
		$MR->log_error("Cannot find variable assignments in $PKG_INFO->{NAME}.$node->{NAME}!");
		return undef;
	}
	
	$iter += 1;
	#get the last assignment operator that has var concatenations

	my $final_assignment = '';
	my @vars_used_in_assignment = ();
	foreach my $snippet (reverse @assignment_list)
	{
		if ($snippet =~ /Dts\.Variables.*User\:\:/)
		{
			$final_assignment = $snippet;
			@vars_used_in_assignment = $final_assignment =~ /user::(\w+)/gis;
			$MR->log_msg("Final assignment: $final_assignment");
			$MR->log_msg("Final assignment: vars: " . Dumper(\@vars_used_in_assignment));
			if ($CONFIG->{need_package_variable_and_component_mapping})
			{
				$CONFIG->{override_sql_statement_variable_list}->{$node->{NAME}} = \@vars_used_in_assignment;
            }
            else
			{
				$CONFIG->{override_sql_statement_variable_list} = \@vars_used_in_assignment;
			}
			last;
		}
	}

	return undef;
}

sub get_script_content
{
	my $node = shift;
	if ($node->{VB_OR_CS_SCRIPT}) #array of hashes
	{
		foreach my $el (@{$node->{VB_OR_CS_SCRIPT}})
		{
			next unless ($el->{Name} eq 'ScriptMain.cs' or $el->{Name} eq 'ScriptMain.vb');
			my $cont = $el->{content};
			if ($el->{Name} eq 'ScriptMain.vb')
			{
				$cont =~ s/$/;/gm; #add semicolon at the end of each line
			}
			
			my $extension_file = $el->{Name};
			$extension_file =~ s/.*\././gis;
			#$MR->log_error(Dumper($node));
			my $cs_or_vb_fp = $OUTPUT_FOLDER . '/' . $node->{LOCAL_NAME} . $extension_file;
			$MR->log_msg("Using file for c# or vb storage: $cs_or_vb_fp");
			$MR->write_file($cs_or_vb_fp, $cont);
			
			return $cont;
		}
	}
	$MR->log_error("Cannot find script in node $PKG_INFO->{NAME}.$node->{NAME}");
	return undef;
}

sub exec_sql_block
{
	my $node = shift;

	my @var_list = ();
	my @var_comp_name;
	if ($CONFIG->{need_package_variable_and_component_mapping})
	{
		if($CONFIG->{package_variable_and_component_mapping}->{$PKG_INFO->{NAME}}->{$node->{NAME}})
		{
			@var_comp_name = @{$CONFIG->{package_variable_and_component_mapping}->{$PKG_INFO->{NAME}}->{$node->{NAME}}};
			
			foreach(@var_comp_name)
			{
				@var_list = (@var_list,$CONFIG->{override_sql_statement_variable_list}->{$_}?@{$CONFIG->{override_sql_statement_variable_list}->{$_}}:@{$CONFIG->{sql_statement_variable_list}});
			}
		}
		else
		{
			@var_list = $CONFIG->{override_sql_statement_variable_list}?@{$CONFIG->{override_sql_statement_variable_list}}:@{$CONFIG->{sql_statement_variable_list}};
		}
	}
	else
	{
		@var_list = $CONFIG->{override_sql_statement_variable_list}?@{$CONFIG->{override_sql_statement_variable_list}}:@{$CONFIG->{sql_statement_variable_list}};
	}

	return "$COMMENT_PEFIX No vars specified in config entry sql_statement_variable_list" unless $#var_list >= 0;  #unless $CONFIG->{sql_statement_variable_list};
	my @stmt_list = (); #array of statements from vars

	foreach my $var (@var_list)
	{
		next unless $PKG_VARS->{$var};
		if(substr($PKG_VARS->{$var}, 0,1) eq '"')
		{
			$PKG_VARS->{$var} = substr $PKG_VARS->{$var}, 1;
		}
		if(substr($PKG_VARS->{$var}, -1) eq '"')
		{
			chop $PKG_VARS->{$var};
		}
		
		push(@stmt_list, "$NO_WRAP_PREFIX $var;\n", $PKG_VARS->{$var});
		$MR->log_msg("Using var for sql execution: $var");
	}
	my $content = join("\n", @stmt_list);
	#$content = $SQL_PARSER->convert_sql_fragment($content);
	my @ret = ();
	#my @proc_cont = ();
	my $proc_start = 0;
	push(@ret, "# Using the following package variables to generate SQL: " . join(', ', @var_list));
	$MAPPED_TABLES = {};
	$SQL_CONTENT .= $content."\n";
	#save_content($content, 'orig');
	
	if ($CONFIG->{multi_level_var_subst})
	{
       	$content =~ s/^\s*\-\-+\s*\@\[.*?$//gm;
		foreach my $item (keys %$PKG_VARS)
		{
			my $val = $PKG_VARS->{$item};
			$content =~ s/\@\[User\:\:$item\]\s*\+?/$val/gis;
		}
    }

	my $comm = collect_tables_in_to_hash($content);
	push(@ret, $comm);
	
	foreach my $key (sort { length $b <=> length $a } keys %$MAPPED_TABLES)
	{
		my $reg_name =$MAPPED_TABLES->{$key}->{REGEX_NAME};
		my $value = $MAPPED_TABLES->{$key}->{VALUE};
		if ($key =~ /\..*?\.(.*?\..*)/g)
		{
			my $short_tbl_name = $1;
			if ($MAPPED_TABLES->{$short_tbl_name})
			{
                $value = $MAPPED_TABLES->{$short_tbl_name}->{VALUE};
            }
		}		
		$MR->log_msg("Value: $reg_name");
		$content =~ s/$reg_name/$value/g;
	}

	foreach my $key (sort { length $b <=> length $a } keys %$MAPPED_ALL_TABLES)
	{
		my $reg_name =$MAPPED_ALL_TABLES->{$key}->{REGEX_NAME};
		my $value = $MAPPED_ALL_TABLES->{$key}->{VALUE};
		if ($key =~ /\..*?\.(.*?\..*)/g)
		{
			my $short_tbl_name = $1;
			if ($MAPPED_ALL_TABLES->{$short_tbl_name})
			{
                $value = $MAPPED_ALL_TABLES->{$short_tbl_name}->{VALUE};
            }
		}		
		$MR->log_msg("Value: $reg_name");
		$content =~ s/$reg_name/$value/g;
	}
	
	my @fragments = split_sql_into_fragments($content);
	$MR->log_msg("Number of sql fragments: " . scalar(@fragments) . " Content: " . ref($content) . " len: " . length($content));
	
	foreach my $fr (@fragments)
	{
		my $frag = $SQL_PARSER->convert_sql_fragment(@$fr);
		my $fra_cont = join("\n", $frag);
		#$MR->log_error("post : $fra_cont_procedure");
		$fra_cont =~ s/^\s*\-\-.*//gm;
		$fra_cont =~ s/^\s+|\s+$//g;
		
		if($fra_cont =~ /^CREATE\s+TABLE/gi)
		{
			if($fra_cont =~ /\bERROR_MESSAGE\b/i)
			{
				$ERROR_MESSAGE_FINAL_COUNT += 1;
			}
		}
	}
	foreach my $fr (@fragments)
	{
		my $frag = $SQL_PARSER->convert_sql_fragment(@$fr);
		my $fr_for_procedure = $PROCEDURE_PARSER->convert_sql_fragment(@$fr);
		my $fra_cont = join("\n", $frag);
		
	#custom convert

	$fra_cont =~ s/(\'\{\w+\}\')\s*\:\:\s*(Varchar)/cast($1 as $2)/gis;
	$fra_cont =~ s/(\{\w+\})\s*\:\:\s*(Varchar)/cast($1 as $2)/gis;
	$fra_cont =~ s/(\w+)\s*\:\:\s*(Varchar)/cast($1 as $2)/gis;
	$fra_cont =~ s/(\"\{\w+\}\")\s*\:\:\s*(Varchar)/cast($1 as $2)/gis;

	$fra_cont =~ s/(\'\{\w+\}\')\s*\:\:\s*Numeric\s*(\(.*?\))/cast($1 as Decimal$2)/gis;
	$fra_cont =~ s/(\{\w+\})\s*\:\:\s*Numeric\s*(\(.*?\))/cast($1 as Decimal$2)/gis;
	$fra_cont =~ s/(\w+)\s*\:\:\s*Numeric\s*(\(.*?\))/cast($1 as Decimal$2)/gis;
	$fra_cont =~ s/(\"\{\w+\}\")\s*\:\:\s*Numeric\s*(\(.*?\))/cast($1 as Decimal$2)/gis;

	$fra_cont =~ s/(\'\{\w+\}\')\s*\:\:\s*Date/to_date($1, 'yyyyMMdd')/gis;
	$fra_cont =~ s/(\{\w+\})\s*\:\:\s*Date/to_date($1, 'yyyyMMdd')/gis;
	$fra_cont =~ s/(\w+)\s*\:\:\s*Date/to_date($1, 'yyyyMMdd')/gis;
	$fra_cont =~ s/(\"\{\w+\}\")\s*\:\:\s*Date/to_date($1, 'yyyyMMdd')/gis;
	
	#custom convert
		
		
		#	custom cast changes expression :: type to cast(expression, type)
		$fra_cont = custom_cast($fra_cont);
		
		#$MR->log_error("pre : $fra_cont");
		my $fra_cont_procedure = join("\n", $fr_for_procedure);
		if ($CONFIG->{generate_only_sql_convert})
		{
			$fr_for_procedure = custom_cast($fr_for_procedure);
			#$fr_for_procedure = not_exist_to_left_join($fr_for_procedure);
			push(@proc_cont, $fr_for_procedure);
			next;
        }
		#$MR->log_error("post : $fra_cont_procedure");
		$fra_cont =~ s/^\s*\-\-.*//gm;
		$fra_cont =~ s/^\s+|\s+$//g;
		if ($proc_start == 1)
		{
			push(@proc_cont, $fr_for_procedure);
			next;
        }
		$fra_cont =~ s/;$//gis;
        
		if($fra_cont eq '')
		{
			next;
		}
		my $tbl_name;
		if($fra_cont =~ /^CREATE\s+TABLE/gi)
		{
			($fra_cont,$tbl_name) = generate_CREATE_TABLE($fra_cont);
			$EVERY_STATEMENTS_FOOTER =~ s/\%TABLE\%/$tbl_name/gis;
			$fra_cont = $EVERY_STATEMENTS_HEADER. $fra_cont. $EVERY_STATEMENTS_FOOTER;
			push(@ret, $fra_cont);
		}
		elsif($fra_cont =~ /^INSERT\s+INTO/gi)
		{
			($fra_cont,$tbl_name) = generate_INSERT($fra_cont);
			$EVERY_STATEMENTS_FOOTER =~ s/\%TABLE\%/$tbl_name/gis;
			$fra_cont = $EVERY_STATEMENTS_HEADER. $fra_cont. $EVERY_STATEMENTS_FOOTER;
			push(@ret, $fra_cont);
		}
		elsif($fra_cont =~ /^UPDATE\s+/gi)
		{
			(my $up_cont,$tbl_name) = generate_UPDATE($fra_cont);
			$EVERY_STATEMENTS_FOOTER =~ s/\%TABLE\%/$tbl_name/gis;
			$fra_cont = $EVERY_STATEMENTS_HEADER. $fra_cont. $EVERY_STATEMENTS_FOOTER;
			if ($CONFIG->{generate_procedure_after_update})
			{
				$proc_start = 1;
				push(@proc_cont, $fra_cont_procedure.';');		
			}
			push(@ret, $up_cont);
		}
		elsif($fra_cont =~ /^DELETE\s+/gi)
		{
			(my $dl_cont,$tbl_name) = generate_DELETE($fra_cont);
			$EVERY_STATEMENTS_FOOTER =~ s/\%TABLE\%/$tbl_name/gis;
			$fra_cont = $EVERY_STATEMENTS_HEADER. $fra_cont. $EVERY_STATEMENTS_FOOTER;
			if ($CONFIG->{generate_procedure_after_delete})
			{
				$proc_start = 1;
				push(@proc_cont, $fra_cont_procedure.';');		
			}
			push(@ret, $dl_cont);
		}
		elsif($fra_cont =~ /$NO_WRAP_PREFIX/)
		{
			$fra_cont = code_indent($fra_cont);
			push(@ret, $fra_cont);
		}
		else
		{
			my @sql = wrap_sql_statement($fra_cont); #returns array of lines
			push(@ret, $MR->trim(join("\n", @sql)));
		}
	}
	
	if (!$CONFIG->{generate_only_sql_convert})
	{
		if($#proc_cont > -1)
		{
			my $proc = "\n" . join("\n", @proc_cont);
			$proc =~ s/\;\s*\;/;/gis;
			create_procedure($proc);
		}
		
		my $pre_node_line = get_pre_node_line($node);
		return $pre_node_line . "\n" . join("\n\n", @ret);
	}
	else
	{
		push(@proc_cont, $comm);
	}

	#return $content;
}

############## Supporting routines ##############

sub get_pre_node_line
{
	my $node = shift;
	my $ln = $CONFIG->{pre_node_line};
	my %subst = (
		'%NODE_NAME%' => $node->{NAME},
		'%NODE_TYPE%' => $node->{USER_TYPE},
		'%USER_TYPE%' => $node->{USER_TYPE}
	);
	$ln = $MR->replace_all($ln, \%subst);
	return $ln;
}

sub wrap_sql_statement
{
	my $sql = shift;
	$sql =~ s/;$//gis;
	$sql = code_indent("spark.sql(\"\"\"$sql\"\"\")");
	$sql =~ s/\"\"\"\"/"""/gis;
	return $sql;
}

# returns array of params out of input/output structures
sub get_param_names
{
	my $struct = shift;
	my @ret = ();
	foreach my $el (@$struct)
	{
		my $var = $el->{'SQLTask:DtsVariableName'};
		$var = $1 if $var =~ /\w+::(\w+)/;
		push(@ret, $var);
	}
	return @ret;
}

sub split_sql_into_fragments
{
	my $content = shift;
	my $tmp_fn = $OUTPUT_FOLDER . '/' . $PKG_INFO->{NAME} . $$ . '_' . $MR->get_current_datetime_YYYYMMDD_HHMMSS() . '.sql';
	$MR->log_msg("Using file for temp storage: $tmp_fn");
	$MR->write_file($tmp_fn, $content);
	my @fragments = $SQL_PARSER->get_code_fragments($tmp_fn);
	unlink $tmp_fn unless $CONFIG->{save_debug_info}->{create_sql_debug_files};
	#$MR->log_msg("FRAGMENTS RETURNED: " . Dumper(\@fragments));
	return @fragments;
}

sub split_sql_procedure_into_fragments
{
	my $content = shift;
	my $tmp_fn = $OUTPUT_FOLDER . '/' . $PKG_INFO->{NAME} . $$ . '_' . $MR->get_current_datetime_YYYYMMDD_HHMMSS() . '.sql';
	$MR->log_msg("Using file for temp storage: $tmp_fn");
	$MR->write_file($tmp_fn, $content);
	my @fragments = $SQL_PARSER->get_code_fragments($tmp_fn);
	unlink $tmp_fn unless $CONFIG->{save_debug_info}->{create_sql_debug_files};
	#$MR->log_msg("FRAGMENTS RETURNED: " . Dumper(\@fragments));
	return @fragments;
}

sub loop_start
{
	my $node = shift;
	$MR->debug_msg("Loop encountered");
	return "";
}

sub save_content
{
	my $content = shift;
	my $type = shift; #should be original or converted
	my $tmp_fn = $type =~ /orig/i?$CONFIG->{save_debug_info}->{original_sql_file_pattern}:$CONFIG->{save_debug_info}->{converted_sql_file_pattern};
	if(!$tmp_fn)
	{
		$MR->log_error("no debug template found for $type!");
		return undef;
	}
	$tmp_fn = $OUTPUT_FOLDER . '/' . $tmp_fn;
	my %subst = (
		'%PACKAGE_NAME%' => $PKG_INFO->{NAME},
		'%PID%' => $$,
		'%TIMESTAMP%' => $MR->get_current_datetime_YYYYMMDD_HHMMSS()
	);

	$tmp_fn = $MR->replace_all($tmp_fn, \%subst);

	$MR->log_msg("Using file for storage, type $type: $tmp_fn");
	
	$MR->write_file($tmp_fn, $content);
}

sub collect_tables_in_to_hash
{
	my $content	= shift;
	
	my %hashed_tbl = map{$_=>1} @all_tables;
	
#	I have to add to config
	
	my @tables = ();
	$content =~ s/\s*\-\-.*//gm;
	foreach my $tbl_template (@{$CONFIG->{table_name_trappers}})
	{
		@tables = (@tables, $content=~ /$tbl_template/gis);
	}
	
	if($#tables == -1)
	{
		return '';
	}
	#$last_temp_table_index = 1;
	my $return_text = "\n$COMMENT_PEFIX ALL tables have been replaced from ---> to:\n\n";
	foreach my $table (@tables)
	{
		if ($table !~ /\$/i)
		{
            if ($table !~ /\./i)
			{
				next;
			}
        }

		if($table eq '')
		{
			next;
		}
		$table = $MR->trim($table);
		#$table =~ s/\(.*//gs;
		#$table =~ s/\).*//gs;
        foreach my $cl_templ (@{$CONFIG->{table_name_cleaner}})
		{
			$table =~ s/$cl_templ//gs;
		}
		my $last_symbol = substr($table, -1);
		if($last_symbol eq ';' or $last_symbol eq ',')
		{
			chop($table);
		}

		if ($hashed_tbl{$table})
		{
            next;
        }
        
		if(!$MAPPED_ALL_TABLES->{$table})
		{
			my $copied_name = $MR->deep_copy($table);
			$copied_name =~ s/\$/\\\$/g;
			$copied_name =~ s/{/\\{/g;
			$copied_name =~ s/}/\\}/g;
			$copied_name =~ s/\./\\./g;
            
			$MAPPED_ALL_TABLES->{$table} = {VALUE => "Temp_Table_$last_temp_table_index", REGEX_NAME => $copied_name};			
		}
		
		if(!$MAPPED_TABLES->{$table})
		{
			my $copied_name = $MR->deep_copy($table);
			$copied_name =~ s/\$/\\\$/g;
			$copied_name =~ s/{/\\{/g;
			$copied_name =~ s/}/\\}/g;
			$copied_name =~ s/\./\\./g;
            
			$MAPPED_TABLES->{$table} = {VALUE => "Temp_Table_$last_temp_table_index", REGEX_NAME => $copied_name};
			$return_text .= "$COMMENT_PEFIX'$table'   ---> Temp_Table_$last_temp_table_index\n";
			$last_temp_table_index ++;
		}

	}
	@all_tables = (@all_tables,@tables);
	return $return_text;
}

sub generate_CREATE_TABLE
{
	my $content = shift;
	$content =~ s/;$//gis;
	$MR->log_msg("Started generate_CREATE_TABLE");
	$content = $MR->trim($content);
	my $error_if_last_template = $MR->deep_copy($ERROR_IF_LAST_STATEMENT);
	my $create_table_template;
	my $create_temp_view_template;
	my $tbl_name;
	if($content =~ /^CREATE\s+TABLE\b\s*(\w+)\s*\((.*?)\)\s*\bAS\b(.*)/is)
	{
		$tbl_name = $MR->trim($1);
		my $select = $3;
		$create_table_template = $CONFIG->{commands}->{CREATE_TABLE_AS_SELECT_TEMPLATE};
		$create_temp_view_template = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
		$create_table_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
		$error_if_last_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
		$create_temp_view_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
		
#		if ($select =~ /\bSPLIT_TO_COLUMNS_TRIM\b/)
#		{
#            my $custom_query = toolkit_split_to_columns($select);
#			$create_temp_view_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
#			return code_indent("$custom_query$create_table_template");
#        }
		$create_table_template =~ s/\%CREATE_TABLE_SELECT\%/$select/gi;
		$create_table_template = $create_table_template.$create_temp_view_template;
		#return $create_table_template;
	}
	elsif($content =~ /^CREATE\s+TABLE\b\s*(\w+)\s*\bAS\b(.*)/is)
	{
		$tbl_name = $MR->trim($1);
		my $select = $2;
		$create_table_template = $CONFIG->{commands}->{CREATE_TABLE_AS_SELECT_TEMPLATE};
		$create_temp_view_template = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
		
		$create_table_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
		$error_if_last_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
		$create_table_template =~ s/\%CREATE_TABLE_SELECT\%/$select/gi;
		$create_temp_view_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
		
#		if ($select =~ /\bSPLIT_TO_COLUMNS_TRIM\b/)
#		{
#            my $custom_query = toolkit_split_to_columns($select);
#			$create_temp_view_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
#			return code_indent("$custom_query$create_table_template");
#        }
		
		$create_table_template = $create_table_template.$create_temp_view_template;
		#return $create_table_template;
	}
	elsif($content =~ /^CREATE\s+TABLE\b\s*(.*?)\((.*)\)/is)
	{
		$tbl_name = $MR->trim($1);
		my $cols = generate_COLUMNS($2);
		$create_table_template = $CONFIG->{commands}->{CREATE_TABLE_TEMPLATE};
		$create_table_template =~ s/\%SRC_TABLE\%/$tbl_name/g;
		$error_if_last_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
		$create_table_template =~ s/\%COLUMNS\%/$cols/g;
		#return $create_table_template;
	}
	else
	{
		my $wrap_template = $CONFIG->{commands}->{WRAP};
		$wrap_template =~ s/\%SQL\%/$content/gi;
		return code_indent($wrap_template);
	}
	if($create_table_template =~ /\bERROR_MESSAGE\b/i)
	{
		$ERROR_MESSAGE_CURRENT_COUNT += 1;
		if($ERROR_MESSAGE_CURRENT_COUNT == $ERROR_MESSAGE_FINAL_COUNT)
		{
            $create_table_template .= $error_if_last_template;
        }
        
	}
	return (code_indent($create_table_template),$tbl_name);
}

sub generate_INSERT
{
	my $content = shift;
	$content =~ s/;$//gis;
	$MR->log_msg("Started generate_INSERT");
	$content = $MR->trim($content);
	my $ret = '';
	$ret = '';
	my $insert_to_select = $CONFIG->{insert_to_select_word};
	my $create_table_template = $CONFIG->{commands}->{CREATE_TABLE_AS_SELECT_TEMPLATE};
	my $create_temp_view_template = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
	my $sub_table_name = 'Sub_Table';

	if($content =~ /^INSERT\s+INTO\b\s*(\w+.?\w*)\s*(\bSELECT\b.*)/is)
	{
		my $tbl_name = $1;
		my $select = $2;

		$tbl_name = $MR->trim($tbl_name);

		my $format_columns = '';
		if ($select =~ /\bnot\s+exists\b\s*\(/)
		{
			$create_table_template = $CONFIG->{commands}->{CREATE_TABLE_AS_SELECT_TEMPLATE_FORMAT};
			($select,$format_columns) = not_exist_to_left_join($select);
		}
		$create_table_template =~ s/\%SRC_TABLE\%/Sub_Table/gi;
		$create_table_template =~ s/\%CREATE_TABLE_SELECT\%/$select/gi;
		$create_table_template =~ s/\%COLUMNS\%/$format_columns/gi;
		$create_temp_view_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
		
		if ($select =~ /\bSPLIT_TO_COLUMNS_TRIM\b/)
		{
            (my $custom_query, $sub_table_name) = toolkit_split_to_columns($select);
			$create_temp_view_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
			$create_table_template = $custom_query;
        }
		
		if($insert_to_select and $select =~/\b$insert_to_select\b/)
		{
			$create_table_template = $create_table_template.$create_temp_view_template;
			return (code_indent($create_table_template),$tbl_name);
		}
		my $insert_table_template = $CONFIG->{commands}->{INSERT_INTO};
		$insert_table_template =~ s/\%TGT_TABLE\%/$tbl_name/gi;
		$insert_table_template =~ s/\%INSERTED_TABLE_NAME\%/Sub_Table/gi;
		$ret .= code_indent("$create_table_template$insert_table_template$create_temp_view_template");
		return ($ret,$tbl_name);
	}
	elsif($content =~ /^INSERT\s+INTO\b\s*(\w+.?\w*)\s*\(.*?\)\s*(.*)/is)
	{
		my $tbl_name = $1;
		my $select = $2;

		$tbl_name = $MR->trim($tbl_name);

		my $format_columns = '';
		if ($select =~ /\bnot\s+exists\b\s*\(/)
		{
			$create_table_template = $CONFIG->{commands}->{CREATE_TABLE_AS_SELECT_TEMPLATE_FORMAT};
			($select,$format_columns) = not_exist_to_left_join($select);
		}
		
		$create_table_template =~ s/\%SRC_TABLE\%/$sub_table_name/gi;
		$create_table_template =~ s/\%CREATE_TABLE_SELECT\%/$select/gi;
		$create_table_template =~ s/\%COLUMNS\%/$format_columns/gi;
		
		if ($select =~ /\bSPLIT_TO_COLUMNS_TRIM\b/)
		{
            (my $custom_query, $sub_table_name) = toolkit_split_to_columns($select);
			$create_temp_view_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
			$create_table_template = $custom_query;
        }
		
		$create_temp_view_template =~ s/\%SRC_TABLE\%/$tbl_name/gi;
		if($insert_to_select and $select =~/\b$insert_to_select\b/)
		{
			$create_table_template = $create_table_template.$create_temp_view_template;
			return (code_indent($create_table_template),$tbl_name);
		}		
		my $insert_table_template = $CONFIG->{commands}->{INSERT_INTO};
		$insert_table_template =~ s/\%TGT_TABLE\%/$tbl_name/gi;
		$insert_table_template =~ s/\%INSERTED_TABLE_NAME\%/$sub_table_name/gi;
		$ret .= code_indent("$create_table_template$insert_table_template$create_temp_view_template");
		return ($ret,$tbl_name);
	}
	else
	{
		my $wrap_template = $CONFIG->{commands}->{WRAP};
		$wrap_template =~ s/\%SQL\%/$content/gi;
		return code_indent($wrap_template);
	}
}

sub generate_UPDATE
{
	my $content = shift;
	$MR->log_msg("Started generate_UPDATE");
	$content =~ s/;$//gis;
	$content = $MR->trim($content);
	my $redshift_command = $CONFIG->{commands}->{REDSHIFT_COMMAND};
	#my $proc_name = $CONFIG->{commands}->{procedure_name};

	$content =~ /\bUPDATE\b\s*(.*?)\s+/gis;
	my $tbl_name = $1;
	if (!$CONFIG->{generate_procedure_after_update})
	{
		my $update = $CONFIG->{commands}->{WRAP};
		$update =~ s/\%SQL\%/$content/gi;
		#my $ret = $redshift_command;
		#$ret .= code_indent("\n$update");
		return (code_indent("$redshift_command\n$update"),$tbl_name);
    }
    
	$redshift_command =~ s/\%PROCEDURE_NAME\%/$FILE_NAME/gis;
	return (code_indent("$redshift_command"),$tbl_name);	
}

sub generate_DELETE
{
	my $content = shift;
	$MR->log_msg("Started generate_DELETE");
	$content =~ s/;$//gis;
	$content = $MR->trim($content);
	my $redshift_command = $CONFIG->{commands}->{REDSHIFT_COMMAND};
	#my $proc_name = $CONFIG->{commands}->{procedure_name};
	$content =~ /\bDELETE\b\s*(.*?)\s+/gis;
	my $tbl_name = $1;
	if (!$CONFIG->{generate_procedure_after_delete})
	{
		my $delete = $CONFIG->{commands}->{WRAP};
		$delete =~ s/\%SQL\%/$content/gi;
		return (code_indent("$redshift_command\n$delete"),$tbl_name);
    }
    
	$redshift_command =~ s/\%PROCEDURE_NAME\%/$FILE_NAME/gis;
	return (code_indent("$redshift_command"),$tbl_name);
}

sub generate_COLUMNS
{
	my $columns = shift;
	my @split = split(/\,/,$columns);
	my $cols = '';
	foreach my $item (@split)
	{
		my $column_template = $CONFIG->{commands}->{COLUMN};
		$item = $MR->trim($item);
		if($item =~ /^(\w+)/)
		{
			if($cols ne '')
			{
				$cols .= ',';
			}
			my $col_name = $1;
			$column_template =~ s/\%COLUMN_NAME\%/$col_name/gis;
			$cols .= $column_template;
		}
	}
	return $cols;
}

sub generate_COLUMNS_OLD
{
	my $columns = shift;
	my @split = split(/\,/,$columns);
	my $cols = '';
	foreach my $item (@split)
	{
		$item = $MR->trim($item);
		if($item =~ /^(\w+)/)
		{
			if($cols ne '')
			{
				$cols .= ',';
			}
			$cols .= '"'.$1.'"';
		}
	}
	return $cols;
}

sub create_procedure
{
	my $text = shift;

	#my $file_name = $OUTPUT_FOLDER.'/'.$CONFIG->{file_name}.'.sql';
	my $file_name = $OUTPUT_FOLDER.'/'.$FILE_NAME.'.sql';
	#$file_name =~ s/\%PROCEDURE_NAME\%/$FILE_NAME/gis;
	my $template = $CONFIG->{create_procedure_template};
	$template =~ s/\%PROCEDURE_NAME\%/$FILE_NAME/gis;
	$template =~ s/\%BODY\%/$text/gis;
	open(OUT, '>', $file_name) or die "Could not open file '$file_name' $!";
	print OUT $template;
	close OUT;
}

sub create_script
{
	my $text = shift;

	#my $file_name = $OUTPUT_FOLDER.'/'.$CONFIG->{file_name}.'.sql';
	my $file_name = $OUTPUT_FOLDER.'/'.$FILE_NAME.'.sql';
	#$file_name =~ s/\%PROCEDURE_NAME\%/$FILE_NAME/gis;
	open(OUT, '>', $file_name) or die "Could not open file '$file_name' $!";
	print OUT $text;
	close OUT;
}

# custom functions
sub not_exist_to_left_join
{
	my $text = shift;
	
	if ($text !~ /\bnot\s+exists\b\s*\(/gis)
	{
        return $text;
    }
	
	my @not_exists_array = ();
	while ($text =~ /(\bnot\s+exists\b\s*)\((.*)/gis)
	{
		my $expression = $2;
		my $formed_str = '';
		my $start_prent_count = 1;
		my $end_prent_count = 0;
		
		foreach my $char (split('', $expression))
		{
			if($char eq '(')
			{
				$start_prent_count += 1;
			}
			elsif($char eq ')')
			{
				$end_prent_count += 1;
			}
			if ($start_prent_count == $end_prent_count)
			{
				last;
			}
			$formed_str .= $char;
		}
		my $escaped_final_expression = "$formed_str";
		$formed_str =~ s/.*?\bfrom\b\s+(.*)\bwhere\b\s*(.*)/left outer join $1 on \n $2/gis;
		$escaped_final_expression = escape_str($escaped_final_expression);
		$escaped_final_expression =~ s/\*/\\*/gis;
		
		$text =~ s/\bnot\s+exists\b\s*\($escaped_final_expression\)\s*AND\b/$formed_str\n/gis;
		$text =~ s/\bnot\s+exists\b\s*\($escaped_final_expression\)\s*OR\b/$formed_str\n/gis;
		$text =~ s/\bnot\s+exists\b\s*\($escaped_final_expression\)/$formed_str\nWHERE /gis;
		push(@not_exists_array,split(/\band\b/,$formed_str));
	}
	my $where_condition = '';
	foreach my $condition (@not_exists_array)
	{
		if ($condition =~ /\=(.*)/gis)
		{
			my $col = $MR->trim($1);
            if ($where_condition ne '')
			{
                $where_condition .= 'and ';
            }
            $where_condition .= " $col is null\n";
        }
	}
	$text =~ s/(.*WHERE)(.*)/$1$where_condition\n$2/gis;
	
	my @format_params = $text =~ /\$\{(.*?)\}/gim;
	$text =~ s/\$\{.*?\}/{}/gis;
    #my $formats_str = join(',', @format_params);
	return ($text,join(',', @format_params));
}

sub custom_cast
{
	my $text = shift;

	if ($text !~ /\:\:/)
	{
        return $text;
    }
	
	my $custom_cast = $CONFIG->{custom_cast};
	
	foreach	my $k (keys %$custom_cast)
	{
		while ($text =~ /\:\:\s*$k/)
		{
			my $expression = '';
			my $precision = '';
			if ($custom_cast->{$k}->{Precision})
			{
                $text =~ /(.*)\:\:\s*$k(\(.*?\))/i;
				$expression = $1;
				$precision = $2;
            }
            else
			{
				$text =~ /(.*)\:\:\s*$k/i;
				$expression = $1;
			}
			
			my $final_expression = '';
			my $reversed_original_expression = reverse $expression;
			
			my $dynamic_reversed_expression = $MR->trim("$reversed_original_expression");
			
			if ($dynamic_reversed_expression =~ /^(\w+)/)
			{
				$final_expression = reverse $1;
			}
			elsif($dynamic_reversed_expression =~ /^(\).*\(\s*\w+)/)
			{
				$dynamic_reversed_expression = $1;
				my $start_prent_count = 0;
				my $end_prent_count = 0;
				
				my $formed_str = '';
				my $iter = 0;
				
				foreach my $char (split('', $dynamic_reversed_expression))
				{
					$iter += 1;
					if($char eq '(')
					{
						$start_prent_count += 1;
					}
					if($char eq ')')
					{
						$end_prent_count += 1;
					}
					$formed_str .= $char;
					if ($start_prent_count == $end_prent_count)
					{
						my $remain_str = substr($dynamic_reversed_expression,$iter);
						my $word;
						if($remain_str =~ /(^\s*\w+)/)
						{
							$word = $1;
						}
						
						if ($word and $word ne '')
						{
                            if (lc(reverse $word) ne 'select')
							{
                                $formed_str .= $word;
                            }
                        }
						last;
					}
				}
				$final_expression = reverse $formed_str;
			}
		
			my $escaped_final_expression = "$final_expression";
			$escaped_final_expression =~ s/\*/\\*/gis;
			#$final_expression = "CAST($final_expression AS Decimal$precision)";
			$escaped_final_expression = escape_str($escaped_final_expression."\\s*::\\s*$k$precision");
			
			my $value = $custom_cast->{$k}->{Value};
			$value =~ s/\%EXPRESSION\%/$final_expression/gis;
			$value =~ s/\%PRECISION\%/$precision/gis;
			$text =~ s/$escaped_final_expression/$value/gis;
		}
	}
	return $text;
}

sub escape_str
{
	my $text = shift;
	
	$text =~ s/\{/\\{/gis;
	$text =~ s/\}/\\}/gis;
	$text =~ s/\(/\\(/gis;
	$text =~ s/\)/\\)/gis;
	$text =~ s/\]/\\]/gis;
	$text =~ s/\[/\\[/gis;
	$text =~ s/\?/\\?/gis;
	$text =~ s/\$/\\\$/gis;
	
	$text =~ s/\^/\\^/gis;
	$text =~ s/\+/\\+/gis;

	return $text;
}

sub toolkit_split_to_columns
{
	my $text = shift;
		
	my $ret_value = '';
	my $toolkit_expression;
	my $toolkit_table_alias;
	my $toolkit_column;
	my $toolkit_column_count;
	my $toolkit_column_delimiter;
	my $where_condition;
	my $table_name;
	my $table_alias;
	my @toolkit_splitted_columns = ();
	my $before_toolkit_text;
	
	$text =~ /(SELECT\s*.*?)\bS1/gis;
	$before_toolkit_text = $1;
	$before_toolkit_text = "$before_toolkit_text";
	$before_toolkit_text =~ s/(.*)\,.*/$1/gis;

	$text = "$text";
	my $has_row_id = 0;
	my $next_id;
	#my $select_with_format_condition;
	my $final_select;
	
	if ($before_toolkit_text =~ /SELECT\s+ROWID\b/gis)
	{
        $has_row_id = 1;
		#$before_toolkit_text =~ s/^ROWID\b\s*\,?\s*//gis;
		$before_toolkit_text =~ s/\bROWID\b/row_number() over (order by 1) as ROWID/gis;
    }
	if ($before_toolkit_text =~ /\bNEXT\b\s+VALUE\s+FOR\b\s*.*? AS\s+(\w+)/gis)
	{
        $next_id = $1;
		$before_toolkit_text =~ s/\bNEXT\b\s+VALUE\s+FOR\b\s*.*? AS\s+\w+\s*\,?//gis;
    }
	my @match_params = $before_toolkit_text =~ /\'?\$\{.*?\}\'?\s+AS\s+\w+/gim;
	@match_params = (@match_params ,$before_toolkit_text =~ /\w+\(\'?\$\{.*?\}\'?.*?\)\s+AS\s+\w+/gim);
	$before_toolkit_text =~ s/\$//gim;
	
	my @match_column_alias = $before_toolkit_text =~ /\bAS\s+(\w+)/gim;
					
	#$before_toolkit_text =~ s/\'?\$\{.*?\}\'?\s+AS\s+\w+\s*\,?//gim;
	#$before_toolkit_text =~ s/\w+\(\'?\$\{.*?\}\'?.*?\)\s+AS\s+\w+\s*\,?//gim;
	foreach my $item (@match_column_alias)
	{
		$final_select .= "$item, ";
	}
	
#	foreach my $item (@match_params)
#	{
#		if ($select_with_format_condition)
#		{
#            $select_with_format_condition .= ', ';
#        }
#		$item =~ /\{(.*?)\}.*\bAS\s*(\w+)/gis;
#        my $l = $1;
#        my $r = $2;
#		$select_with_format_condition .= "$l = $r";
#	}
    
	if ($text =~ /\bFROM\b\s*(\w+)\s+AS\s+(\w+).*?\bTABLE\b\s*\(/gis)
	{
       	$table_name = $1;
		$table_alias = $2;
    }
    else
	{
		$text =~ /\bFROM\b\s*(\w+)\s+(\w+).*?\bTABLE\b\s*\(/gis;
		$table_name = $1;
		$table_alias = $2;
	}
	
	$table_name =~ s/^\s+|\s+$//g;
	$table_alias =~ s/^\s+|\s+$//g;
	$text = "$text";
	$text =~ /\bTABLE\s*\(.*?\((.*?)\)\)+(.*?)(\bWHERE\s*.*)/gis;
	$toolkit_expression = $1;
	$toolkit_table_alias = $2;
	$where_condition = $3;
	$toolkit_expression =~ s/^\s+|\s+$//g;
	$toolkit_table_alias =~ s/^\s+|\s+$//g;
	$where_condition =~ s/^\s+|\s+$//g;
	$text = "$text";
	
	my @toolkit_expression_items = split(',', $toolkit_expression);
	$toolkit_column_count = $toolkit_expression_items[2];
	$toolkit_column_count =~ s/^\s+|\s+$//g;
	$toolkit_column_delimiter = $toolkit_expression_items[1];
	$toolkit_column_delimiter =~ s/^\s+|\s+$//g;
	$toolkit_column_delimiter =~ s/^["']+//g;
	$toolkit_column_delimiter =~ s/["']*$//g;
	$toolkit_expression_items[0] =~ /$table_alias\.(.*)/;
	$toolkit_column = $1;
	$toolkit_column =~ s/^\s+|\s+$//g;

	$text =~ /\bS1(.*?)\bFROM\b/gis;
	@toolkit_splitted_columns = $1 =~ /\s+\bAS\b\s+(\w+)/gim;
	
	my $select_with_where = $CONFIG->{custom_commands}->{SPLIT_TO_COLUMNS_SELECT_WITH_WHERE};
	$select_with_where =~ s/\%TABLE\%/$table_name/gis;
	$select_with_where =~ s/\%WHERE\%/$where_condition/gis;
	
	$ret_value = $select_with_where;
	#$ret_value = "sql_statement = \"\"\"SELECT * FROM $table_name $where_condition\"\"\"\n";
	#$ret_value .= "$table_name = spark.sql(sql_statement)\n\n";
	$ret_value .= "$table_name = $table_name";
	
	
	my $iter = 1;
	my $concat_toolikit_columns;
	for my $item (@toolkit_splitted_columns)
	{
		my $select_with_format = $CONFIG->{custom_commands}->{SPLIT_TO_COLUMNS_with_column};
		$select_with_format =~ s/\%COLUMN\%/$item/gis;
		$select_with_format =~ s/\%TABLE\%/$table_name/gis;
		$select_with_format =~ s/\%TOOLKIT_COLUMN\%/$toolkit_column/gis;
		$select_with_format =~ s/\%DELIMITER\%/$toolkit_column_delimiter/gis;
		$select_with_format =~ s/\%INDEX\%/$iter/gis;
		
		$ret_value .= $select_with_format;
		#$ret_value .= ". \\\nwithColumn('$item',split($table_name"."['$toolkit_column'], '[$toolkit_column_delimiter]').getItem($iter))";
		if($concat_toolikit_columns)
		{
			$concat_toolikit_columns .= ',';
		}
		$concat_toolikit_columns .= "NVL($item,'') as $item";
		
		$iter += 1;
	}
	
	$ret_value .= "\n\n";
	if ($next_id)
	{
		my $next_value_for = $CONFIG->{custom_commands}->{SPLIT_TO_COLUMNS_NEXT_VALUE_FOR};
		$next_value_for =~ s/\%TABLE\%/$table_name/gis;
		$next_value_for =~ s/\%NEXT_ID\%/$next_id/gis;
		$ret_value .= $next_value_for;
        #$ret_value .= "$table_name = SEQGEN($table_name, '$next_id')\n";
        #$ret_value .= "$table_name.createOrReplaceTempView('$table_name')\n\n";
    }
    $before_toolkit_text =~ s/\n//gis;
	
	my $select_with_format = $CONFIG->{custom_commands}->{SPLIT_TO_COLUMNS_select_with_format};
	$select_with_format =~ s/\%SELECT\%/$before_toolkit_text/gis;
	$select_with_format =~ s/\%TABLE\%/$table_name/gis;
	
	my $final_select_tempalte = $CONFIG->{custom_commands}->{SPLIT_TO_COLUMNS_final_select};
	$final_select_tempalte =~ s/\%SELECT\%/$final_select/gis;
	$final_select_tempalte =~ s/\%TOOLKIT_COLUMNS\%/$concat_toolikit_columns/gis;
	$final_select_tempalte =~ s/\%TABLE\%/$table_name/gis;
	
	#$ret_value .= "sql_statement = \"\"\"$before_toolkit_text * FROM $table_name\"\"\".format(IDP_AUDIT_ID=AUDIT_ID, IDP_DATA_DATE=idp_data_date_var)\n";
	#$ret_value .= "$table_name = spark.sql(sql_statement)\n";
	#$ret_value .= "$table_name.createOrReplaceTempView('$table_name')\n\n";
	#
	#$ret_value .= "sql_statement = \"\"\"$final_select $concat_toolikit_columns FROM $table_name\"\"\"\n";
	#$ret_value .= "$table_name = spark.sql(sql_statement)\n";
	#$ret_value .= "$table_name.createOrReplaceTempView('$table_name')\n\n";
	$ret_value .= $select_with_format.$final_select_tempalte;
	return ($ret_value,$table_name);
}

sub mark_separators
{
	my $sql = shift; #scalar content of file

	$sql =~ s/END\s*GO\s*$/${DELIM}\nPROC_FINISH/gis;
	$sql =~ s/END\s*$/${DELIM}\nPROC_FINISH/gis;
	$sql =~ s/with\s+RECOMPILE//gis; #so it does not mess up our WITH logic

	my $i = 0;
	my $len = length($sql);
	my @chars = split(//, $sql);
	my @final_chars = ();
	my $quote_escape_str = '__BBQUOTE_ESC@PE__';
	my $hit_cnt = 0;
	my $inside_1line_comment = 0; #single line comment flag
	my $inside_mline_comment = 0; #multi line comment flag
	my @prior_keywords = ('WHERE', 'GROUP BY', 'ORDER BY', 'IF', 'BEGIN', 'UPDATE', 'INSERT', 'MERGE', 'DECLARE', 'VALUES', 'UNION', 'WITH');
	#my @curr_keywords_cond = ('CASE'); #capture conditionals.  We need to mark ELSE and END as COND_ELSE and COND_END
	my $prior_keyword = '';
	#my $prior_keyword_cond = '';
	my $level = 0;
	my $case_level = 0;
	my $case_hit_cnt = 0;
	my $with_used = 0;
	my @WITH_KW = qw(INSERT DELETE UPDATE);
	foreach my $c (@chars)
	{
		$inside_1line_comment = 1 if (!$inside_mline_comment && !$inside_1line_comment && substr($sql, $i, 2) eq '--');
		$inside_mline_comment = 1 if (!$inside_mline_comment && !$inside_1line_comment && substr($sql, $i, 2) eq '/*');
		$inside_mline_comment = 0 if ($inside_mline_comment && !$inside_1line_comment && substr($sql, $i, 2) eq '*/');
		$inside_1line_comment = 0 if (!$inside_mline_comment && $inside_1line_comment && substr($sql, $i, 1) eq "\n");
		$level++ if (!$inside_mline_comment && !$inside_1line_comment && substr($sql, $i, 1) eq "(");
		$level-- if (!$inside_mline_comment && !$inside_1line_comment && substr($sql, $i, 1) eq ")");

		#$MR->log_msg("MARK_SEP: NL at $i") if $c eq "\n";
		#$MR->log_msg("MARK_SEP: CR at $i") if $c eq "\r";

		#grab look for keywords
		if (!$inside_mline_comment && !$inside_1line_comment && $level == 0)
		{
			foreach my $kw (@prior_keywords)
			{
				my $tmp_str = substr($sql, $i-1, length($kw)+2 ); #grab 1 char before and after
				#$MR->log_msg("MARK_SEP: pos $i, KW $kw, STR: '$tmp_str'");
				if ($tmp_str =~ /\W$kw\W/gis)
				{
					#$MR->log_msg("MARK_SEP: KW_MATCH!");
					$prior_keyword = $kw;
				}
			}
		}

		my $tmp_with = substr($sql, $i-1, 6); #grab 1 char before and after
		if ($tmp_with =~ /\WWITH\W/gis && !$inside_mline_comment && !$inside_1line_comment && $level == 0 && !$with_used)
		{
			$with_used = 1;
			$MR->log_msg("WITH Found at level $level. Offset $i");
		}

		if ($with_used)
		{
			foreach my $wkw (@WITH_KW)
			{
				my $tmp_with_kw = substr($sql, $i-1, length($wkw)+2); #grab 1 char before and after
				#$MR->log_msg("WITH_KW: '$wkw', '$tmp_with_kw'");
				if ($tmp_with_kw =~ /\W$wkw\W/gis && !$inside_mline_comment && !$inside_1line_comment && $level == 0 && $with_used)
				{
					#$MR->log_msg("WITH KEYWORD Found at level $level. Offset $i. KW: $wkw");
					$with_used = 0;
					push(@final_chars, $WITH_PREFIX);
					last;
				}
			}
		}

		my $tmp_select = substr($sql, $i-1, 8); #grab 1 char before and after
		if ($tmp_select =~ /\WSELECT\W/gis)
		{
			$hit_cnt++;
			$MR->log_msg("MARK_SEP: SELECT. LEVEL: $level, 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $hit_cnt. Prior: $prior_keyword. '$tmp_select'");
			if ( !$inside_mline_comment && !$inside_1line_comment && $level == 0 && $prior_keyword ne 'INSERT' && $prior_keyword ne 'UNION' && $prior_keyword ne 'WITH')
			{
				$MR->log_msg("MARK_SEP: Adding delimiter!");
				push(@final_chars, "\n$DELIM\n");
			}
		}
		my $tmp_case = substr($sql, $i-1, 6); #grab 1 char before and after
		if ($tmp_case =~ /\WCASE\W/gis && !$inside_mline_comment && !$inside_1line_comment)
		{
			$case_level++;
			$case_hit_cnt++;
			$MR->log_msg("MARK_SEP: CASE. LEVEL: $case_level, 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $case_hit_cnt.");
		}


		#Handle ELSE keyword, which could be inside a case statement or at inside a conditional
		my $tmp_else = substr($sql, $i-1, 6); #grab 1 char before and after
		if ($tmp_else =~ /\WELSE\W/gis && !$inside_mline_comment && !$inside_1line_comment)
		{
			if ($case_level > 0)
			{
				$MR->log_msg("MARK_SEP: CASE ELSE. LEVEL: $case_level, 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $case_hit_cnt.");
				#$case_level--; #we are closing a case statement
			}
			else
			{
				push(@final_chars, "\n${DELIM}\nCOND_"); #make it COND_ELSE
				$MR->log_msg("MARK_SEP: CONDITIONAL ELSE. 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $case_hit_cnt.");
			}
		}


		#Handle END keyword, which could be inside a case statement or at the end of a conditional
		my $tmp_end = substr($sql, $i-1, 5); #grab 1 char before and after
		if ($tmp_end =~ /\WEND\W/gis && !$inside_mline_comment && !$inside_1line_comment)
		{
			if ($case_level > 0)
			{
				$MR->log_msg("MARK_SEP: CASE END. LEVEL: $case_level, 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $case_hit_cnt.");
				$case_level--; #we are closing a case statement
			}
			else
			{
				# push(@final_chars, "\n${DELIM}\nCOND_"); #make it COND_END
				$MR->log_msg("MARK_SEP: CONDITIONAL END. 1L: $inside_1line_comment, ML: $inside_mline_comment, at pos $i, hit $case_hit_cnt.");
			}
		}
		
		my $tmp_if = substr($sql, $i-1, 4); #grab 1 char before and after to check for IF
		if ($tmp_if =~ /\WIF\W/is && !$inside_mline_comment && !$inside_1line_comment && $level == 0)
		{
			push(@final_chars, "\n$DELIM\n");
		}

		push(@final_chars, $c) unless $c eq '';
		$i++;
	}
	$sql = join('',@final_chars);
	return $sql;
}

sub select_into_fragment
{
	my $cont = shift;
	$MR->log_msg("update_to_merge_fragment:\n$cont");
	$cont = $MR->trim($cont);

	my $table_name = undef;
	my $variable_str = undef;
	if ($cont =~ /\bSELECT\s+.*?\s*\bINTO\b\s*.*?\s*\bFROM\b/is)
	{
		$cont =~ s/(\bSELECT\s+.*?\s*)\bINTO\b\s*(.*?)\s*\bFROM\b/CREATE TABLE $2 AS \n$1\n FROM/is;
    }

	$cont = $SQL_PARSER->convert_sql_fragment($cont);
	my $wrap_templaet = $CONFIG->{commands}->{WRAP};
	$wrap_templaet =~ s/\%SQL\%/$cont/gis;
	#$ret .= $wrap_templaet;
	#$cont = code_indent("spark.sql(f\"\"\"$cont\"\"\")\n");
	return $wrap_templaet;
}

sub python_variable_assignment
{
	my $cont = shift;
	$MR->log_msg("update_to_merge_fragment:\n$cont");
	$cont = $ETL_PARSER->convert_sql_fragment($cont);
	my @vars = $cont =~ /(\bV_\w+)\s*\=/gis;
	my @values = split /\bV_\w+\s*\=/,$cont;

	my $index = 0;
	my $ret = '';
	foreach my $val (@values)
	{
		if (!$val || $val eq '')
		{
            next;
        }
        
		$val = $MR->trim($val);
		$val =~ s/\,$//;
		$val = $MR->trim($val);
		$ret .= "$vars[$index] = $val\n";
		$index += 1;
	}
	$ret .= "\n";
	#$cont = code_indent($cont."\n");
	return $ret;
}

sub update_to_merge_fragment
{
	my $cont = shift;
	$MR->log_msg("update_to_merge_fragment:\n$cont");
	my $ret = $SQL_PARSER->convert_sql_fragment($MR->trim($cont));
	#$ret =~ s/\@(\w+)/{$VARIABLE_PREFIX$1}/gis;
	$ret = $SQL_PARSER->convert_update_to_merge($ret);

	my $wrap_templaet = $CONFIG->{commands}->{WRAP};
	$wrap_templaet =~ s/\%SQL\%/$ret/gis;
	#$ret .= $wrap_templaet;
	#$cont = code_indent("spark.sql(f\"\"\"$cont\"\"\")\n");
	return $wrap_templaet;
}

sub source_block
{
	my $node = shift;

	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n";

	$MR->log_msg("source node: " . Dumper($node));
	
	my $script = '';
	if($node->{SQL_COMMAND})
	{
		$script = $SQL_PARSER->preprocess_add_delimiters($node->{SQL_COMMAND});
		#$MR->log_error("source cont: " . $script);
		#$script = mark_separators($node->{SQL_STATEMENT});

		#$node->{SQL_STATEMENT} =~ s/\bIF OBJECT_ID\b/;\nIF OBJECT_ID/g;
		$script =~ s/\/\*.*?\*\///gs;
		$script =~ s/\/\*\*.*?\*\*\///gs;
		$script =~ s/\;WITH\b/\;\nWITH/gs;
		$script =~ s/\;\s*\;/;/gs;
		
		$script =~ s/\bCOUNT\(\*\)/COUNT( * )/gm;
		   
		#$script =~ s/\@(\w+)/:::$1_$LOCAL_VARIABLE_ENUMIRATOR/g;
		#if($script =~ /\;\s*SELECT.*?\;/gis)
		#{
		#	$script =~ s/\;\s*SELECT.*?\;/;/gis;
		#}
		#elsif($script =~ /\;\s*SELECT.*/gis)
		#{
		#	$script =~ s/\;\s*SELECT.*/;/gis;
		#}
		#elsif($script =~ /\;\s*CALL.*\;/gis)
		#{
		#	$script =~ s/\;\s*CALL.*\;/;/gis;
		#}

		if($node->{ID_MAPPING})
		{
			my @mapping_ids = split /\;/, $node->{ID_MAPPING};
			foreach my $m_id (@mapping_ids)
			{
				foreach my $var (keys %{$PKG_INFO->{PACKAGE_VARIABLE_DETAILS}})
				{
					if($m_id eq $PKG_INFO->{PACKAGE_VARIABLE_DETAILS}->{$var}->{ID})
					{
						$script =~ s/\=\s*\?/={V_$var}/;
						last;
					}
				}
			}
	
		}
		$script = change_var_and_params_for_databricks($script);
		$script =~ s/\@\[User\:\:(\w+)\]/{$1}/g;
		$script =~ s/\[(\w+)\]/$1/g;

		#$COMPONENT_LAST_SELECT = $script;
	}
	elsif($node->{TABLE_NAME})
	{
		my @cols = $MR->get_sorted_column_list($node);
		my $concat_cols = '';
		foreach my $col (@cols)
		{
			if ($concat_cols ne '')
			{
                $concat_cols .= ",\n";
            }

            $concat_cols .= $col;
		}
		$node->{TABLE_NAME} =~ s/\[//g;
		$node->{TABLE_NAME} =~ s/\]//g;
		$script = "SELECT\n$concat_cols\nFROM $node->{TABLE_NAME}";
	}
	$node->{SQL} = $script;
	$MR->log_msg("source cont: " . $script);

	#$node->{COLUMNS}->{Test}->{COLUMN_ORDER} = 1;
	#return $SQL_PARSER->generate_SOURCE($node);
	my $node_name = $node->{NAME};
	$node_name = replace_invalid_characters($node_name);
	
	my $wrap_templaet = $CONFIG->{commands}->{SET_WRAP};
	$wrap_templaet =~ s/\%SQL\%/$script/gis;
	$wrap_templaet =~ s/\%VARIABLE\%/$node_name/gis;

	my $create_view_templaet = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
	$create_view_templaet =~ s/\%DF\%/$node_name/gis;
	$ret .= "\n$wrap_templaet\n$create_view_templaet";
	return code_indent($ret);
}

sub target_block
{
	my $node = shift;

	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n";

	$MR->log_msg("target node: " . Dumper($node));
	if($node->{SQL_COMMAND}->{content})
	{
		my $script = $SQL_PARSER->preprocess_add_delimiters($node->{SQL_COMMAND}->{content});
		$script = mark_separators($node->{SQL_STATEMENT});
		
		#$node->{SQL_STATEMENT} =~ s/\bIF OBJECT_ID\b/;\nIF OBJECT_ID/g;
		$script =~ s/\/\*.*?\*\///gs;
		$script =~ s/\/\*\*.*?\*\*\///gs;
		$script =~ s/\;WITH\b/\;\nWITH/gs;
		$script =~ s/\;\s*\;/;/gs;
		
		my $ret_value = change_var_and_params_for_databricks($node->{SQL_COMMAND}->{content});
		return $ret_value;
	}
	elsif($node->{TABLE_NAME})
	{
		my @src = $WRITER->get_sorted_source_nodes($node->{NAME});
		my $source_name = $src[0];
		$source_name = replace_invalid_characters($source_name);

		$node->{TABLE_NAME} =~ s/\[//g;
		$node->{TABLE_NAME} =~ s/\]//g;
		my $cols = '';
		foreach my $c (keys %{$node->{COLUMNS}})
		{
			if ($cols ne '')
			{
                $cols .= ",\n";
            }
            $cols .= $c;
		}
		if ($MR->trim($cols) eq '')
		{
            $cols = '*';
        }
        
		my $sql = "INSERT INTO $node->{TABLE_NAME}\n SELECT\n$cols\nFROM $source_name";
		my $wrap_templaet = $CONFIG->{commands}->{WRAP};
		$wrap_templaet =~ s/\%SQL\%/$sql/gis;
		$ret .= "\n$wrap_templaet";
		return code_indent($ret);
	}
}

sub aggregator_block
{
	my $node = shift;
	
	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n";
	
	$MR->debug_msg("aggregator_block: Sources: " . $MR->UnicodeDumper($PKG_INFO->{TARGET_SOURCE_REGISTER}->{$node->{NAME}}));
	$MR->debug_msg("aggregator_block for node $node->{NAME}: " . $MR->UnicodeDumper($node));

	my @src = $WRITER->get_sorted_source_nodes($node->{NAME});

	#get sort specs
	my @cols = $MR->get_sorted_column_list($node);
	my @out_cols = ();
	$MR->debug_msg("aggregator_block: Sources: " . $MR->UnicodeDumper(\@cols));
	# # make sure all columns are being propogated
	# @out_cols = ("$node->{TARGET_NODE_LIST}.*") if ($self->{PROPAGATE_ALL_COLUMNS} == 1 && $node->{COLUMNS} > 0);

	my @groupby = ();
	my %aggr_keys = ();
	map {$aggr_keys{$_} = 1} split(/,/, $node->{AGGR_KEYS}) if $node->{AGGR_KEYS}; #datastage convention
	my $expressions_embedded = $node->{AGGR_KEYS}?1:0; #for datastage, expressions are already embedded
	$MR->debug_msg("aggregator_block: expressions_embedded: $expressions_embedded. Keys: " . Dumper(\%aggr_keys));

	my %group_by_expr = ();
	if ($node->{AGGR_KEYS}) #not infa, prob datastage
	{
		my $src = $node->{INPUT_NODE_LIST_BY_NAME}->[0] if $node->{INPUT_NODE_LIST_BY_NAME};
		$src .= '.' if $src;
		foreach my $c (split(/,/, $node->{AGGR_KEYS}))
		{
			$group_by_expr{"$src$c"} = 1;
		}
	}
	$MR->debug_msg("aggregator_block: group by expressions: " . Dumper(\%group_by_expr) . "\nColumns: " . Dumper(@cols));

	#check if nesting is required.  This is done for targets like databricks, where forward column aliasing is not supported as of now (Aug 2022)
	my $overall_nesting_required_flag = 0;
	if ($CONFIG->{use_nested_select_on_every_calc_field} && $node->{CALC_FIELD_DETECTED})
	{
		foreach my $c (@cols)
		{
			my $need_nesting_flag = $WRITER>calc_field_needs_nesting($c, $node);
			$overall_nesting_required_flag = 1 if $need_nesting_flag;
		}
	}
	$MR->debug_msg("Aggregator: overall_nesting_required_flag for $node->{NAME}: $overall_nesting_required_flag");
	# when nesting is required, do not do aggregations in line, but just record them and the group by cols.  Later, add them to the final statement
	my @overall_aggregated_cols = ();
	my @overall_key_cols = ();

	my $default_function = $CONFIG->{default_aggregator_function_call} || "MIN";

	foreach my $c (@cols)
	{
		#next if $node->{COLUMNS}->{$c}->{COLUMN_HIDDEN_FLAG};
		my $hidden_col = $node->{COLUMNS}->{$c}->{COLUMN_HIDDEN_FLAG}?1:0;
		my $expr = $node->{COLUMNS}->{$c}->{EXPRESSION};
		$expr = $WRITER->double_quote_identifier_if_required($expr) if $expr eq $c; #if expressio is a column, enclose in quotes if needed

		if ($ETL_PARSER)
		{
			$MR->debug_msg("Parsing expression $expr");
			$expr = $ETL_PARSER->add_END_after_ELSE({EXPR => $expr}) if ($expr =~ /IF\b.*\bTHEN/gis && $WRITER->{AGGREGATOR_IF_TO_CASE_EXPRESSION} == 1);
			$expr = $ETL_PARSER->convert_sql_fragment($expr) unless ($node->{DO_NOT_PARSE} == 1);
			$MR->debug_msg("After parsing: $expr");
		}

		$expr = $WRITER->get_qualified_source_field($node->{NAME}, $c) || $WRITER->double_quote_identifier_if_required($c) if $expr eq '';
		$MR->debug_msg("Inside generate_AGGREGATOR  Columns expr: \n $expr" );

		if ($expr ne '')
		{
			$expr = $WRITER->adjust_token_fields($expr,$node->{NAME}) if $CONFIG->{transformer_vars_use_cte_flag};
			#$expr = $WRITER->get_qualified_source_field($node->{NAME}, $c) || $c;
			my $aggr_func = $node->{COLUMNS}->{$c}->{AGGREGATE_FUNCTION} || $default_function;

			if ($expressions_embedded && ! ($expr =~ /\(/) && !$group_by_expr{$expr})
			{
				$expr = "MIN($expr)"; #most likely was a datastage dedup originally
			}

			$expr .= " as " . $WRITER->double_quote_identifier_if_required($c);
		}
		#$MR->debug_msg("Inside generate_AGGREGATOR after Columns expr: \n $expr" );

		my $group_by_col = 0;

		$expr = $ETL_PARSER->convert_sql_fragment($node->{COLUMNS}->{$c}->{EXPRESSION}) . " as $c" if ($node->{SKIP_AGGREGATOR_EXPRESSION_CONVERSION} == 1 && defined $node->{COLUMNS}->{$c}->{EXPRESSION});

		if (!$overall_nesting_required_flag && $hidden_col) #suppress columns that are hidden. was only working for nested scenarios
		{
			#do nothing
		}
		else #old logic
		{
			push(@out_cols, $expr)
		}

		if ($node->{COLUMNS}->{$c}->{AGGREGATE_FLAG} eq 'Y')
		{
			if ($overall_nesting_required_flag)
			{
				push(@overall_key_cols, $c) unless $hidden_col;
			}
			else
			{
				push(@groupby, $c) unless $hidden_col;
			}
		}
	} # end of column iteration

	if ($#groupby < 0 && $node->{AGGR_KEYS}) #not infa, prob datastage
	{
		my $src = $node->{INPUT_NODE_LIST_BY_NAME}->[0] if $node->{INPUT_NODE_LIST_BY_NAME};
		$src .= '.' if $src;
		foreach my $c (split(/,/, $node->{AGGR_KEYS}))
		{
			push(@groupby, "$src$c");
		}
	}

	foreach (@src)
	{
		$_ = replace_invalid_characters($_);
	}

	my $from_clause = $node->{DEFAULT_FROM_CLAUSE} || $WRITER->get_FROM_clause({NODE => $node}) || join("\nLEFT JOIN ", $WRITER->add_rowid_into_from_clause(@src));
	if ($WRITER->adjust_select_clause(\@out_cols, @src)) #if changes were made, the last element is the row id. apply MIN function
	{
		$out_cols[-1] = "$default_function($out_cols[-1])";
		$out_cols[-1] .= " as $CONFIG->{rowid_column_name}" if $CONFIG->{rowid_column_name};
	}

	my $filter = $node->{PARAMETERS}->{OUTPUT_FILTER};
	if ( ! $filter )
	{
		$filter = $WRITER->get_not_null_value_from_node_meta($node->{NAME}, 'OUTPUT_LINK_SPECIFIC_FILTER');
	}
	if (ref($filter) eq 'ARRAY')
	{
		$filter = join(' AND ', @$filter);
	}
	if ($MR->trim($filter) ne '')
	{
		$filter = $SQL_PARSER->convert_sql_fragment($filter);
		$filter = "\nWHERE " . $filter;
	}

	my $sql = '';
	if ($CONFIG->{use_nested_select_on_every_calc_field} && $node->{CALC_FIELD_DETECTED})
	{
		$sql = $WRITER->nest_every_calc_field_in_SELECT({
			NODE => $node,
			COLUMN_ARRAY => \@out_cols,
			FROM_CLAUSE => $from_clause
			})
	}
	else
	{
		$sql = "SELECT\n" . join(",\n", @out_cols) . "\nFROM\n" . $from_clause;
	}

	$sql .= $filter;

	if ($overall_nesting_required_flag) #add the key fields, aggregated fields, and GROUP BY clause around the generated statement
	{
		$sql = "SELECT\n" . join(",\n", @overall_key_cols, @overall_aggregated_cols) . "\nFROM (\n$sql\n)\nGROUP BY\n" . join(",\n", @overall_key_cols);
	}
	else
	{
		$sql .= "\nGROUP BY\n" . join(",\n",
				map { $WRITER->get_qualified_source_field($node->{NAME}, $_) || $WRITER->double_quote_identifier_if_required($_) } @groupby
			) if $#groupby >= 0;
	}

	$sql = "SELECT\n" . join(",\n", @out_cols) . "\nFROM\n" . $from_clause if ($node->{SKIP_GROUPBY_CLAUSE} == 1);

	my $node_name = $node->{NAME};
	$node_name = replace_invalid_characters($node_name);
	
	my $wrap_templaet = $CONFIG->{commands}->{SET_WRAP};
	$wrap_templaet =~ s/\%SQL\%/$sql/gis;
	$wrap_templaet =~ s/\%VARIABLE\%/$node_name/gis;
	my $create_view_templaet = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
	$create_view_templaet =~ s/\%DF\%/$node_name/gis;
	$ret .= "\n$wrap_templaet\n$create_view_templaet";
	return code_indent($ret);
}

sub expression_block
{
	my $node = shift;

	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n";
	
	$MR->debug_msg("expression_block: Sources: " . $MR->UnicodeDumper($PKG_INFO->{TARGET_SOURCE_REGISTER}->{$node->{NAME}}));
	$MR->debug_msg("expression_block for node $node->{NAME}: " . $MR->UnicodeDumper($node));	

	my @src = $WRITER->get_sorted_source_nodes($node->{NAME});
	$MR->debug_msg("replicate_block: Sources: " . $MR->UnicodeDumper(\@src));
	
	my $src_obj = $WRITER->get_node_pointer_from_meta($src[0]);

	
	#get sort specs
	my @cols = $MR->get_sorted_column_list($node);
	
	#get sort specs from source
	my @source_cols = $MR->get_sorted_column_list($src_obj);
	
	my %col_names = ();
	map {$col_names{$_} = 1} @cols;
	my $sql = '';
	my $columns_for_child = {};

	foreach my $c (@source_cols)
	{
		if (!$col_names{$c})
		{
			$node->{COLUMNS}->{$c} = $src_obj->{COLUMNS}->{$c};
			$node->{COLUMNS}->{$c}->{EXPRESSION} = $c;
        }
	}
	@cols = $MR->get_sorted_column_list($node);

	foreach my $c (@cols)
	{
		if ($sql ne '')
		{
			$sql .= ",\n";
        }
		$node->{COLUMNS}->{$c}->{EXPRESSION} =~ s/\[(\w+)\]/$1/g;
		$node->{COLUMNS}->{$c}->{EXPRESSION}=~ s/\bISNULL\s*\((.*)?\)\s*\?\s*(.*?)\s*\:\s*(\w+)/IF(ISNULL($1), $2, $3)/gis;
		$sql .= "$node->{COLUMNS}->{$c}->{EXPRESSION} AS $node->{COLUMNS}->{$c}->{COLUMN_NAME}";
	}

	$src_obj->{NAME} = replace_invalid_characters($src_obj->{NAME});

	$sql = "SELECT $sql\nFROM $src_obj->{NAME}";
	$sql = $SQL_PARSER->convert_sql_fragment($sql);
	$sql = change_var_and_params_for_databricks($sql);
	
	my $node_name = $node->{NAME};
	$node_name = replace_invalid_characters($node_name);
	
	my $wrap_templaet = $CONFIG->{commands}->{SET_WRAP};
	$wrap_templaet =~ s/\%SQL\%/$sql/gis;
	$wrap_templaet =~ s/\%VARIABLE\%/$node_name/gis;
	my $create_view_templaet = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
	$create_view_templaet =~ s/\%DF\%/$node_name/gis;
	$ret .= "\n$wrap_templaet\n$create_view_templaet";

	$ret =~ s/==/=/g;

	return code_indent($ret);
}

sub replicate_block
{
	my $node = shift;

	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n";
	
	$MR->debug_msg("replicate_block: Sources: " . $MR->UnicodeDumper($PKG_INFO->{TARGET_SOURCE_REGISTER}->{$node->{NAME}}));
	$MR->debug_msg("replicate_block for node $node->{NAME}: " . $MR->UnicodeDumper($node));

	my @src = $WRITER->get_sorted_source_nodes($node->{NAME});
	$MR->debug_msg("replicate_block: Sources: " . $MR->UnicodeDumper(\@src));

	my $src_obj = $WRITER->get_node_pointer_from_meta($src[0]);
	my $source_name = $src_obj->{NAME};
	$source_name = replace_invalid_characters($source_name);
	
	$MR->debug_msg("replicate_block: Source obj: " . $MR->UnicodeDumper($src_obj));
	$node->{COLUMNS} = $src_obj->{COLUMNS};
	
	my $node_name = $node->{NAME};
	$node_name = replace_invalid_characters($node_name);

	my $wrap_templaet = $CONFIG->{commands}->{SET_WRAP};
	$wrap_templaet =~ s/\%SQL\%/SELECT * FROM $source_name/gis;
	$wrap_templaet =~ s/\%VARIABLE\%/$node_name/gis;
	my $create_view_templaet = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
	$create_view_templaet =~ s/\%DF\%/$node_name/gis;
	$ret .= "\n$wrap_templaet\n$create_view_templaet";
	return code_indent($ret);
}

sub lookup_block
{
	my $node = shift;

	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n";
	
	$MR->debug_msg("lookup_block: Sources: " . $MR->UnicodeDumper($PKG_INFO->{TARGET_SOURCE_REGISTER}->{$node->{NAME}}));
	
	$MR->debug_msg("lookup_block for node $node->{NAME}: " . $MR->UnicodeDumper($node));	

	my @src = $WRITER->get_sorted_source_nodes($node->{NAME});
	$MR->debug_msg("lookup_block: Sources: " . $MR->UnicodeDumper(\@src));
	
	my $src_obj = $WRITER->get_node_pointer_from_meta($src[0]);
	$MR->debug_msg("lookup_block: Source obj: " . $MR->UnicodeDumper($src_obj));
	
	#get sort specs
	my @cols = $MR->get_sorted_column_list($node);
	
	#get sort specs from source
	my @source_cols = $MR->get_sorted_column_list($src_obj);

	
	my %col_names = ();
	map {$col_names{$_} = 1} @cols;
	my $sql = '';
	my $source_obj_name = $src_obj->{NAME};
	$source_obj_name = replace_invalid_characters($source_obj_name);

	foreach	my $src_col (@source_cols)
	{
		if ($sql ne '')
		{
			$sql .= ",\n";
        }
		$sql .= "$source_obj_name.$src_col AS $src_col";
		$node->{COLUMNS}->{$src_col} = $src_obj->{COLUMNS}->{$src_col};
	}

	my $where_is_mach_cond = '';
	my $where_no_mach_cond = '';
	foreach	my $col (@cols)
	{

		# if $col has a characters that are not part of \w (so \W),
		# then it needs to be enclosed in backticks
		if ($col =~ /\W/)
		{
			$col = "`$col`";
		}

		if ($sql ne '')
		{
			$sql .= ",\n";
        }
		$sql .= "$node->{LOOKUP_ALIAS}.$col AS $col";
		
		if ($where_no_mach_cond ne '')
		{
            $where_no_mach_cond .= " AND\n";
			$where_is_mach_cond .= " AND\n";
        }
        $where_no_mach_cond .= "$node->{LOOKUP_ALIAS}.$col IS NULL";
		$where_is_mach_cond .= "$node->{LOOKUP_ALIAS}.$col IS NOT NULL";
	}
	$sql =  "SELECT $sql\nFROM $source_obj_name\nINNER JOIN ($node->{SQL}) AS $node->{LOOKUP_ALIAS}\n ON $node->{JOIN_CONDITION}";
	$sql =~ s/\%SOURCE_TABLE\%/$source_obj_name/gis;

	$sql = $SQL_PARSER->convert_sql_fragment($sql);
	$sql = change_var_and_params_for_databricks($sql);
	
	foreach my $target_node_name(keys %{$LINK_NAME->{$node->{NAME}}})
	{
		my $count = scalar($LINK_NAME->{$node->{NAME}}->{$target_node_name});
		foreach my $tgn (@{$LINK_NAME->{$node->{NAME}}->{$target_node_name}})
		{
			if ($tgn =~ /no\s+match/i)
			{
				my $orig_val = (keys %{$PKG_INFO->{TARGET_SOURCE_REGISTER}->{$target_node_name}})[0];
				$orig_val =~ s/(.*\\)(.*)/$1_NO_$2/;
				if ($count == 1)
				{
					delete $PKG_INFO->{TARGET_SOURCE_REGISTER}->{$target_node_name};
                }
                
				$PKG_INFO->{TARGET_SOURCE_REGISTER}->{$target_node_name}->{$orig_val} = 1;
	
				my $new_node_name = $MR->deep_copy($orig_val);
				$new_node_name = replace_invalid_characters($new_node_name);
	
				my $wrap_templaet = $CONFIG->{commands}->{SET_WRAP};

				if ($where_no_mach_cond ne '')
				{
					$wrap_templaet =~ s/\%SQL\%/$sql\nWHERE $where_no_mach_cond/gis;
				}
				else
				{
					$wrap_templaet =~ s/\%SQL\%/$sql/gis;
				}               
				$wrap_templaet =~ s/\%VARIABLE\%/$new_node_name/gis;
				my $create_view_templaet = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
				$create_view_templaet =~ s/\%DF\%/$new_node_name/gis;
				$ret .= "\n$wrap_templaet\n$create_view_templaet\n";
				my $coped_node = $MR->deep_copy($node);
				$coped_node->{NAME} = $orig_val;
				push(@{$WRITER->{JOB}->{NODES}},$coped_node);
			}
		}			
	}


	my $node_name = $node->{NAME};
	$node_name = replace_invalid_characters($node_name);

	my $wrap_templaet = $CONFIG->{commands}->{SET_WRAP};
	#$wrap_templaet =~ s/\%SQL\%/$sql/gis;
	
	if ($where_is_mach_cond ne '')
	{
		$wrap_templaet =~ s/\%SQL\%/$sql\nWHERE $where_is_mach_cond/gis;
	}
	else
	{
		$wrap_templaet =~ s/\%SQL\%/$sql/gis;
		$ret .= "\n#LOOKUP does not contain an output column, so no WHERE statement is generated.\n";
	}
	$wrap_templaet =~ s/\%VARIABLE\%/$node_name/gis;
	my $create_view_templaet = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
	$create_view_templaet =~ s/\%DF\%/$node_name/gis;
	$ret .= "\n$wrap_templaet\n$create_view_templaet";
	return code_indent($ret);
}

sub conditionalsplit_block
{
	my $node = shift;

	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n";
	
	
	$MR->debug_msg("conditional_block Link names: " . $MR->UnicodeDumper($LINK_NAME->{$node->{NAME}}));
	$MR->debug_msg("conditional_block for node $node->{NAME}: " . $MR->UnicodeDumper($node));	

	my @src = $WRITER->get_sorted_source_nodes($node->{NAME});
	$MR->debug_msg("conditional_block: Sources: " . $MR->UnicodeDumper(\@src));
	
	my $src_obj = $WRITER->get_node_pointer_from_meta($src[0]);
	$MR->debug_msg("conditional_block: Source obj: " . $MR->UnicodeDumper($src_obj));
	
	#get sort specs from source
	my @source_cols = $MR->get_sorted_column_list($src_obj);
	
	my $sql = '';
	my $source_obj_name = $src_obj->{NAME};
	$source_obj_name = replace_invalid_characters($source_obj_name);

	foreach	my $src_col (@source_cols)
	{
		if ($sql ne '')
		{
			$sql .= ",\n";
        }
		$sql .= "$source_obj_name.$src_col AS $src_col";
	}

	my $where_cond = '';

	$sql =  "SELECT $sql\nFROM $source_obj_name\n";

	$sql = $SQL_PARSER->convert_sql_fragment($sql);
	$sql = change_var_and_params_for_databricks($sql);	
	foreach my $target_node_name(keys %{$LINK_NAME->{$node->{NAME}}})
	{
		my $tgn = @{$LINK_NAME->{$node->{NAME}}->{$target_node_name}}[0];
		my $tgn1 = "_$tgn".'_';
		my $orig_val = (keys %{$PKG_INFO->{TARGET_SOURCE_REGISTER}->{$target_node_name}})[0];
		$orig_val =~ s/(.*\\)(.*)/$1$tgn1$2/;
		delete $PKG_INFO->{TARGET_SOURCE_REGISTER}->{$target_node_name};
		$PKG_INFO->{TARGET_SOURCE_REGISTER}->{$target_node_name}->{$orig_val} = 1;

		my $new_node_name = $MR->deep_copy($orig_val);
		$new_node_name = replace_invalid_characters($new_node_name);

		my $wrap_templaet = $CONFIG->{commands}->{SET_WRAP};
		if ($tgn eq $node->{CONDITION}->{LINK_NAME})
		{
			$where_cond = "\nWHERE $node->{CONDITION}->{VALUE}";
        }
		else
		{
			$where_cond = "\nWHERE ($node->{CONDITION}->{VALUE}) == 0";
		}

		$where_cond = $SQL_PARSER->convert_sql_fragment($where_cond);
		$where_cond = change_var_and_params_for_databricks($where_cond);
		$wrap_templaet =~ s/\%SQL\%/$sql$where_cond/gis;
		$wrap_templaet =~ s/\%VARIABLE\%/$new_node_name/gis;
		my $create_view_templaet = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
		$create_view_templaet =~ s/\%DF\%/$new_node_name/gis;
		$ret .= "\n$wrap_templaet\n$create_view_templaet\n";
		my $coped_node = $MR->deep_copy($node);
		$coped_node->{NAME} = $orig_val;
		push(@{$WRITER->{JOB}->{NODES}},$coped_node);
	}
	$node->{COLUMNS} = $src_obj->{COLUMNS};

	# replace all \=\= with \=
	$ret =~ s/==/=/g;

	return code_indent($ret);
}

sub dummy_block
{
	my $node = shift;

	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n#We do not support conversion of this component.\n";
	
	$MR->debug_msg("dummy_block: Sources: " . $MR->UnicodeDumper($PKG_INFO->{TARGET_SOURCE_REGISTER}->{$node->{NAME}}));
	
	$MR->debug_msg("dummy_block for node $node->{NAME}: " . $MR->UnicodeDumper($node));	

	my @src = $WRITER->get_sorted_source_nodes($node->{NAME});
	$MR->debug_msg("dummy_block: Sources: " . $MR->UnicodeDumper(\@src));
	
	my $src_obj = $WRITER->get_node_pointer_from_meta($src[0]);
	$MR->debug_msg("dummy_block: Source obj: " . $MR->UnicodeDumper($src_obj));
	my $source_name = $src_obj->{NAME};

	$source_name = replace_invalid_characters($source_name);
	#get sort specs from source
	my @source_cols = $MR->get_sorted_column_list($src_obj);
	
	my $sql = '';
	my $source_obj_name = $src_obj->{NAME};
	$source_obj_name = replace_invalid_characters($source_obj_name);

	foreach	my $src_col (@source_cols)
	{
		if ($sql ne '')
		{
			$sql .= ",\n";
        }
		$sql .= "$source_obj_name.$src_col AS $src_col";
	}

	$node->{COLUMNS} = $src_obj->{COLUMNS};

	my $node_name = $node->{NAME};
	$node_name = replace_invalid_characters($node_name);
	
	my $wrap_templaet = $CONFIG->{commands}->{SET_WRAP};
	$wrap_templaet =~ s/\%SQL\%/SELECT * FROM $source_name/gis;
	$wrap_templaet =~ s/\%VARIABLE\%/$node_name/gis;
	my $create_view_templaet = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
	$create_view_templaet =~ s/\%DF\%/$node_name/gis;
	$ret .= "\n$wrap_templaet\n$create_view_templaet";
	return code_indent($ret);
}

sub union_block
{
	my $node = shift;

	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n";
	
	$MR->debug_msg("union_block: Sources: " . $MR->UnicodeDumper($PKG_INFO->{TARGET_SOURCE_REGISTER}->{$node->{NAME}}));
	$MR->debug_msg("union_block for node $node->{NAME}: " . $MR->UnicodeDumper($node));	

	my @src = $WRITER->get_sorted_source_nodes($node->{NAME});

	$MR->debug_msg("union_block: Sources: " . $MR->UnicodeDumper(\@src));
	my $sql = '';
	#get sort specs
	my @cols = $MR->get_sorted_column_list($node);
	my $cols_str = join(",\n", @cols);
	foreach my $s (@src)
	{
		if ($sql ne '')
		{
            $sql .= "\nUNION ALL\n";
        }
		$s = replace_invalid_characters($s);
		$cols_str =~ s/(\w+)/$s.$1/gs;
		$sql .= "SELECT\n$cols_str\nFROM\n$s";
		$cols_str = join(",\n", @cols);
	}
	
	$sql = $SQL_PARSER->convert_sql_fragment($sql);
	$sql = change_var_and_params_for_databricks($sql);
	
	my $node_name = $node->{NAME};
	$node_name = replace_invalid_characters($node_name);

	my $wrap_templaet = $CONFIG->{commands}->{SET_WRAP};
	$wrap_templaet =~ s/\%SQL\%/$sql/gis;
	$wrap_templaet =~ s/\%VARIABLE\%/$node_name/gis;
	my $create_view_templaet = $CONFIG->{commands}->{CREATE_TEMP_VIEW};
	$create_view_templaet =~ s/\%DF\%/$node_name/gis;
	$ret .= "\n$wrap_templaet\n$create_view_templaet";
	return code_indent($ret);
}


sub excelsource_block
{
	my $node = shift;

	my $pre_node_line = get_pre_node_line($node);
	my $ret = $pre_node_line . "\n";
	$ret .= "$COMMENT_PEFIX component name". $node->{LOCAL_NAME} . "\n";

	$MR->log_msg("excel source node: " . Dumper($node));
	
	my $read_excel_templaet = $CONFIG->{commands}->{READ_EXCEL_COMMAND};
	$node->{CONNECTIONSTRING} =~ /\bData\s+Source\=\s*(.*?)\;/is;
	my $excel_path = $1;
	$read_excel_templaet =~ s/\%PATH\%/$excel_path/gs;
	$read_excel_templaet =~ s/\%SHEET\%/$node->{SHEET_NAME}/gs;
	my $node_name = $node->{NAME};
	$node_name = replace_invalid_characters($node_name);
	$read_excel_templaet =~ s/\%NODE_NAME\%/$node_name/gs;
	$ret .= "\n$read_excel_templaet";
	return code_indent($ret);
}

sub change_var_and_params_for_databricks
{
	my $content = shift;

	foreach my $item (keys %$PKG_INFO)
	{
		if($PKG_INFO->{PACKAGE_VARIABLE_DETAILS}->{$item}->{PARAM_TYPE} eq 'VARIABLE')
		{
			my $new_item = ' ${var.'.$item.'}';
			$content =~ s/(?<![AS|SELECT|DISTINCT])\s+\b$item\b/$new_item/gis;
		}

		if($PKG_INFO->{PACKAGE_VARIABLE_DETAILS}->{$item}->{PARAM_TYPE} eq 'PARAMETER')
		{
			my $new_item = ' ${'.$item.'}';
			$content =~ s/\b$item\b/$new_item/gis;
		}		
	}
	return $content;
}

sub replace_invalid_characters
{
	my $str = shift;
	#return $str if $CONFIG->{keep_node_names_as_is};
	$str = $MR->trim($str);
	$str =~ s/\s+/_/g;
	$str =~ s/=/_/g;
	$str =~ s/'/_/g;
	$str =~ s/-/_/g;
	$str =~ s/,/_/g;
	$str =~ s/\./_/g;
	$str =~ s/\!/_/g;
	$str =~ s/\&/_/g;
	$str =~ s/\//_/g;
	$str =~ s/\?/_/g;
	$str =~ s/\\/_/g;
	$str =~ s/\</_/g;
	$str =~ s/\>/_/g;
	$str =~ s/\(//g;
	$str =~ s/\)//g;
	$str =~ s/"//g;
	$str =~ s/\*//g;
	$str =~ s/\+//g;
	$str =~ s/_+/_/g;

	return $str;
}
