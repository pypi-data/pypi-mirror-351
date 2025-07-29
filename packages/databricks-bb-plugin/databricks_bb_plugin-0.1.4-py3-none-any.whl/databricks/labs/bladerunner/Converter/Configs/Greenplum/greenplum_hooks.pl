use strict;
use warnings FATAL => 'all';

use Data::Dumper;
use Common::MiscRoutines;
my $mr = new Common::MiscRoutines(DEBUG_FLAG => 1, MESSAGE_PREFIX => 'greenplum_hooks');

my @greenplum_subst;

sub init_hooks_greenplum_subst #register this function in the config file
{
	my $param = shift;
	@greenplum_subst = @{$param->{CONFIG}->{greenplum_hooks_subst}};
	print "init_hooks_greenplum_subst Called. config:\n" . Dumper(\@greenplum_subst);
}

sub greenplum_finalize_code
{
    my $ar = shift;
    my $options = shift;

    my $sql = join("\n", @{$ar});
    my $old_sql = $sql;

    $mr->log_msg("Applying preprocess_subst");
    foreach my $el (@greenplum_subst)
    {
        my ($from, $to) = ($el->{from}, $el->{to});
        $mr->log_msg("greenplum_hooks_subst: changing:\nFROM $from\nTO $to");
        while ($sql =~ s/$from/$to/is)
        {
            my @tok = ($1,$2,$3,$4,$5,$6,$7,$8,$9);
            my $idx = 1;
            foreach my $t (@tok)
            {
                $sql =~ s/\$$idx/$t/g;
                $idx++;
            }
        }
    }

    if (!($sql eq $old_sql))
    {
        my $count = 0;
        foreach (@{$ar})
        {
            if ($count eq 0)
            {
                $_ = $sql;
                $count++;
            }
            else
            {
                $_ = "";
            }
        }
        return
    }
}
