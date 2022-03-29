############################################
#
#        名  前：SUN-SYSTEM 関連CGI 排他制限処理CGI ver0.5
#        制  作：www.sun-co-ltd.com 松本竜太(著作権保有)
#        説  明：2003/8/25  精度の高い排他処理 制作
#
#■ロックする時(タイムアウトするとdie)は
#  $lfh = &filelock() or die 'Busy!';
#  $lfh = &filelock() or &disp_error("サーバーが混んでいる可能性があります。");
#
#■ロックを解除する時は
#  &fileunlock($lfh);
#
# こうなるように使う!
# require "filelock.pl";
#
# １．ロックする
# $lfh = &filelock("ディレクトリ名", "ファイル名") or &disp_error('error');
#
# ２．読み込むとか処理するとか
# open FH, "<$lfh->{current}"; 〜
#
# ３．一時データファイルに書き込む(処理ファイル名は、$lfh->{current}です。
# open FH, ">$lfh->{current}";
#
# ４．ロック解除する(一時データファイルを正規ファイル名にリネームする)
# &fileunlock($lfh);     #<-- &fileunlock("$lfh");とすると動かないので注意
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
