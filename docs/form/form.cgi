#!/usr/bin/perl --
########################################################################
#
#       名  前：sun-co-ltd.com/form_base ver1.07
#       制  作：sun-co-ltd.com 松本竜太（著作権保有）
#       注意点：このCGI自身の文字コードはEUC限定です。
#       内  容：2003/1/27 送信フォームのベースになるCGI
#             ：          mimew.pl, jcode.pl, filelock.pl が必要
#             ：          設定が細かくなる場合はoption.plも必要
#             ：2003/3/16 SJISテンプレートに対応
#             ：2003/8/2  変数名をハンガリー表記に変更、subscript説明記述
#             ：2004/2/5  itoh　ヘッダが出ない問題を修正、
#             ：          データ２のチェックおよびファイル名生成の抜けを補完
#             ：          数字の"0"が必須時にエラーになる問題を修正
#             ：2004/2/26 最新版が分岐してしまったので統合した
#             ：2004/3/1  メール本文のコードをsjis→jisに修正した(Mac対策)
#             ：2004/3/2  メールアドレス形式で＠以前に「/」を許容した
#
########################################################################
require 'setting.pl';

#######
# メイン
###
&setting_check;						# 設定内容を整合する
require './jcode.pl';

if($sREQUEST_METHOD eq "POST"){
	if($ENV{'CONTENT_TYPE'}  =~ m!^multipart/form-data!){
		&read_stdin;
	}else{
		&parse_form_data( *IN );
	}
}

if(!$IN{'form_step_check'} or $IN{'check0'}){
	&read_template("$TEMPLATE1", "1");		# 入力画面を表示
}elsif($IN{'form_step_check'} == 1 and $DISP_CHECK){
	&check_input_data;				# 項目のチェック
	&read_template("$TEMPLATE2", "1");		# 確認画面を表示

}elsif(($IN{'form_step_check'} == 2) or $IN{'check2'}){
	&check_input_data;				# 項目のチェック
	if($SAVE_DATA){ &save_data; }			# データ保存
	if($SAVE_DATA2){ &save_data2; }			# データ保存
	if($ADMIN_MAIL or $USER_MAIL){			# メール送信処理
		&make_mail_header;
		if($ADMIN_MAIL){ &send_email_admin; }
		if($USER_MAIL and $IN{'email'}){ &send_email_user; }
	}
	if($LOCATION_OK){
		print "Location: $LOCATION\n\n";	# サンクスページの表示
	}else{
		&read_template("$LOCATION", "1");
	}
}
exit;


#-----------------------------------------------------------------------
# call  : &setting_check;
# text  : CGIの主要な設定確認、call時の初期値設定
# return: none
#-----------------------------------------------------------------------
sub setting_check{
	my $error = ();

	#-- キャリアの判別
	my $agent = $ENV{'HTTP_USER_AGENT'};
	if($agent =~ /DoCoMo/i){ $nCAREER = 'i'; }
	elsif($agent =~ /J-PHONE/i){ $nCAREER = 'j'; }
	elsif($agent =~ /UP\.Browser/i){ $nCAREER = 'e'; }
	else{ $nCAREER = 'pc'; }

	#-- 機種別に設定ファイルをrequireする場合は記述。標準はsetting.pl。
	if($nCAREER eq 'i' and -e 'setting_i.pl'){
		require 'setting_i.pl';
	}elsif($nCAREER eq 'j' and -e 'setting_j.pl'){
		require 'setting_j.pl';
	}elsif($nCAREER eq 'e' and -e 'setting_e.pl'){
		require 'setting_e.pl';
	}else{
		unless( -e 'setting.pl'){ $error .= "設定ファイルが確認できません。正しく設置されていない可能性があります。"; }
		require 'setting.pl';
	}

	#-- 出力ヘッダーの確定
	if($nCAREER ne 'e'){ $nHEADER = "Content-type: text/html;\n\n"; }
	else{ $nHEADER = "Content-type:text/html;charset=Shift_JIS;\n\n"; }

	#-- ユーザー情報の取得
	$sHTTP_REFERER = $ENV{'HTTP_REFERER'};
	$sHTTP_REFERER =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	$sUSER_AGENT  = $ENV{'HTTP_USER_AGENT'};
	$sREMOTE_ADDR = $ENV{'REMOTE_ADDR'};
	$sREMOTE_HOST = $ENV{'REMOTE_HOST'};
	$sREQUEST_METHOD = $ENV{'REQUEST_METHOD'};
	if($GETHOSTBYADDR_OK and (!$sREMOTE_HOST or $sREMOTE_HOST eq $sREMOTE_ADDR)){ 
		$sREMOTE_HOST = gethostbyaddr(pack('C4',split(/\./,$sREMOTE_ADDR)),2); 
		if($sREMOTE_HOST eq ''){ $sREMOTE_HOST = $sREMOTE_ADDR; }
	}
	$IN{'http_referer'} = $sHTTP_REFERER;
	$IN{'user_agent'}   = $sUSER_AGENT;
	$IN{'remote_addr'}  = $sREMOTE_ADDR;
	$IN{'remote_host'}  = $sREMOTE_HOST;

	### 時間の取得
	($nSEC,$nMIN,$nHOUR,$nDAY,$nMON,$nYEAR,$nWDAY) = (localtime)[0,1,2,3,4,5,6];
	$nYEAR += 1900;
	$nMON += 1;
	if($nMON  < 10){ $nMON  = "0$nMON"; }
	if($nDAY  < 10){ $nDAY  = "0$nDAY"; }
	if($nHOUR < 10){ $nHOUR = "0$nHOUR"; }
	if($nMIN  < 10){ $nMIN  = "0$nMIN"; }
	$IN{'year'} = $nYEAR;
	$IN{'mon'}  = $nMON;
	$IN{'day'}  = $nDAY;
	$IN{'hour'} = $nHOUR;
	$IN{'min'}  = $nMIN;
	$sCURRENT_TIME = sprintf("%04d\/%02d\/%02d(%s)%02d\:%02d" ,$nYEAR,$nMON,$nDAY,$mYOUBI[$nWDAY],$nHOUR,$nMIN);
	$IN{'current_time'} = $sCURRENT_TIME;


	### 各HTMLファイルの定義確認
	unless( -e 'jcode.pl'){
		$error .= 'jcode.plが用意されていません。<BR>';
	}
	unless( -e 'check.txt'){
		$error .= '入力チェック設定ファイルが用意されていません。<BR>';
	}
	unless( -e "$MYSCRIPT"){
		$error .= 'CGIファイル名が正しく指定されていません。<BR>';
	}
	unless( -e "$TEMPLATE1"){
		$error .= 'テンプレート(入力画面)が正しく指定されていません。<BR>';
	}
	if($DISP_CHECK and !( -e "$TEMPLATE2")){
		$error .= 'テンプレート(確認画面)が正しく指定されていません。<BR>';
	}
	unless($LOCATION){
		$error .= '送信完了画面が指定されていません。<BR>';
	}elsif($LOCATION !~ /^http/ and !( -e "$LOCATION")){
		$error .= '送信完了画面が正しく指定されていません。<BR>';
	}

	### 保存ファイル名の確認
	if($SAVE_DATA){
		my $file_date;
		unless( -e "$DATA_DIR"){
			$error .= 'データの保存ディレクトリが正しく指定されていません。<BR>';
		}
		unless($DATA_TERM){
			unless($DATA_CODE){ $DATA_CODE = 'data'; }
		}elsif($DATA_TERM eq 's'){
			$file_date = sprintf("%04d%02d%02d%02d%02d" ,$nYEAR,$nMON,$nDAY,$nMIN,$nSEC);
			$file_date = "$file_date-$$";
		}elsif($DATA_TERM eq 'd'){
			$file_date = sprintf("%04d%02d%02d" ,$nYEAR,$nMON,$nDAY);
		}elsif($DATA_TERM eq 'm'){
			$file_date = sprintf("%04d%02d" ,$nYEAR,$nMON);
		}else{
			$error .= 'データの保存間隔が正しく指定されていません。<BR>';
		}
		$sFILE_NAME = "$DATA_CODE$file_date$DATA_EXT";

		if(($T ne "\t") and ($T ne ',') and ($T ne "\n")){
			$error .= '保存データの区切り文字が適切ではありません。<BR>'
		}
	}

	#-- データ保存関連2のチェックおよびファイル名の設定を追加。2004/2/5 itoh
	if($SAVE_DATA2){
		my $file_date2;
		unless( -e "$DATA_DIR2"){
			$error .= 'データの保存ディレクトリが正しく指定されていません。<BR>';
		}
		unless($DATA_TERM2){
			unless($DATA_CODE2){ $DATA_CODE2 = 'data'; }
		}elsif($DATA_TERM2 eq 's'){
			$file_date2 = sprintf("%04d%02d%02d%02d%02d" ,$nYEAR,$nMON,$nDAY,$nMIN,$nSEC);
			$file_date2 = "$file_date2-$$";
		}elsif($DATA_TERM2 eq 'd'){
			$file_date2 = sprintf("%04d%02d%02d" ,$nYEAR,$nMON,$nDAY);
		}elsif($DATA_TERM2 eq 'm'){
			$file_date2 = sprintf("%04d%02d" ,$nYEAR,$nMON);
		}else{
			$error .= 'データ２の保存間隔が正しく指定されていません。<BR>';
		}
		$sFILE_NAME2 = "$DATA_CODE2$file_date2$DATA_EXT2";

		if(($T2 ne "\t") and ($T2 ne ',') and ($T2 ne "\n")){
			$error .= '保存データ２の区切り文字が適切ではありません。<BR>'
		}
	}

	### メール送信時の設定確認
	my $mailflag = (); #メール使用判断
	if($ADMIN_MAIL){
		$mailflag = 1;
		unless( -e "$ADMIN_MAIL"){
			$error .= '管理者宛メールのテンプレートが指定されていません。<BR>';
		}
		unless($ADMIN_TO =~ /^[_0-9a-zA-Z\.\-\/]+\@\S+\.[a-zA-Z][a-zA-z][a-zA-Z]*$/){
			$error .= '$ADMIN_TO のメールを正しく設定してください。<BR>';
		}
	}
	if($USER_MAIL){
		$mailflag = 1;
		unless( -e "$USER_MAIL"){
			$error .= 'ユーザー宛メールのテンプレートが指定されていません。<BR>';
		}
		unless($USER_SUBJECT){
			$error .= 'ユーザー宛メールのタイトルが指定されていません。<BR>';
		}
		unless($sUSER_FROM_EMAIL){
			if($ADMIN_TO){
				my $admin_to_dummy = $ADMIN_TO;
				($sUSER_FROM_EMAIL, $admin_to_dummy) = split /,/, $admin_to_dummy;
			}else{
				$error .= 'ユーザー宛メールの差出人アドレスが正しく指定されていません。<BR>';
			}
		}
	}
	if($mailflag){
		if($MAILMETHOD == 1){
			unless($sMAILSERVER){
				$error .= '接続するSMTPが設定されていません。<BR>';
			}
		}elsif($MAILMETHOD == 2){
			unless($SENDMAIL){
				$error .= 'sendmailが正しく設定されていません。<BR>';
			}
		}else{
			$error .= 'メール送信方法が正しく選択されていません。<BR>';
		}
		unless( -e 'mimew.pl'){
			$error .= 'mimew.plが用意されていません。<BR>';
		}
	}
	if($error){
		&disp_error('CGIの設定エラー報告', "$error");
	}
}


#-----------------------------------------------------------------------
# call  : &read_template('テンプレートファイル', '表示フラグ1or0');
# text  : テンプレートの読み込み＆置換＆条件的に表示
# return: 表示フラグが0のとき置換したデータを返す
#-----------------------------------------------------------------------
sub read_template{
	my $template = shift; #読み込むテンプレート
	my $disp = shift;     #表示するかどうか

	#-- $next_step=1を表示するときは入力画面、2を表示するときは確認画面
	my $next_step = ();
	if($IN{'error'}){
		if($DISP_CHECK){ $next_step = 1; }	#確認画面ありは=1
		else{ $next_step = 2; }			#確認画面なしは=2
	}elsif($IN{'check0'}){
		$next_step = 1;
	}elsif($IN{'form_step_check'} eq ''){
		#--指定なしで呼ばれている場合
		if($DISP_CHECK){ $next_step = 1; }	#確認画面ありは=1
		else{ $next_step = 2; }			#確認画面なしは=2
	}elsif($IN{'form_step_check'} == 1){
		$next_step = 2;
	}

	#-- HTML表示用の入力値の確認(主に改行と<BR>のみ)
	my (%html, @keys, $key);
	%html = %IN;
	@keys = keys %html;
	foreach $key (@keys){
		if($key eq 'error'){
			next;
		}elsif($next_step == 1){
			#-- 入力画面時、<BR>を改行に変換
			$html{"$key"} =~ s/<BR>/\n/g;
		}elsif($next_step == 2){
			#-- 確認画面時、改行を<BR>に変換
			$html{"$key"} =~ s/\x0D\x0A/<BR>/g;
			$html{"$key"} =~ s/\x0D/<BR>/g;
			$html{"$key"} =~ s/\x0A/<BR>/g;
		}
	}

	#-- やや個別環境 -----------------------------------------------
	if($IN{'file_url'}){
		$html{'file'} = <<"END";
<input type="hidden" name="file_url" value="$IN{'file_url'}">
ファイルのアップロードは完了しています。<BR>
END
	}else{
		$html{'file'} = <<"END";
<input type="file" name="file"><BR>
<div style="font-size: 12px; color: #ff0000">
全角文字を含むフォルダやファイル名の場合、正しくアップロードできない場合があります。<BR>半角のフォルダ、ファイル名にしてから参照をおこなってください。<BR>またアップロードできるファイルのデータサイズは最大$SIZE_MAX byteです。</div>
END
	}
	#---------------------------------------------------------------

	#-- 置換開始
	my ($text, $h_flg); #全体、hidden付記用
	my ($s_flg, $s_name, $s_key, %selected); #selected付記用
	my ($c_flg, $c_name, $c_key, %checked);  #checked付記用
	open TEMPLATE, "<$template" or &disp_error("送信画面のテンプレートファイルの読み込みに失敗しました。");
	while(<TEMPLATE>){
		&jcode::convert(\$_, 'euc');

		#-- <SELECT>のselectedの条件を探す
		if($_ =~ /<select /i){ $s_flg = 1; }
		if($s_flg){
			if($_ =~ /name=["|']?([^ \f\n\r\t\"\']+)["|']?/i){
				$s_name = $1;
				if(defined $s_name){
					$s_key = $IN{"$s_name"};
					$selected{"$s_key"} = 'selected';
				}
			}
			if(0 <= (index "$_", '>')){
				$s_name = ();
				$s_flg = 0;
			}
		}
		if($_ =~ /<\/select>/i){ %selected = (); }

		#-- <input type="checkbox">,<input type="radio">のcheckedの条件を探す
		if($_ =~ /type=["|']?checkbox["|']?/i){ $c_flg = 1; }
		elsif($_ =~ /type=["|']?radio["|']?/i){ $c_flg = 1; }
		if($c_flg){
			if($_ =~ /name=["|']?([^ \f\n\r\t\"\']+)["|']?/i){
				$c_name = $1;
				if(defined $c_name){
					$c_key = $IN{"$c_name"};
					$checked{"$c_key"} = 'checked';
				}
			}
			if(0 <= (index "$_", '>')){
				$c_name = ();
				$c_flg = 0;
			}
		}

		#-- HIDDEN値の埋めこみ(少しややこしい)
		if($_ =~ /<form/i){ $h_flg = 1; }		# <form>タグ開始で1
		if($h_flg){
			if(0 <= (index "$_", "$MYSCRIPT")){ $h_flg = 2; }
								# このCGIを呼んでたら2
			if($h_flg == 1){			# 1のまま閉じてたら
				if(0 <= (index "$_", '>')){ $h_flg = 0; }
								# 状態を0に戻す
			}elsif($h_flg == 2){			# 2の状態で閉じてたら
				$_ =~ s/>/>\n<input type=\"hidden\" name=\"form_step_check\" value=\"$next_step\">\n$input_hidden/o;
								# HIDDEN値を埋め込んで
				$h_flg = 0;			# 状態を0に戻す
			}
		}

		if(0 <= (index "$_", '$')){
			if(0 <= (index "$_", '$selected')){
				$_ =~ s/\$selected\{(.+)\}/$selected{"$1"}/g;

			}elsif(0 <= (index "$_", '$checked')){
				$_ =~ s/\$checked\{(.+)\}/$checked{"$1"}/g;
				$checked{"$1"} = ();
			}
#			$_ =~ s/\$([^ \r\t\n\f\"\'\<\>\$\,\&\=\-\:\/\{\}\\\[\]]+)/$html{"$1"}/g;
			$_ =~ s/\$([A-Za-z0-9_]+)/$html{"$1"}/g;
		}
		$text .= $_;
		%checked = ();
	}
	close TEMPLATE;

	if($disp){
		print "$nHEADER";
		&jcode::convert(\$text, "$TEMPLATE_CODE");
		print "$text";
		exit;
	}else{
		return $text;
	}
}


#-----------------------------------------------------------------------
# call  : &check_input_data
# text  : check.txtに従って入力内容の確認
# return: 返り値なし
#-----------------------------------------------------------------------
sub check_input_data {
	my (@check, $name, $item, $requir, $type, $num, $value, %unique, @error);
	my (%choice, @groups, $error);
	#-- 必須項目チェックなど
	open CHECK, "<check.txt" or &disp_error("入力チェック設定ファイルが読みこめません。");
	@check = <CHECK>;
	close CHECK;
	foreach (@check){
		&jcode::convert(\$_, 'euc');
		if(0 == (index "$_", '#')){ next; }		# コメント行は飛ばす
		chomp;
		($name, $item, $require, $type, $num, $group) = split /\t/;
		$value = $IN{"$name"};
		$item{"$name"} = $item;
		++$name{"$name"};

		#-- 値の最後に改行がいっぱいある場合は消しておく
		while($value =~ /\x0D\x0A$/){ chomp $value; }

		#-- 値の確認
		if($value eq ''){ # 「0」の入力は通す
			#-- 必須入力のチェック(or必須)
			if($require eq 'or' and $group){
				#-- 入力がなく、他にも入力がない状態
				unless($choice{"$group"}){
					if((index $error, "<!--$group-->") < 0){
						$error .= "<!--$group-->$item をどれかご回答ください。<BR>\n";
					}
				}
			#-- 必須入力のチェック(絶対必須)
			}elsif($require){
				unless($group and $unique{"$group"}){
					$error .= "$item をご入力ください。<BR>\n";
					++$unique{"$group"};
				}
			}
		}else{
			#-- 必須入力のチェック(or必須) 入力があれば覚えておく
			if($require eq 'or' and $group){ ++$choice{"$group"}; }
			#-- 半角数字のチェック( , - は通す)
			if($type eq '1' and $value =~ /[^0-9\,\-]/){
				$error .= "$item を半角数字でご入力ください。<BR>\n";
			#-- 半角英数のチェック
			}elsif($type eq 'a' and $value =~ /\W/){
				$error .= "$item を半角英数でご入力ください。<BR>\n";
			#-- メール形式のチェック
			}elsif($type eq 'e' and $value !~ /^[_0-9a-zA-Z\.\-\/]+\@\S+\.[a-zA-Z][a-zA-z][a-zA-Z]*$/){
				$error .= "$item を正しくご入力ください。<BR>\n";
			#-- 再入力のチェック
			}elsif($type and $name{"$type"} and $IN{"$type"} ne $IN{"$name"}){
				$error .= "$item は $item{$type} と同じ内容を入力してください。<BR>\n";
			}
			#-- 文字数のチェック
			if($num and $num < length($value)){
				$error .= "$item を半角$num文字以下でご入力ください。<BR>\n";
			}
		}
	}

	#-- 最後に必須入力(or必須)の入力があるものはエラーから除外
	@groups = keys %choice;
	foreach $group (@groups){
		$error =~ s/<!--$group-->[^\<]*<BR>\n//;
	}

	if($error){					# エラーがあれば
#		&jcode::convert(\$error, 'euc');
		$IN{'error'} = $error;
		&read_template("$TEMPLATE1", "1");	# 入力画面再表示
	}else{
		my (@keys, $key);
		@keys = keys %IN;
		foreach $key (@keys){
			unless(defined $IN{"$key"}){ next; }
			elsif($key eq 'remote_host'){ next; }
			elsif($key eq 'remote_addr'){ next; }
			elsif($key eq 'http_referer'){ next; }
			elsif($key eq 'user_agent'){ next; }
			elsif($key eq 'form_step_check'){ next; }
			elsif($key eq 'current_time'){ next; }
			elsif($key eq 'year'){ next; }
			elsif($key eq 'mon'){ next; }
			elsif($key eq 'day'){ next; }
			elsif($key eq 'min'){ next; }
			elsif($key eq 'sec'){ next; }
			elsif($key eq 'file_url'){ next; }
			elsif($key =~ /^submit$/i){ next; }
			else{
				$input_hidden .= <<"END";
<input type="hidden" name="$key" value="$IN{$key}">
END
			}
		}
	}
}


#-----------------------------------------------------------------------
# call  : &disp_error('表示タイトル', 'メッセージ');
# text  : 与えられたタイトルとメッセージを表示する
# return: 返り値なし
#-----------------------------------------------------------------------
sub disp_error {
	my $title = shift;
	my $message = shift;
	if($title and !$message){
		$message = $title;
		$title = 'エラーメッセージ';
	}
	print "$nHEADER";
	if($nCAREER ne 'e'){
		&disp_header("$title");
		print <<"END";
<div align="center">
<table border="0" width="450" cellpadding="2" cellspacing="1">
 <tr><td class="td">$message</td></tr>
</table><BR> <BR> <BR>
[<A HREF=JavaScript:history.back()>戻る</A>]
</div>
END
		&disp_footer;
	}else{
		my $html .= <<"END";
<?xml version="1.0" encoding="Shift_JIS"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=Shift_JIS" />
<title>$message</title>
</head>
<body bgcolor="#FFFFFF" text="#000000" link="#FF9900" vlink="#FFCE86" alink="#FF0000">
$message
<br />

</body>
</html>
END
		&jcode::convert(\$html, 'sjis');
		print $html;
	}
	exit;
}


#-----------------------------------------------------------------------
# call  : &save_data;
# text  : setting.plの設定条件に従ってデータを保存
# return: 返り値なし
#-----------------------------------------------------------------------
sub save_data {
	my ($data, $lfh, @filelist, $data_temp);
	my $flag = 0;  #<-- $flag=0;を明確に定義すること。

	#-- ファイルの存在確認
	opendir DIR, $DATA_DIR;
  	@filelist = readdir DIR;
	closedir DIR;
	foreach (@filelist) {
		if(/^$sFILE_NAME(\d*)/) { $flag = 1; last; }
	}
	#-- 保存ファイルもロックファイルも無かったらファイル作成
	unless($flag){
		if(@DATA_HEADER){
			$data = ();
			foreach (@DATA_HEADER){ $data .= "$_$T"; }
		}
		open DATA, ">$DATA_DIR/$sFILE_NAME" or &disp_error("データを保存することができません。<!--1a-->");
		if($data){
			&jcode::convert(\$data, "sjis");
			print DATA "$data\n";
		}
		close DATA;
		chmod 0666, "$DATA_DIR/$sFILE_NAME";
	}

	#-- ここから通常の保存処理
	$data = ();
	@data_name_temp = @DATA_NAME;
	foreach $data_temp (@data_name_temp){
		$data_temp =~ s/\$([a-zA-Z0-9_]+)/$IN{"$1"}/g;
		$data .= "$data_temp$T";
	}
	$data =~ tr/\x0D\x0A//d;			# 改行コード削除
	&jcode::convert(\$data, "sjis");

	# ロック処理開始 $lfhは解除キー
	require 'filelock.pl';				# ファイルロックの読込
	$lfh = &filelock($DATA_DIR, $sFILE_NAME);
	open DATA, ">>$lfh->{current}" or &disp_error("データを保存することができません。<!--1b-->");
	print DATA "$data\n";
	close DATA;

	&fileunlock($lfh);				# ロック解除
	$lfh = ();
}


#-----------------------------------------------------------------------
# call  : &save_data2;
# text  : setting.plの設定条件に従ってデータを保存（予備保存用）
# return: 返り値なし
#-----------------------------------------------------------------------
sub save_data2 {
	my ($data, $lfh, @filelist, $data_temp);
	my $flag = 0;  #<-- $flag=0;を明確に定義すること。

	#-- ファイルの存在確認
	opendir DIR, $DATA_DIR2;
  	@filelist = readdir DIR;
	closedir DIR;
	foreach (@filelist) {
		if(/^$sFILE_NAME(\d*)/) { $flag = 1; last; }
	}
	#-- 保存ファイルもロックファイルも無かったらファイル作成
	unless($flag){
		if(@DATA_HEADER2){
			$data = ();
			foreach (@DATA_HEADER2){ $data .= "$_$T"; }
		}
		open DATA, ">$DATA_DIR2/$sFILE_NAME2" or &disp_error("データを保存することができません。<!--2a-->");
		if($data){
			&jcode::convert(\$data, "sjis");
			print DATA "$data\n"
		}
		close DATA;
		chmod 0666, "$DATA_DIR2/$sFILE_NAME2";
	}

	$data = ();
	@data_name_temp = @DATA_NAME2;
	foreach $data_temp (@data_name_temp){
		$data_temp =~ s/\$([a-zA-Z0-9_-]+)/$IN{"$1"}/g;
		$data .= "$data_temp$T";
	}
	$data =~ tr/\x0D\x0A//d;			# 改行コード削除
	&jcode::convert(\$data, "sjis");

	# ロック処理開始 $lfhは解除キー
	require 'filelock.pl';				# ファイルロックの読込
	$lfh = &filelock($DATA_DIR2, $sFILE_NAME2);
	open DATA, ">>$lfh->{current}" or &disp_error("データを保存することができません。<!--2b-->");
	print DATA "$data\n";
	close DATA;
	&fileunlock($lfh);				# ロック解除
	$lfh = ();
}


#-----------------------------------------------------------------------
# call  : &make_mail_header;
# text  : sendmailで表示するためのメールヘッダーの作成
# return: グローバル変数にするので返り値なし
#-----------------------------------------------------------------------
sub make_mail_header {
	#-- メールのヘッダー部分の作成
	$sMAIL_HEADER = <<"END";
X-Processed: $sCURRENT_TIME
X-HTTP_REFERER: $sHTTP_REFERER
X-HTTP-User-Agent: $sUSER_AGENT
X-Remote-host: $sREMOTE_HOST
X-Remote-Addr: $sREMOTE_ADDR
MIME-Version: 1.0
Content-Type: text/plain; charset="iso-2022-jp"
Content-Transfer-Encoding: 7bit
X-Mailer: MAILFORM v1.02 copyright(c)sun-co-ltd.com
END
	require 'mimew.pl';				# mimew.plを読みこみ
}


#-----------------------------------------------------------------------
# call  : &send_email_admin;
# text  : 管理者宛メールの送信
# return: 返り値なし
#-----------------------------------------------------------------------
sub send_email_admin{
	my ($mail_data, $from, $to, $subject);
	my $to_address = $ADMIN_TO;
	#-- 管理者にメールを送る

	#-- From部分生成
	if($ADMIN_FROM eq 'user'){
		unless($IN{'email'} =~ /^[_0-9a-zA-Z\.\-\/]+\@\S+\.[a-zA-Z][a-zA-z][a-zA-Z]*$/){
			$from = "From: $to_address";
		}else{
			$from = "From: $IN{'name'} <$IN{'email'}>";
		}
	}else{
		$from = "From : $ADMIN_TO";
	}
	&jcode::convert(\$from, 'jis');
	$from = &mimeencode($from);
	#-- メール本文生成
	$mail_data = &read_template("$ADMIN_MAIL");
	$mail_data =~ s/<BR>/\n/gi;
	&jcode::convert(\$mail_data, 'jis');
	&jcode::convert(\$ADMIN_SUBJECT, 'jis');
	&jcode::convert(\$subject, 'jis');
	$to = $to_address;
	$subject = "$ADMIN_SUBJECT [$sCURRENT_TIME]";

	&mail($sMAIL_HEADER, $from, $to, $subject, $mail_data);
}


#-----------------------------------------------------------------------
# call  : &send_email_user;
# text  : ユーザー宛メールの送信
# return: 返り値なし
#-----------------------------------------------------------------------
sub send_email_user{
	my ($mail_data, $from);
	#-- ユーザーにメールを送る

	#-- From部分生成
	$from = "From: $USER_FROM_NAME <$sUSER_FROM_EMAIL>";
	&jcode::convert(\$from, 'jis');
	$from = &mimeencode($from);
	#-- メール本文生成
	$mail_data = &read_template("$USER_MAIL");
	$mail_data =~ s/<BR>/\n/gi;
	&jcode::convert(\$mail_data, 'jis');
	&jcode::convert(\$USER_SUBJECT, 'jis');
	$to = $IN{'email'};
	$subject = $USER_SUBJECT;
	&mail($sMAIL_HEADER, $from, $to, $subject, $mail_data);
}


#-----------------------------------------------------------------------
# call  : &mail('ヘッダー','From','送り先Email','Subject','本文');
# text  : 実際のメール送信処理
# return: 返り値なし
#-----------------------------------------------------------------------
sub mail{
	#-- メール送信の本体部分
	my $mail_header = shift;
	my $from        = shift;
	my $to          = shift;
	my $subject     = shift;
	my $mail_data   = shift;

	if($MAILMETHOD == 2){
		open MAIL, "|$SENDMAIL -t" or &disp_error('送信に失敗しました。');
		print MAIL "$mail_header";
		print MAIL "$from\n";
		print MAIL "To: $to\n";
		print MAIL "Subject: $subject\n";
		print MAIL "\n";
		print MAIL "$mail_data";
		close MAIL;
	}elsif($MAILMETHOD == 1){
		my $sock_stream = 1 ;	#-- この部分は動かない場合は2
		my $pf_inet = 2;
		my $port = 25; 
		my $iaddr = gethostbyname($sMAILSERVER); #[4];
#		my $iaddr = gethostbyname($sMAILSERVER, 4); #[4];
		my $s_type = 'S n a4 x8';
		my $sock_addr = pack($s_type, $pf_inet, $port, $iaddr);
		socket(SMTP, $pf_inet, $sock_stream, 0) or &error("socket: $!");
		connect(SMTP, $sock_addr) or &error("connect: $!");

		&syswr("220", "HELO localhost\r\n");
		&syswr("250", "MAIL From: $sSMTP_FROM\r\n"); 
		&syswr("250", "RCPT To: $to\r\n");
		&syswr("250", "DATA\r\n");
		&syswr("354", "$from\n",
		              "To: $to\n",
		              "Subject: $subject\n\n",
		              "$mail_data\r\n.\r\n"
		      );
		&syswr("250", "QUIT\r\n");
		&syswr("221");
		close SMTP;
	}
}


#-----------------------------------------------------------------------
# call  : &syswr('値');
# text  : SMTPで送信するときの予備関数
# return: 返り値なし
#-----------------------------------------------------------------------
sub syswr{
	my $buf = "";
	if (sysread(SMTP, $buf, 1024) > 0) {
#		print $buf;
		my $rsp = substr($buf, 0, 3);
		($rsp == $_[0]) || die "bad response";
		shift(@_);
		foreach (@_){
			syswrite(SMTP, $_, length($_));
		}
	}
}


#-----------------------------------------------------------------------
# call  : &disp_header('タイトル', 'リフレッシュする場合はURL');
# text  : 本CGIで出力するHTML(完了画面などの)ヘッダー
# return: 返り値なし
#-----------------------------------------------------------------------
sub disp_header{
	my $title = shift;
	my $jump_url  = shift;
	print <<"END";
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ja">
<head>
<META http-equiv="content-type" content="text/html;charset=x-euc-jp">
<META http-equiv="Content-Style-Type" content="text/css">
<META http-equiv="Content-Script-Type" content="text/javascript">
END
	if($jump_url){
		print <<"END";
<META HTTP-EQUIV="Refresh" CONTENT="1;URL=$MYSCRIPT?$IN{'query_string'}">
END
	}
	print <<"END";
<style>
.td { border-color: #CCCCCC #666666 #666666 #CCCCCC; border-style: solid; border-top-width: 1px; border-right-width: 1px; border-bottom-width: 1px; border-left-width: 1px; font-size: 10pt }
</style>
<title>$title</title>
</head>
<div align="center">
<table border="0" width="450" cellpadding="4">
 <tr>
  <td style="font-size: 10pt" bgcolor="$COLOR" align="center" class="td">$title</td>
 </tr>
</table>
</div><br>
END
}


#-----------------------------------------------------------------------
# call  : &disp_footer;
# text  : 本CGIで出力するHTMLフッター(copyrightなど表示)
# return: 返り値なし
#-----------------------------------------------------------------------
sub disp_footer{
	### copyright表示(変更不可)ほとんど使いませんね、ここ。
	my $copyright = 'copyright(c) www.sun-co-ltd.com<BR>';
	print <<"END";
<div align="center" style="font-size: 10pt">
<hr size="1" color="$COLOR">
$copyright<BR>
</div>
</body>
</html>
END
}


#-----------------------------------------------------------------------
# call  : &parse_form_data(*IN);
# text  : パース走査処理。全半角置換、サニタイジングもおこなう。
# return: (*IN)と指定すれば%INに格納される。グローバルなので、返り値なし
#-----------------------------------------------------------------------
sub parse_form_data {

	local ( *FORM_DATA ) = @_;
	local ( $query_string, $pairs, $key_value, $key, $value );

	read ( STDIN, $query_string, $ENV{'CONTENT_LENGTH'} );

	if( $ENV{'QUERY_STRING'}){
		$query_string = join("&", $query_string, $ENV{'QUERY_STRING'});
	}

	@pairs = split( /&/, $query_string );

	foreach $key_value ( @pairs ){
		( $key, $value ) = split( /=/, $key_value );
		$key =~ tr/+/ /;
		$value =~ tr/+/ /;

		$key 	=~ s/%([\dA-Fa-f][\dA-Fa-f])/pack("C", hex($1))/eg;
		$value 	=~ s/%([\dA-Fa-f][\dA-Fa-f])/pack("C", hex($1))/eg;

		&jcode::convert(\$value, "euc");

		#-- サニタイジング処理
#		$value =~ s/&/&amp;/g; # タグ禁止
#		$value =~ s/"/&quot;/g;
#		$value =~ s/</&lt;/g;
#		$value =~ s/>/&gt;/g;

		$value =~ s/&/＆/g; # タグ禁止
		$value =~ s/"/”/g;
		$value =~ s/</＜/g;
		$value =~ s/>/＞/g;
		$value =~ s/,/，/g;
		$value =~ s/＜BR＞/<BR>/ig;

		#-- 全半角置換
		if($Z_TO_H){
			&jcode::tr(\$value, '０-９Ａ-Ｚａ-ｚ', '0-9A-Za-z'); 
			&jcode::tr(\$value, '　（）＿＠−．，', ' ()_@-.,');
		}

		if( defined( $FORM_DATA{ $key }) ){
#			$FORM_DATA{ $key } = join( "\0", $FORM_DATA{ $key }, $value );
			$FORM_DATA{ $key } = "$FORM_DATA{ $key }, $value";
		} else {
			$FORM_DATA{ $key } = $value;
		}
	}
}


#-----------------------------------------------------------------------
# call  : &read_stdin;
# text  : ファイルアップロード有りのパース走査処理。サニタイジング。
# return: 強制的に%INに格納される。返り値なし。
#-----------------------------------------------------------------------
sub read_stdin{
	my ($buf, $read_data, $remain, @headers, $delimiter, $up_file_name, $name, $i);

	#-- 標準入力からデータを読みだす
	$buf = "";
	$read_data = "";
	$remain = $ENV{'CONTENT_LENGTH'};
	binmode(STDIN);
	while($remain){
		$remain -= sysread(STDIN, $buf, $remain);
		$read_data .= $buf;
	}

	#-- ヘッダ処理
	@headers = split /\x0D\x0A/, $read_data;
	$buf = $read_data = $remain = ();

	$delimiter = "";
	$up_file_name = "";
	$name = "";
	$i = 0;

	for($i = 0; (defined($headers[$i]) or ($jump)); ++$i){
		unless($delimiter_temp){ $delimiter_temp = $headers[$i]; }

		if($jump){
			$jump = ();
		}elsif(0 == (index $headers[$i], $delimiter_temp)){
			$name = ();
			$delimiter = 1;
		}elsif($headers[$i] =~ /^Content-Disposition: ([^;]*); name="([^;]*)"; filename="([^;]*)"/i){
			if($3){
				$up_file_name = $3;
				if($up_file_name =~ /([^\\\/]+$)/){
					$up_file_name = $1;
				}
			}
			$name = $2;
		}elsif($headers[$i] =~ /^Content-Type:/i){
			$delimiter = ();
			$jump = 1;
		}elsif($headers[$i] =~ /^Content-Disposition: ([^;]*); name="([^;]*)"/i){
			$delimiter = ();
			$jump = 1;
			$name = $2;
		}elsif(($name) and !($delimiter)){
			if($name eq 'file'){
				$IN{'file'} .= "$headers[$i]\x0D\x0A";
			}else{
				$headers[$i] =~ s/&/＆/g; # タグ禁止
				$headers[$i] =~ s/"/”/g;
				$headers[$i] =~ s/</＜/g;
				$headers[$i] =~ s/>/＞/g;
				$headers[$i] =~ s/,/，/g;
				$headers[$i] =~ s/＜BR＞/<BR>/ig;
				unless($IN{"$name"}){
					$IN{"$name"} = "$headers[$i]";
				}else{
#					$IN{"$name"} .= ", $headers[$i]";
					$IN{"$name"} = join("\n", $IN{"$name"}, $headers[$i] );
				}
			}
		}
#		if(50 <= $i){ last; }
	}

	#-- 保存するファイル名と拡張子の確認
	my @ext = ('jpg', 'jpeg', 'gif', 'bmp');
	for($i = 0; $ext[$i]; ++$i){
		if($up_file_name =~ /$ext[$i]$/){
			$ext_ok = 1;
			last;
		}
	}
	if($up_file_name){
		#-- ファイルサイズの確認
		$size = length($IN{'file'});

		unless($ext_ok){
			$error .= "添付されたファイルの形式は許可されていません。<BR>";
		}

		#-- 上書きの確認
		if($FILE_UPDATE){
			if( -e "$DATA_DIR/$up_file_name"){
				$error .= "同じ名前のファイルが存在しています。<BR>";
			}
		}

		if($ZERO_BYTE){
			unless($size){
				$error .= "0byteのファイルはアップロードできません。";
			}
		}

		if($SIZE_MAX){
			if($SIZE_MAX < $size){
				$error .= "アップロードできるファイルの最大サイズは $SIZE_MAX byte までです。";
			}
		}

		if($up_file_name =~ /[^A-Za-z0-9-_.]/){
			$error .= "アップロードするファイル名は半角英数でご指定ください。";
		}

		unless($error){
			#-- 問題なければファイルを保存
			open OUT, ">$DATA_DIR/$up_file_name" or &disp_error("ファイルの保存に失敗しました");
			binmode(OUT);
			print OUT "$IN{'file'}";
			close(OUT);
			undef $IN{'file'};
			chmod 0666, "$DATA_DIR/$up_file_name";
			$IN{'file_url'} = "$DATA_DIR_URL/$up_file_name";
		}
	}
}
