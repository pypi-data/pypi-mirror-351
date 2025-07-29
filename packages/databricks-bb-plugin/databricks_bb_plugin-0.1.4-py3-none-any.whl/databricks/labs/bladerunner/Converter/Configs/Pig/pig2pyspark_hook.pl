use strict;
use Data::Dumper;
use Common::MiscRoutines;
use DWSLanguage;

no strict 'refs';


my $MR = new Common::MiscRoutines(MESSAGE_PREFIX => 'PIG_HOOKS');
my $LAN = new DWSLanguage();
my %CFG = (); #entries to be initialized
my $CFG_POINTER = undef;
my $CONVERTER = undef;
my %PRESCAN = ();
my $WIDGET_STRING = "";

my $sql_parser;

sub capture_comments
{
	my $cont = shift;
	my @part_comments = $cont =~ /(\/\*.*?\*\/|--.*?\n)/gs;

	# sort comments by length, largest to smallest
	@part_comments = sort { length($b) <=> length($a) } @part_comments;

	return @part_comments;
}

sub init_pig_hooks #register this function in the config file
{
	my $param = shift;

	%CFG = %{$param->{CONFIG}};
	$CFG_POINTER = $param->{CONFIG}; #give the ability to modify config incrementally
	$CONVERTER = $param->{CONVERTER};

	$MR->log_msg("INIT_HOOKS Called. config:\n");

	#Reinitilize vars for when -d option is used:

	$ENV{CONFIG} = $param->{CONFIG};
	$sql_parser = new DBCatalog::SQLParser(CONFIG => $ENV{CONFIG}, DEBUG_FLAG => 0);
}

sub preprocess_pig
{
	my $cont_ar = shift;

	my $cont = join("\n", @{$cont_ar});

	$cont =~ s/\$([0-9]+)/__DOLLAR__$1/g;

	$MR->log_msg("PREPROCESS Called. content:\n$cont\n");

	#capture comments
	my @part_comments = capture_comments($cont);
	$PRESCAN{comments} = \@part_comments;

	#replace comments with placeholders __COMMENT_1__ and so on
	my $i = 1;
	foreach my $comment (@part_comments)
	{
		my $current_comment = "__COMMENT_" . $i . "__";
		$cont =~ s/\Q$comment/$current_comment/gs;
		$i++;
	}

	$MR->log_msg("PREPROCESS Called. content after comments replacement:\n$cont\n");

	my @ret = split("\n", $cont);
	my $out = generic_substitution(\@ret, "prescan_subst");

	# capture all \$\w+ from $out and store in array
	my @vars = ();
	@vars = $out =~ /\$\w+|__DOLLAR__[0-9]+/g;
	# make values unique
	my %seen = ();
	@vars = grep { !$seen{$_}++ } @vars;

	# foreach @vars need to use $CFG{variable_declaration_template} and replace %VARNAME% with the variable name
	$WIDGET_STRING = "";
	foreach my $var (@vars)
	{
		$WIDGET_STRING .= $CFG{variable_declaration_template};

		my $var_no_dollar = $var;
		$var_no_dollar =~ s/\$//g;
		$var_no_dollar =~ s/__DOLLAR__//g;
		# if just a number add prefix num_
		$var_no_dollar = "num_" . $var_no_dollar if $var_no_dollar =~ /^[0-9]+$/;

		$WIDGET_STRING =~ s/%VARNAME%/$var_no_dollar/g;
	}

	@ret = split("\n", $out);

	return @ret;
}

sub pig_finalize_code
{
	my $ar = shift;
	my $code = join("\n", @{$ar});

	# for each comment, wrap in triple quotes
	my $i = 1;
	foreach my $comment (@{$PRESCAN{comments}})
	{
		my $current_comment = "__COMMENT_" . $i . "__";

		# remove /* */ from $comment and single line comment as well
		$comment =~ s/^\s*\/\*//gs;
		$comment =~ s/\*\/\s*$//gs;
		$comment =~ s/^\s*--//gs;

		$code =~ s/$current_comment/\"\"\"$comment\"\"\"\n/gs;
		$i++;
	}

	delete $PRESCAN{comments};

	my @ret = split("\n", $code);
	$code = generic_substitution(\@ret, "finalize_subst");

	# add variable declarations to the beginning of the code
	$code = $WIDGET_STRING . "\n" . $code if $WIDGET_STRING;

	if ($CFG{variable_declaration_comment} ne '' && $WIDGET_STRING ne '')
	{
		$code = $CFG{variable_declaration_comment} . "\n" . $code;
	}

	# add config header
	if ($CFG{header} ne '')
	{
		$code = $CFG{header} . "\n" . $code;
	}

	@{$ar} = split("\n", $code);

	return $ar;
}

sub from_to_substitution
{
	my $array_string = shift;
	my $expression = shift;

	my @token_substitutions = @{$array_string};
	foreach my $token_sub (@token_substitutions)
	{
		my ($from, $to) = ($token_sub->{from}, $token_sub->{to});
		if ($expression =~ /$from/is)
		{
			while ($expression =~ s/$from/$to/is)
			{
				my @tokk = ($1,$2,$3,$4,$5,$6,$7,$8,$9);
				my $idxx = 1;
				foreach my $too (@tokk)
				{
					$expression =~ s/\$$idxx/$too/g;
					$idxx++;
				}
			}
		}
	}

	return $expression;
}

sub convert_decode
{
	my $expr = shift;
	$MR->log_msg("STARTING DECODE CONVERSION $expr");

	#print("convert_decode subroutine was reached\n");

	$expr =~ /DECODE\s*\((.*)\)$/is;
	my $param = "($1)";
	$MR->log_msg("DECODE PARAMS: $param");

	my @args = $MR->get_direct_function_args($param);

	#Check if even or odd because first argument not required

	$MR->log_msg("DECODE ARGS " . Dumper(\@args));
	my $idx = 0;

	my $ret = '';
	while ($idx < $#args - 1)
	{
		if(!$idx)
		{
			$ret .= "WHEN $args[0] \= $args[$idx+1] THEN $args[$idx+2]";
		}
		else
		{
			$ret .= " WHEN $args[0] \= $args[$idx+1] THEN $args[$idx+2]";
		}
		$idx = $idx + 2;
	}

	#if number of elements is even then add optional default arg
	my $odd_check = scalar(@args) % 2 ;
	if(!$odd_check)
	{
		$ret .= "ELSE $args[$#args]";

	}

	$MR->log_msg("FINAL CONVERSION DECODE ARGS:$#args & $odd_check:\n $ret");
	return $ret;
}

sub generic_substitution
{
	my $ar = shift;
	my $cfg_subst = shift;

	my $cont_str = join("\n", @{$ar});

	$MR->log_msg("$cfg_subst Called. content: $cont_str");

	#block substitution for variable declarations from config
	if (exists $CFG{$cfg_subst})
	{
		$cont_str = from_to_substitution($CFG{$cfg_subst}, $cont_str);
	}

	return $cont_str;
}

sub load_using
{
	my $ar = shift;
	return generic_substitution($ar, "load_using_subst");
}

sub store_into
{
	my $ar = shift;
	return generic_substitution($ar, "store_into_subst");
}

sub foreach_generate
{
	my $ar = shift;

	my $lines = join("\n", @{$ar});

	# call convert_decode
	$lines =~ s/DECODE\s*\((.*?)\)/convert_decode($1)/ge;

	@{$ar} = split("\n", $lines);

	return generic_substitution($ar, "foreach_generate_subst");
}

sub union
{
	my $ar = shift;
	return generic_substitution($ar, "union_subst");
}

sub union_onschema
{
	my $ar = shift;
	return generic_substitution($ar, "union_onschema_subst");
}

sub group
{
	my $ar = shift;
	return generic_substitution($ar, "group_subst");
}

sub distinct
{
	my $ar = shift;
	return generic_substitution($ar, "distinct_subst");
}

sub cross
{
	my $ar = shift;
	return generic_substitution($ar, "cross_subst");
}

sub join
{
	my $ar = shift;
	my $out = generic_substitution($ar, "simple_join_pre_subst");

	my $df_name = "";
	$df_name = $1 if $out =~ /(\w+)\s*=\s*JOIN/i;

	my @join_names = ();

	# take out any __COMMENT_[0-9]+__ from the string and store them in an array
	my @comments = ();
	while ($out =~ /(__COMMENT_[0-9]+__)/)
	{
		my $comment = $1;
		push @comments, $comment;
		$out =~ s/$comment//;
	}

	my $out_copy = $out;

	while ($out_copy =~ /(\w+)\s+BY\s+\(\s*([\w\:\,\s]+)\s*\)\s*LEFT\s*OUTER/i)
	{
		my $name = $1;
		my $col = $2;

		my $insert_col = $col;
		my $insert_name = $name;
		$insert_col =~ s/\w+\:\://g;
		$insert_name =~ s/\w+\:\://g;
		push @join_names, [$insert_name, $insert_col, "left_outer"];
		$out_copy =~ s/$name\s+BY\s+\(\s*$col\s*\)\s*LEFT\s*OUTER//i;
	}

	while ($out_copy =~ /(\w+)\s+BY\s+\(\s*([\w\:\,\s]+)\s*\)/i)
	{
		my $name = $1;
		my $col = $2;

		my $insert_col = $col;
		my $insert_name = $name;
		$insert_col =~ s/\w+\:\://g;
		$insert_name =~ s/\w+\:\://g;
		push @join_names, [$insert_name, $insert_col, ""];
		$out_copy =~ s/$name\s+BY\s+\(\s*$col\s*\)//;
	}

	while ($out_copy =~ /(\w+)\s+BY\s+([\w\:\,\s]+)\s+BY\b/i)
	{
		my $name = $1;
		my $col = $2;

		my $insert_col = $col;
		my $insert_name = $name;
		$insert_col =~ s/\w+\:\://g;
		$insert_name =~ s/\w+\:\://g;
		push @join_names, [$insert_name, $insert_col, ""];
		$out_copy =~ s/$name\s+BY\s+$col//;
	}

	while ($out_copy =~ /(\w+)\s+BY\s+([\w\:\,\s]+)\s+$/i)
	{
		my $name = $1;
		my $col = $2;

		my $insert_col = $col;
		my $insert_name = $name;
		$insert_col =~ s/\w+\:\://g;
		$insert_name =~ s/\w+\:\://g;

		if ($insert_name = "JOIN")
		{
			$insert_name = $insert_col;
		}

		push @join_names, [$insert_name, $insert_col, ""];
		$out_copy =~ s/$name\s+BY\s+$col//;
	}

	my $count = 0;
	my $ret = $df_name . " = ";
	foreach my $join (@join_names)
	{
		if ($count eq 1)
		{
			$count++;
			next;
		}

		my $name = $join->[0];
		my $col = $join->[1];
		$col =~ s/,/\",\"/g;

		# trim leading and trailing whitespace from $col
		$col =~ s/^\s+|\s+$//g;

		my $type = $join->[2];

		if ($count eq 0)
		{
			$ret .= $name . ".join($join_names[$count + 1][0], ";
		}
		else
		{
			$ret .= ".join($name, ";
		}

		if ($type eq "left_outer")
		{
			$ret .= "[\"$col\"], how='left_outer')";
		}
		else
		{
			$ret .= "on=[\"$col\"])";
		}

		$count++;
	}

	# add comments back to front of $ret
	foreach my $comment (@comments)
	{
		$ret = "\n" . $comment . "\n" . $ret;
	}

	return $ret;
}

sub filter
{
	my $ar = shift;

	my $out = generic_substitution($ar, "filter_pre_subst");

	# for $out, go through each word and check if it is a columns,
	# like if its not a number or a string, then it is a column. Then wrap with col()

	# if ($out =~ /__FILTER_S__([\s\S]+)?__FILTER_E__/)
	# {
	# 	my $sub = $1;
	#
	# 	my @words = split(/\s+/, $sub);
	# 	my $i = 0;
	# 	foreach my $word (@words)
	# 	{
	# 		if ($word !~ /^[0-9]+$/ && $word !~ /^['"].*['"]$/ && $word !~ /^[^a-zA-Z0-9]+$/
	# 			&& $word !~ /\bAND\b|\bOR\b|\bIS\b|\bNOT\b|\bNULL\b/i && !($word eq "") )
	# 		{
	# 			$words[$i] = "col('$word')";
	# 		}
	# 		$i++;
	# 	}
	#
	# 	$sub = join(" ", @words);
	#
	# 	$out =~ s/__FILTER_S__([\s\S]+)?__FILTER_E__/$sub/;
	# }

	@{$ar} = split("\n", $out);
	$out = generic_substitution($ar, "filter_post_subst");

	return $out;
}

sub pig_default_handler
{
	my $ar = shift;
	return generic_substitution($ar, "generic_subst");
}
