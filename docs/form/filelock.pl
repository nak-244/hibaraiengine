############################################
#
#        ̾  ����SUN-SYSTEM ��ϢCGI ��¾���½���CGI ver0.5
#        ��  �www.sun-co-ltd.com ����ε��(�����ͭ)
#        ��  ����2003/8/25  ���٤ι⤤��¾���� ����
#
#����å������(�����ॢ���Ȥ����die)��
#  $lfh = &filelock() or die 'Busy!';
#  $lfh = &filelock() or &disp_error("�����С�������Ǥ����ǽ��������ޤ���");
#
#����å������������
#  &fileunlock($lfh);
#
# �����ʤ�褦�˻Ȥ�!
# require "filelock.pl";
#
# ������å�����
# $lfh = &filelock("�ǥ��쥯�ȥ�̾", "�ե�����̾") or &disp_error('error');
#
# �����ɤ߹���Ȥ���������Ȥ�
# open FH, "<$lfh->{current}"; ��
#
# ��������ǡ����ե�����˽񤭹���(�����ե�����̾�ϡ�$lfh->{current}�Ǥ���
# open FH, ">$lfh->{current}";
#
# ������å��������(����ǡ����ե�����������ե�����̾�˥�͡��ह��)
# &fileunlock($lfh);     #<-- &fileunlock("$lfh");�Ȥ����ư���ʤ��Τ����
#
#############################

sub filelock {
	my %lfh;
	$lfh{dir}      = shift;
	$lfh{basename} = shift;
	$lfh{timeout}  = 60;
	$lfh{trytime}  = 10;
	$lfh{path}     = "$lfh{dir}/$lfh{basename}";

	for (my $i = 0; $i < $lfh{trytime}; $i++, sleep 1) {
		return \%lfh if (rename($lfh{path}, $lfh{current} = $lfh{path} . time));
	}
	opendir(LOCKDIR, $lfh{dir});
	my @filelist = readdir(LOCKDIR);
	closedir(LOCKDIR);
	foreach (@filelist) {
		if (/^$lfh{basename}(\d+)/) {
			return \%lfh if (time - $1 > $lfh{timeout} and rename($lfh{dir} . $_, $lfh{current} = $lfh{path} . time));
			last;
		}
	}
	undef;
}


#-----------------------------------------------------------------------
sub fileunlock {
	rename($_[0]->{current}, $_[0]->{path});
}

1;
