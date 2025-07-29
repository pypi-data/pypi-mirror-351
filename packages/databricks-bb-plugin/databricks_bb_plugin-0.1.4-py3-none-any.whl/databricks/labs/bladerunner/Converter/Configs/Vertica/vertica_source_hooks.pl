use strict;
use warnings;
use Globals;

sub vertica_prescan
{
	my $vertica_source_ref = shift;

	# Create a temp array using the passed array (ref), then empty out the passed array
	# We need to do this in order to maintain the REFERENCE to the passed array
	#my @temp_vertica_source = ();
	#foreach (@$vertica_source_ref)
	#{
	#	push(@temp_vertica_source, $_);
	#}
	#while (scalar(@$vertica_source_ref) >= 1) {shift(@$vertica_source_ref);} 

	my @new_hive_source = ();
	$Globals::ENV{PRESCAN} = {};
	# Allow for CHANGES in prescan with this tag
	#if ($Globals::ENV{CONFIG}->{prescan_subst})
	#{
	#	FRAG:
	#	foreach my $source_frag (@temp_vertica_source)
	#	{
	#		foreach my $gsub (@{ $Globals::ENV{CONFIG}->{prescan_subst} })
	#		{
	#
	#			# Remove the fragment if matched and  "__REMOVE__" specified in the "to"
	#			next FRAG if ($source_frag =~ /$gsub->{from}/is and $gsub->{to} eq '__REMOVE__');
	#
	#			# Attempt eval(s) to make the changes
	#			my $save_frag = $source_frag;
	#			my $eval_gsub = "my \$gsub_count = 0; 
	#			while (\$source_frag =~ s{$gsub->{from}}{$gsub->{to}}sgi) {
	#				die \"prescan_subst stuck in loop!!\" if \$gsub_count++ > 1000
	#			}";
	#			eval ($eval_gsub);
	#			my $ret = $@;
	#			if ($ret)
	#			{
	#				$MR->log_msg("Got stuck in loop; reverting to global change instead of \"while...\"");
	#				$source_frag = $save_frag;
	#				$eval_gsub = "my \$gsub_count = 0; 
	#				\$source_frag =~ s{$gsub->{from}}{$gsub->{to}}sgi;";
	#				eval ($eval_gsub);
	#				my $ret = $@;
	#
	#				if ($ret)
	#				{
	#					$MR->log_error("************ EVAL ERROR in global substitution: $ret ************");
	#					$MR->log_error("*** Failing eval code: $eval_gsub");
	#					$MR->log_error("*** Input to substitution (\$source_frag): $source_frag\n");
	#					exit -1;
	#				}
	#			}
	#		}
	#
	#		# Hide semi-colon inside a literal, so that these don't cause an incorrect fragment split. 
	#		# Original reason is code like this in Hive:
	#		#    collection items terminated by '\;'
	#		$source_frag =~ s{'(.*?;.*?)'}{"'<h_i_d_d_e_n>" . hide_value($1) . "</h_i_d_d_e_n>'"}seg;
	#
	#		push(@new_hive_source, $source_frag);
	#	}
	#}
	#else
	#{
	#	@new_hive_source = @temp_hive_source;
	#}

	#my @var_names = ();
	#my $text = join("\n" , @new_hive_source);
	#my @fragments = split("\;", $text);
	#
	## Create a pattern match from config attribs text_table_named_file_formats and text_table_class_name_file_formats
	#my $text_table_named_file_formats = '(textfile|jsonfile|json)';  # Default
	#if ($Globals::ENV{CONFIG}->{text_table_named_file_formats})
	#{
	#	$text_table_named_file_formats = '(' . join('|', @{$Globals::ENV{CONFIG}->{text_table_named_file_formats}}) . ')';
	#}
	#
	#my $text_table_class_name_file_formats = '(org.apache.hadoop.hive.serde2.JsonSerDe'      # Default
	#									   . '|org.apache.hadoop.hive.serde2.OpenCSVSerDe'
	#									   . '|org.apache.hadoop.hive.serde2.RegexSerDe'
	#									   . '|org.apache.hive.hcatalog.data.JsonSerDe)';
	#if ($Globals::ENV{CONFIG}->{text_table_class_name_file_formats})
	#{
	#	$text_table_class_name_file_formats = '(' . join('|', @{$Globals::ENV{CONFIG}->{text_table_class_name_file_formats}}) . ')';
	#}
	#$text_table_class_name_file_formats = 'inputformat\s+' . $text_table_class_name_file_formats;
	#
	#my $text_table_all_file_formats = "(" . $text_table_named_file_formats . "|" . $text_table_class_name_file_formats . ")";

	#my %locations;
	#my @locations_stored;
	#my @locations_stored_2;
	#my @locations_stored_3; #parquet
	#foreach my $frag (@fragments)
	#{
	#	# Unhide hidden values
	#	$frag =~ s{'<h_i_d_d_e_n>([0-9]+)</h_i_d_d_e_n>'}{'$hidden_values{$1}'}g;
	#
	#	$MR->log_msg("Looping through each $frag");
	#
	#	foreach my $suppress (@{$Globals::ENV{CONFIG}->{suppress_lines_containing}})
	#	{
	#		if ($frag !~ /$suppress/gm )
	#		{
	#			while($frag =~ /\bcreate\s+external\s+table\s.*/gis)
	#			{
	#				push(@{ $Globals::ENV{PRESCAN}->{CREATE_EXTERNAL_TABLE}->{ORIGINAL_BLOCK} }, $frag);
	#			}
	#			while($frag =~ /\$\{(.*?)\}/gis)
	#			{
	#				my $var = $1; 
	#				$var =~ s/hivevar\://gis;
	#				push(@var_names,$var);
	#			}
	#			while($frag =~ /\@(\w+)\@/gis)
	#			{
	#				push(@var_names,$1);
	#			}
	#			while($frag =~ /location\s*\'\s*([\w\/\\\:\.]+)\/(\w+)\s*\'/gis)
	#			{
	#				$locations{$1} = 1;
	#			}
	#			while($frag =~ /\bCREATE\s+EXTERNAL\s+TABLE\s+IF\s+NOT\s+EXISTS\s+[\w\@]+\.(\w+)+\s+stored\s+as\s+parquet\s+TBLPROPERTIES\s*\([\"\w\.\=]+\)\s+as\s+select\s*\*\s*(from\s+[\w\@]+\.\w+)/gis)
	#			{
	#				push(@locations_stored_3, {NAME => $1, STORAGE => $2});
	#				push(@var_names,"LOCATION_PATH");
	#			}
	#			while($frag =~ /\bCREATE\s+EXTERNAL\s+TABLE\s+[\w\@]+\.(\w+)+\s+stored\s+as\s+parquet\s+TBLPROPERTIES\s*\([\"\w\.\=]+\)\s+as\s+select\s*\*\s*(from\s+[\w\@]+\.\w+)/gis)
	#			{
	#				push(@locations_stored_3, {NAME => $1, STORAGE => $2});
	#				push(@var_names,"LOCATION_PATH");
	#			}
	#			while($frag =~ /\bCREATE\s+EXTERNAL\s+TABLE\s+IF\s+NOT\s+EXISTS\s+[\w\@]+\.(\w+)[\s\S]+STORED\s*AS\s*(\w+)/gis)
	#			{
	#				push(@locations_stored, {NAME => $1, STORAGE => $2});
	#				push(@var_names,"LOCATION_PATH");
	#			}
	#			while($frag =~ /\bCREATE\s+EXTERNAL\s+TABLE\s+[\w\@]+\.(\w+)[\s\S]+STORED\s*AS\s*(\w+)/gis)
	#			{
	#				push(@locations_stored, {NAME => $1, STORAGE => $2});
	#				push(@var_names,"LOCATION_PATH");
	#			}
	#			while($frag =~ /\bCREATE\s+EXTERNAL\s+TABLE\s+\`?[\w\@]+\`?\.\`?(\w+)\`?\s*AS\s*SELECT\s*/gis)
	#			{
	#				push(@locations_stored_2,$1);
	#				push(@var_names,"LOCATION_PATH");
	#			}
	#		}
	#		
	#	} 
	#	
	#	# if($frag =~ /CREATE\s*TABLE\s*IF\s*NOT\s*EXISTS\s*(.*?)\s*\(/gis || $frag =~ /create\s*table\s*(.*?)\s*\(/gis)
	#	if ($frag =~ m{(\bcreate\s.*?table\s+(?:IF\s+NOT\s+EXISTS\s+)?
	#										(?<table_name>[\${}\w.]+).*?(\(((?:(?>[^()]+)|(?3))*)\))) # Table name followed by balanced parens
	#									    (?<table_attribs>.*?\s+stored\s+as\s+$text_table_all_file_formats # Rest of stmt (must be text format)
	#										 .*)
	#				  }xis)
	#	{
	#		# NOTE: Next line causes perl -c to terminate early!!!
	#		prescan_create_table_as_text($+{table_name},$+{table_attribs});
	#	}
	#
	#	if ($frag =~ m{\bload\s+data\s+(local\s+)?inpath\s.*}si)
	#	{
	#		prescan_load_data($frag);
	#	}
	#
	#	if ($frag =~ m{\binsert\s+overwrite\s+table\s}i)
	#	{
	#		prescan_insert_overwrite_table($frag);
	#		
	#	}
	#}

#	$text = join(";", @fragments);
#
#
#	@var_names = uniq(@var_names);
#
#	$Globals::ENV{PRESCAN}->{CREATE_EXTERNAL_TABLE}->{loc_2} = \@locations_stored_2;
#	$Globals::ENV{PRESCAN}->{CREATE_EXTERNAL_TABLE}->{loc} = \@locations_stored;
#	$Globals::ENV{PRESCAN}->{CREATE_EXTERNAL_TABLE}->{loc_3} = \@locations_stored_3;
#	$Globals::ENV{PRESCAN}->{CREATE_EXTERNAL_TABLE}->{locations} = \%locations;
#
#	$Globals::ENV{GLOBALS}->{proc_arg_count} = 0;
#    $Globals::ENV{GLOBALS}->{declare_var_count} = 0;
#
#	foreach my $var_name(@var_names)
#	{
#		$Globals::ENV{PRESCAN}->{VARIABLES}->{$var_name}->{DATA_TYPE} = "TEXT";
#		$Globals::ENV{PRESCAN}->{VARIABLES}->{$var_name}->{NAME} = $var_name;
#
#		$Globals::ENV{GLOBALS}->{declare_var_count}++;
#	}
#
#	@new_hive_source = split(/\n/, $text);
#
#	# Re-populate the original array that was passed (by ref)
#	foreach (@new_hive_source)
#	{
#		push($hive_source_ref, $_);
#	}
#
#	$text =~ s/\bset\b.*?\;//gim;
#
#	#	collect widgets
#	my @widget_vars = $text =~ /\$\{hiveconf\:(.*?)\}/gim;
#	
#	my %hashed_widget_vars = map {$_ => 1} @widget_vars;
#	foreach my $v (keys %hashed_widget_vars)
#	{
#		$Globals::ENV{PRESCAN}->{WIDGETS}->{$v} = 1;
#	}
#	
##	collect temp table names
#	my @temp_tables = $text =~ /\bCREATE\s+TEMPORARY\s+TABLE\s+(\$\{hiveconf\:.*?\}\w*\.?\w*\.?\w*)\s*\(/gim;
#	@temp_tables = (@temp_tables, $text =~ /\bCREATE\s+TEMPORARY\s+TABLE\s+(\$\{hiveconf\:.*?\}\w*\.?\w*\.?\w*)\s*\bSTORED\s+AS\s+PARQUET\b/gim);
#	
#	#@temp_tables = sort {length($b) <=> length($a)} @temp_tables;
#	
#	my %hashed_temp_tables = map {$_ => 1} @temp_tables;
#	foreach my $v (keys %hashed_temp_tables)
#	{
#		$v =~ /.*\.(.*)/;
#		my $new_val = $1;
#		$v =~ s/\$/\\\$/;
#		$v =~ s/\{/\\{/;
#		$v =~ s/\}/\\}/;
#		$Globals::ENV{PRESCAN}->{TEMP_TABLES}->{$new_val} = $v;
#	}
	
	$MR->log_msg("End vertica prescan : " . Dumper($Globals::ENV{PRESCAN}));
}
