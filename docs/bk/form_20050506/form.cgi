#!/usr/bin/perl --
########################################################################
#
#       ̾  ����sun-co-ltd.com/form_base ver1.07
#       ��  �sun-co-ltd.com ����ε���������ͭ��
#       �����������CGI���Ȥ�ʸ�������ɤ�EUC����Ǥ���
#       ��  �ơ�2003/1/27 �����ե�����Υ١����ˤʤ�CGI
#             ��          mimew.pl, jcode.pl, filelock.pl ��ɬ��
#             ��          ���꤬�٤����ʤ����option.pl��ɬ��
#             ��2003/3/16 SJIS�ƥ�ץ졼�Ȥ��б�
#             ��2003/8/2  �ѿ�̾��ϥ󥬥꡼ɽ�����ѹ���subscript��������
#             ��2004/2/5  itoh���إå����Фʤ����������
#             ��          �ǡ������Υ����å�����ӥե�����̾������ȴ�����䴰
#             ��          ������"0"��ɬ�ܻ��˥��顼�ˤʤ��������
#             ��2004/2/26 �ǿ��Ǥ�ʬ�����Ƥ��ޤä��Τ����礷��
#             ��2004/3/1  �᡼����ʸ�Υ����ɤ�sjis��jis�˽�������(Mac�к�)
#             ��2004/3/2  �᡼�륢�ɥ쥹�����ǡ������ˡ�/�פ���Ƥ���
#
########################################################################
require 'setting.pl';

#######
# �ᥤ��
###
&setting_check;						# �������Ƥ����礹��
require './jcode.pl';

if($sREQUEST_METHOD eq "POST"){
	if($ENV{'CONTENT_TYPE'}  =~ m!^multipart/form-data!){
		&read_stdin;
	}else{
		&parse_form_data( *IN );
	}
}

if(!$IN{'form_step_check'} or $IN{'check0'}){
	&read_template("$TEMPLATE1", "1");		# ���ϲ��̤�ɽ��
}elsif($IN{'form_step_check'} == 1 and $DISP_CHECK){
	&check_input_data;				# ���ܤΥ����å�
	&read_template("$TEMPLATE2", "1");		# ��ǧ���̤�ɽ��

}elsif(($IN{'form_step_check'} == 2) or $IN{'check2'}){
	&check_input_data;				# ���ܤΥ����å�
	if($SAVE_DATA){ &save_data; }			# �ǡ�����¸
	if($SAVE_DATA2){ &save_data2; }			# �ǡ�����¸
	if($ADMIN_MAIL or $USER_MAIL){			# �᡼����������
		&make_mail_header;
		if($ADMIN_MAIL){ &send_email_admin; }
		if($USER_MAIL and $IN{'email'}){ &send_email_user; }
	}
	if($LOCATION_OK){
		print "Location: $LOCATION\n\n";	# ���󥯥��ڡ�����ɽ��
	}else{
		&read_template("$LOCATION", "1");
	}
}
exit;


#-----------------------------------------------------------------------
# call  : &setting_check;
# text  : CGI�μ��פ������ǧ��call���ν��������
# return: none
#-----------------------------------------------------------------------
sub setting_check{
	my $error = ();

	#-- ����ꥢ��Ƚ��
	my $agent = $ENV{'HTTP_USER_AGENT'};
	if($agent =~ /DoCoMo/i){ $nCAREER = 'i'; }
	elsif($agent =~ /J-PHONE/i){ $nCAREER = 'j'; }
	elsif($agent =~ /UP\.Browser/i){ $nCAREER = 'e'; }
	else{ $nCAREER = 'pc'; }

	#-- �����̤�����ե������require������ϵ��ҡ�ɸ���setting.pl��
	if($nCAREER eq 'i' and -e 'setting_i.pl'){
		require 'setting_i.pl';
	}elsif($nCAREER eq 'j' and -e 'setting_j.pl'){
		require 'setting_j.pl';
	}elsif($nCAREER eq 'e' and -e 'setting_e.pl'){
		require 'setting_e.pl';
	}else{
		unless( -e 'setting.pl'){ $error .= "����ե����뤬��ǧ�Ǥ��ޤ������������֤���Ƥ��ʤ���ǽ��������ޤ���"; }
		require 'setting.pl';
	}

	#-- ���ϥإå����γ���
	if($nCAREER ne 'e'){ $nHEADER = "Content-type: text/html;\n\n"; }
	else{ $nHEADER = "Content-type:text/html;charset=Shift_JIS;\n\n"; }

	#-- �桼��������μ���
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

	### ���֤μ���
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


	### ��HTML�ե�����������ǧ
	unless( -e 'jcode.pl'){
		$error .= 'jcode.pl���Ѱդ���Ƥ��ޤ���<BR>';
	}
	unless( -e 'check.txt'){
		$error .= '���ϥ����å�����ե����뤬�Ѱդ���Ƥ��ޤ���<BR>';
	}
	unless( -e "$MYSCRIPT"){
		$error .= 'CGI�ե�����̾�����������ꤵ��Ƥ��ޤ���<BR>';
	}
	unless( -e "$TEMPLATE1"){
		$error .= '�ƥ�ץ졼��(���ϲ���)�����������ꤵ��Ƥ��ޤ���<BR>';
	}
	if($DISP_CHECK and !( -e "$TEMPLATE2")){
		$error .= '�ƥ�ץ졼��(��ǧ����)�����������ꤵ��Ƥ��ޤ���<BR>';
	}
	unless($LOCATION){
		$error .= '������λ���̤����ꤵ��Ƥ��ޤ���<BR>';
	}elsif($LOCATION !~ /^http/ and !( -e "$LOCATION")){
		$error .= '������λ���̤����������ꤵ��Ƥ��ޤ���<BR>';
	}

	### ��¸�ե�����̾�γ�ǧ
	if($SAVE_DATA){
		my $file_date;
		unless( -e "$DATA_DIR"){
			$error .= '�ǡ�������¸�ǥ��쥯�ȥ꤬���������ꤵ��Ƥ��ޤ���<BR>';
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
			$error .= '�ǡ�������¸�ֳ֤����������ꤵ��Ƥ��ޤ���<BR>';
		}
		$sFILE_NAME = "$DATA_CODE$file_date$DATA_EXT";

		if(($T ne "\t") and ($T ne ',') and ($T ne "\n")){
			$error .= '��¸�ǡ����ζ��ڤ�ʸ����Ŭ�ڤǤϤ���ޤ���<BR>'
		}
	}

	#-- �ǡ�����¸��Ϣ2�Υ����å�����ӥե�����̾��������ɲá�2004/2/5 itoh
	if($SAVE_DATA2){
		my $file_date2;
		unless( -e "$DATA_DIR2"){
			$error .= '�ǡ�������¸�ǥ��쥯�ȥ꤬���������ꤵ��Ƥ��ޤ���<BR>';
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
			$error .= '�ǡ���������¸�ֳ֤����������ꤵ��Ƥ��ޤ���<BR>';
		}
		$sFILE_NAME2 = "$DATA_CODE2$file_date2$DATA_EXT2";

		if(($T2 ne "\t") and ($T2 ne ',') and ($T2 ne "\n")){
			$error .= '��¸�ǡ������ζ��ڤ�ʸ����Ŭ�ڤǤϤ���ޤ���<BR>'
		}
	}

	### �᡼���������������ǧ
	my $mailflag = (); #�᡼�����Ƚ��
	if($ADMIN_MAIL){
		$mailflag = 1;
		unless( -e "$ADMIN_MAIL"){
			$error .= '�����԰��᡼��Υƥ�ץ졼�Ȥ����ꤵ��Ƥ��ޤ���<BR>';
		}
		unless($ADMIN_TO =~ /^[_0-9a-zA-Z\.\-\/]+\@\S+\.[a-zA-Z][a-zA-z][a-zA-Z]*$/){
			$error .= '$ADMIN_TO �Υ᡼������������ꤷ�Ƥ���������<BR>';
		}
	}
	if($USER_MAIL){
		$mailflag = 1;
		unless( -e "$USER_MAIL"){
			$error .= '�桼�������᡼��Υƥ�ץ졼�Ȥ����ꤵ��Ƥ��ޤ���<BR>';
		}
		unless($USER_SUBJECT){
			$error .= '�桼�������᡼��Υ����ȥ뤬���ꤵ��Ƥ��ޤ���<BR>';
		}
		unless($sUSER_FROM_EMAIL){
			if($ADMIN_TO){
				my $admin_to_dummy = $ADMIN_TO;
				($sUSER_FROM_EMAIL, $admin_to_dummy) = split /,/, $admin_to_dummy;
			}else{
				$error .= '�桼�������᡼��κ��пͥ��ɥ쥹�����������ꤵ��Ƥ��ޤ���<BR>';
			}
		}
	}
	if($mailflag){
		if($MAILMETHOD == 1){
			unless($sMAILSERVER){
				$error .= '��³����SMTP�����ꤵ��Ƥ��ޤ���<BR>';
			}
		}elsif($MAILMETHOD == 2){
			unless($SENDMAIL){
				$error .= 'sendmail�����������ꤵ��Ƥ��ޤ���<BR>';
			}
		}else{
			$error .= '�᡼��������ˡ�����������򤵤�Ƥ��ޤ���<BR>';
		}
		unless( -e 'mimew.pl'){
			$error .= 'mimew.pl���Ѱդ���Ƥ��ޤ���<BR>';
		}
	}
	if($error){
		&disp_error('CGI�����ꥨ�顼���', "$error");
	}
}


#-----------------------------------------------------------------------
# call  : &read_template('�ƥ�ץ졼�ȥե�����', 'ɽ���ե饰1or0');
# text  : �ƥ�ץ졼�Ȥ��ɤ߹��ߡ��ִ������Ū��ɽ��
# return: ɽ���ե饰��0�ΤȤ��ִ������ǡ������֤�
#-----------------------------------------------------------------------
sub read_template{
	my $template = shift; #�ɤ߹���ƥ�ץ졼��
	my $disp = shift;     #ɽ�����뤫�ɤ���

	#-- $next_step=1��ɽ������Ȥ������ϲ��̡�2��ɽ������Ȥ��ϳ�ǧ����
	my $next_step = ();
	if($IN{'error'}){
		if($DISP_CHECK){ $next_step = 1; }	#��ǧ���̤����=1
		else{ $next_step = 2; }			#��ǧ���̤ʤ���=2
	}elsif($IN{'check0'}){
		$next_step = 1;
	}elsif($IN{'form_step_check'} eq ''){
		#--����ʤ��ǸƤФ�Ƥ�����
		if($DISP_CHECK){ $next_step = 1; }	#��ǧ���̤����=1
		else{ $next_step = 2; }			#��ǧ���̤ʤ���=2
	}elsif($IN{'form_step_check'} == 1){
		$next_step = 2;
	}

	#-- HTMLɽ���Ѥ������ͤγ�ǧ(��˲��Ԥ�<BR>�Τ�)
	my (%html, @keys, $key);
	%html = %IN;
	@keys = keys %html;
	foreach $key (@keys){
		if($key eq 'error'){
			next;
		}elsif($next_step == 1){
			#-- ���ϲ��̻���<BR>����Ԥ��Ѵ�
			$html{"$key"} =~ s/<BR>/\n/g;
		}elsif($next_step == 2){
			#-- ��ǧ���̻������Ԥ�<BR>���Ѵ�
			$html{"$key"} =~ s/\x0D\x0A/<BR>/g;
			$html{"$key"} =~ s/\x0D/<BR>/g;
			$html{"$key"} =~ s/\x0A/<BR>/g;
		}
	}

	#-- �����̴Ķ� -----------------------------------------------
	if($IN{'file_url'}){
		$html{'file'} = <<"END";
<input type="hidden" name="file_url" value="$IN{'file_url'}">
�ե�����Υ��åץ��ɤϴ�λ���Ƥ��ޤ���<BR>
END
	}else{
		$html{'file'} = <<"END";
<input type="file" name="file"><BR>
<div style="font-size: 12px; color: #ff0000">
����ʸ����ޤ�ե������ե�����̾�ξ�硢���������åץ��ɤǤ��ʤ���礬����ޤ���<BR>Ⱦ�ѤΥե�������ե�����̾�ˤ��Ƥ��黲�Ȥ򤪤��ʤäƤ���������<BR>�ޤ����åץ��ɤǤ���ե�����Υǡ����������Ϻ���$SIZE_MAX byte�Ǥ���</div>
END
	}
	#---------------------------------------------------------------

	#-- �ִ�����
	my ($text, $h_flg); #���Ρ�hidden�յ���
	my ($s_flg, $s_name, $s_key, %selected); #selected�յ���
	my ($c_flg, $c_name, $c_key, %checked);  #checked�յ���
	open TEMPLATE, "<$template" or &disp_error("�������̤Υƥ�ץ졼�ȥե�������ɤ߹��ߤ˼��Ԥ��ޤ�����");
	while(<TEMPLATE>){
		&jcode::convert(\$_, 'euc');

		#-- <SELECT>��selected�ξ���õ��
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

		#-- <input type="checkbox">,<input type="radio">��checked�ξ���õ��
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

		#-- HIDDEN�ͤ���ᤳ��(������䤳����)
		if($_ =~ /<form/i){ $h_flg = 1; }		# <form>�������Ϥ�1
		if($h_flg){
			if(0 <= (index "$_", "$MYSCRIPT")){ $h_flg = 2; }
								# ����CGI��Ƥ�Ǥ���2
			if($h_flg == 1){			# 1�Τޤ��Ĥ��Ƥ���
				if(0 <= (index "$_", '>')){ $h_flg = 0; }
								# ���֤�0���᤹
			}elsif($h_flg == 2){			# 2�ξ��֤��Ĥ��Ƥ���
				$_ =~ s/>/>\n<input type=\"hidden\" name=\"form_step_check\" value=\"$next_step\">\n$input_hidden/o;
								# HIDDEN�ͤ��������
				$h_flg = 0;			# ���֤�0���᤹
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
# text  : check.txt�˽��ä��������Ƥγ�ǧ
# return: �֤��ͤʤ�
#-----------------------------------------------------------------------
sub check_input_data {
	my (@check, $name, $item, $requir, $type, $num, $value, %unique, @error);
	my (%choice, @groups, $error);
	#-- ɬ�ܹ��ܥ����å��ʤ�
	open CHECK, "<check.txt" or &disp_error("���ϥ����å�����ե����뤬�ɤߤ���ޤ���");
	@check = <CHECK>;
	close CHECK;
	foreach (@check){
		&jcode::convert(\$_, 'euc');
		if(0 == (index "$_", '#')){ next; }		# �����ȹԤ����Ф�
		chomp;
		($name, $item, $require, $type, $num, $group) = split /\t/;
		$value = $IN{"$name"};
		$item{"$name"} = $item;
		++$name{"$name"};

		#-- �ͤκǸ�˲��Ԥ����äѤ�������Ͼä��Ƥ���
		while($value =~ /\x0D\x0A$/){ chomp $value; }

		#-- �ͤγ�ǧ
		if($value eq ''){ # ��0�פ����Ϥ��̤�
			#-- ɬ�����ϤΥ����å�(orɬ��)
			if($require eq 'or' and $group){
				#-- ���Ϥ��ʤ���¾�ˤ����Ϥ��ʤ�����
				unless($choice{"$group"}){
					if((index $error, "<!--$group-->") < 0){
						$error .= "<!--$group-->$item ��ɤ줫����������������<BR>\n";
					}
				}
			#-- ɬ�����ϤΥ����å�(����ɬ��)
			}elsif($require){
				unless($group and $unique{"$group"}){
					$error .= "$item �����Ϥ���������<BR>\n";
					++$unique{"$group"};
				}
			}
		}else{
			#-- ɬ�����ϤΥ����å�(orɬ��) ���Ϥ�����гФ��Ƥ���
			if($require eq 'or' and $group){ ++$choice{"$group"}; }
			#-- Ⱦ�ѿ����Υ����å�( , - ���̤�)
			if($type eq '1' and $value =~ /[^0-9\,\-]/){
				$error .= "$item ��Ⱦ�ѿ����Ǥ����Ϥ���������<BR>\n";
			#-- Ⱦ�ѱѿ��Υ����å�
			}elsif($type eq 'a' and $value =~ /\W/){
				$error .= "$item ��Ⱦ�ѱѿ��Ǥ����Ϥ���������<BR>\n";
			#-- �᡼������Υ����å�
			}elsif($type eq 'e' and $value !~ /^[_0-9a-zA-Z\.\-\/]+\@\S+\.[a-zA-Z][a-zA-z][a-zA-Z]*$/){
				$error .= "$item �������������Ϥ���������<BR>\n";
			#-- �����ϤΥ����å�
			}elsif($type and $name{"$type"} and $IN{"$type"} ne $IN{"$name"}){
				$error .= "$item �� $item{$type} ��Ʊ�����Ƥ����Ϥ��Ƥ���������<BR>\n";
			}
			#-- ʸ�����Υ����å�
			if($num and $num < length($value)){
				$error .= "$item ��Ⱦ��$numʸ���ʲ��Ǥ����Ϥ���������<BR>\n";
			}
		}
	}

	#-- �Ǹ��ɬ������(orɬ��)�����Ϥ������Τϥ��顼�������
	@groups = keys %choice;
	foreach $group (@groups){
		$error =~ s/<!--$group-->[^\<]*<BR>\n//;
	}

	if($error){					# ���顼�������
#		&jcode::convert(\$error, 'euc');
		$IN{'error'} = $error;
		&read_template("$TEMPLATE1", "1");	# ���ϲ��̺�ɽ��
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
# call  : &disp_error('ɽ�������ȥ�', '��å�����');
# text  : Ϳ����줿�����ȥ�ȥ�å�������ɽ������
# return: �֤��ͤʤ�
#-----------------------------------------------------------------------
sub disp_error {
	my $title = shift;
	my $message = shift;
	if($title and !$message){
		$message = $title;
		$title = '���顼��å�����';
	}
	print "$nHEADER";
	if($nCAREER ne 'e'){
		&disp_header("$title");
		print <<"END";
<div align="center">
<table border="0" width="450" cellpadding="2" cellspacing="1">
 <tr><td class="td">$message</td></tr>
</table><BR> <BR> <BR>
[<A HREF=JavaScript:history.back()>���</A>]
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
# text  : setting.pl��������˽��äƥǡ�������¸
# return: �֤��ͤʤ�
#-----------------------------------------------------------------------
sub save_data {
	my ($data, $lfh, @filelist, $data_temp);
	my $flag = 0;  #<-- $flag=0;�����Τ�������뤳�ȡ�

	#-- �ե������¸�߳�ǧ
	opendir DIR, $DATA_DIR;
  	@filelist = readdir DIR;
	closedir DIR;
	foreach (@filelist) {
		if(/^$sFILE_NAME(\d*)/) { $flag = 1; last; }
	}
	#-- ��¸�ե�������å��ե������̵���ä���ե��������
	unless($flag){
		if(@DATA_HEADER){
			$data = ();
			foreach (@DATA_HEADER){ $data .= "$_$T"; }
		}
		open DATA, ">$DATA_DIR/$sFILE_NAME" or &disp_error("�ǡ�������¸���뤳�Ȥ��Ǥ��ޤ���<!--1a-->");
		if($data){
			&jcode::convert(\$data, "sjis");
			print DATA "$data\n";
		}
		close DATA;
		chmod 0666, "$DATA_DIR/$sFILE_NAME";
	}

	#-- ���������̾����¸����
	$data = ();
	@data_name_temp = @DATA_NAME;
	foreach $data_temp (@data_name_temp){
		$data_temp =~ s/\$([a-zA-Z0-9_]+)/$IN{"$1"}/g;
		$data .= "$data_temp$T";
	}
	$data =~ tr/\x0D\x0A//d;			# ���ԥ����ɺ��
	&jcode::convert(\$data, "sjis");

	# ��å��������� $lfh�ϲ������
	require 'filelock.pl';				# �ե������å����ɹ�
	$lfh = &filelock($DATA_DIR, $sFILE_NAME);
	open DATA, ">>$lfh->{current}" or &disp_error("�ǡ�������¸���뤳�Ȥ��Ǥ��ޤ���<!--1b-->");
	print DATA "$data\n";
	close DATA;

	&fileunlock($lfh);				# ��å����
	$lfh = ();
}


#-----------------------------------------------------------------------
# call  : &save_data2;
# text  : setting.pl��������˽��äƥǡ�������¸��ͽ����¸�ѡ�
# return: �֤��ͤʤ�
#-----------------------------------------------------------------------
sub save_data2 {
	my ($data, $lfh, @filelist, $data_temp);
	my $flag = 0;  #<-- $flag=0;�����Τ�������뤳�ȡ�

	#-- �ե������¸�߳�ǧ
	opendir DIR, $DATA_DIR2;
  	@filelist = readdir DIR;
	closedir DIR;
	foreach (@filelist) {
		if(/^$sFILE_NAME(\d*)/) { $flag = 1; last; }
	}
	#-- ��¸�ե�������å��ե������̵���ä���ե��������
	unless($flag){
		if(@DATA_HEADER2){
			$data = ();
			foreach (@DATA_HEADER2){ $data .= "$_$T"; }
		}
		open DATA, ">$DATA_DIR2/$sFILE_NAME2" or &disp_error("�ǡ�������¸���뤳�Ȥ��Ǥ��ޤ���<!--2a-->");
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
	$data =~ tr/\x0D\x0A//d;			# ���ԥ����ɺ��
	&jcode::convert(\$data, "sjis");

	# ��å��������� $lfh�ϲ������
	require 'filelock.pl';				# �ե������å����ɹ�
	$lfh = &filelock($DATA_DIR2, $sFILE_NAME2);
	open DATA, ">>$lfh->{current}" or &disp_error("�ǡ�������¸���뤳�Ȥ��Ǥ��ޤ���<!--2b-->");
	print DATA "$data\n";
	close DATA;
	&fileunlock($lfh);				# ��å����
	$lfh = ();
}


#-----------------------------------------------------------------------
# call  : &make_mail_header;
# text  : sendmail��ɽ�����뤿��Υ᡼��إå����κ���
# return: �����Х��ѿ��ˤ���Τ��֤��ͤʤ�
#-----------------------------------------------------------------------
sub make_mail_header {
	#-- �᡼��Υإå�����ʬ�κ���
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
	require 'mimew.pl';				# mimew.pl���ɤߤ���
}


#-----------------------------------------------------------------------
# call  : &send_email_admin;
# text  : �����԰��᡼�������
# return: �֤��ͤʤ�
#-----------------------------------------------------------------------
sub send_email_admin{
	my ($mail_data, $from, $to, $subject);
	my $to_address = $ADMIN_TO;
	#-- �����Ԥ˥᡼�������

	#-- From��ʬ����
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
	#-- �᡼����ʸ����
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
# text  : �桼�������᡼�������
# return: �֤��ͤʤ�
#-----------------------------------------------------------------------
sub send_email_user{
	my ($mail_data, $from);
	#-- �桼�����˥᡼�������

	#-- From��ʬ����
	$from = "From: $USER_FROM_NAME <$sUSER_FROM_EMAIL>";
	&jcode::convert(\$from, 'jis');
	$from = &mimeencode($from);
	#-- �᡼����ʸ����
	$mail_data = &read_template("$USER_MAIL");
	$mail_data =~ s/<BR>/\n/gi;
	&jcode::convert(\$mail_data, 'jis');
	&jcode::convert(\$USER_SUBJECT, 'jis');
	$to = $IN{'email'};
	$subject = $USER_SUBJECT;
	&mail($sMAIL_HEADER, $from, $to, $subject, $mail_data);
}


#-----------------------------------------------------------------------
# call  : &mail('�إå���','From','������Email','Subject','��ʸ');
# text  : �ºݤΥ᡼����������
# return: �֤��ͤʤ�
#-----------------------------------------------------------------------
sub mail{
	#-- �᡼��������������ʬ
	my $mail_header = shift;
	my $from        = shift;
	my $to          = shift;
	my $subject     = shift;
	my $mail_data   = shift;

	if($MAILMETHOD == 2){
		open MAIL, "|$SENDMAIL -t" or &disp_error('�����˼��Ԥ��ޤ�����');
		print MAIL "$mail_header";
		print MAIL "$from\n";
		print MAIL "To: $to\n";
		print MAIL "Subject: $subject\n";
		print MAIL "\n";
		print MAIL "$mail_data";
		close MAIL;
	}elsif($MAILMETHOD == 1){
		my $sock_stream = 1 ;	#-- ������ʬ��ư���ʤ�����2
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
# call  : &syswr('��');
# text  : SMTP����������Ȥ���ͽ���ؿ�
# return: �֤��ͤʤ�
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
# call  : &disp_header('�����ȥ�', '��ե�å��夹�����URL');
# text  : ��CGI�ǽ��Ϥ���HTML(��λ���̤ʤɤ�)�إå���
# return: �֤��ͤʤ�
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
# text  : ��CGI�ǽ��Ϥ���HTML�եå���(copyright�ʤ�ɽ��)
# return: �֤��ͤʤ�
#-----------------------------------------------------------------------
sub disp_footer{
	### copyrightɽ��(�ѹ��Բ�)�ۤȤ�ɻȤ��ޤ���͡�������
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
# text  : �ѡ���������������Ⱦ���ִ������˥������󥰤⤪���ʤ���
# return: (*IN)�Ȼ��ꤹ���%IN�˳�Ǽ����롣�����Х�ʤΤǡ��֤��ͤʤ�
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

		#-- ���˥������󥰽���
#		$value =~ s/&/&amp;/g; # �����ػ�
#		$value =~ s/"/&quot;/g;
#		$value =~ s/</&lt;/g;
#		$value =~ s/>/&gt;/g;

		$value =~ s/&/��/g; # �����ػ�
		$value =~ s/"/��/g;
		$value =~ s/</��/g;
		$value =~ s/>/��/g;
		$value =~ s/,/��/g;
		$value =~ s/��BR��/<BR>/ig;

		#-- ��Ⱦ���ִ�
		if($Z_TO_H){
			&jcode::tr(\$value, '��-����-�ڣ�-��', '0-9A-Za-z'); 
			&jcode::tr(\$value, '���ʡˡ����ݡ���', ' ()_@-.,');
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
# text  : �ե����륢�åץ���ͭ��Υѡ����������������˥������󥰡�
# return: ����Ū��%IN�˳�Ǽ����롣�֤��ͤʤ���
#-----------------------------------------------------------------------
sub read_stdin{
	my ($buf, $read_data, $remain, @headers, $delimiter, $up_file_name, $name, $i);

	#-- ɸ�����Ϥ���ǡ������ɤߤ���
	$buf = "";
	$read_data = "";
	$remain = $ENV{'CONTENT_LENGTH'};
	binmode(STDIN);
	while($remain){
		$remain -= sysread(STDIN, $buf, $remain);
		$read_data .= $buf;
	}

	#-- �إå�����
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
				$headers[$i] =~ s/&/��/g; # �����ػ�
				$headers[$i] =~ s/"/��/g;
				$headers[$i] =~ s/</��/g;
				$headers[$i] =~ s/>/��/g;
				$headers[$i] =~ s/,/��/g;
				$headers[$i] =~ s/��BR��/<BR>/ig;
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

	#-- ��¸����ե�����̾�ȳ�ĥ�Ҥγ�ǧ
	my @ext = ('jpg', 'jpeg', 'gif', 'bmp');
	for($i = 0; $ext[$i]; ++$i){
		if($up_file_name =~ /$ext[$i]$/){
			$ext_ok = 1;
			last;
		}
	}
	if($up_file_name){
		#-- �ե����륵�����γ�ǧ
		$size = length($IN{'file'});

		unless($ext_ok){
			$error .= "ź�դ��줿�ե�����η����ϵ��Ĥ���Ƥ��ޤ���<BR>";
		}

		#-- ��񤭤γ�ǧ
		if($FILE_UPDATE){
			if( -e "$DATA_DIR/$up_file_name"){
				$error .= "Ʊ��̾���Υե����뤬¸�ߤ��Ƥ��ޤ���<BR>";
			}
		}

		if($ZERO_BYTE){
			unless($size){
				$error .= "0byte�Υե�����ϥ��åץ��ɤǤ��ޤ���";
			}
		}

		if($SIZE_MAX){
			if($SIZE_MAX < $size){
				$error .= "���åץ��ɤǤ���ե�����κ��祵������ $SIZE_MAX byte �ޤǤǤ���";
			}
		}

		if($up_file_name =~ /[^A-Za-z0-9-_.]/){
			$error .= "���åץ��ɤ���ե�����̾��Ⱦ�ѱѿ��Ǥ����꤯��������";
		}

		unless($error){
			#-- ����ʤ���Хե��������¸
			open OUT, ">$DATA_DIR/$up_file_name" or &disp_error("�ե��������¸�˼��Ԥ��ޤ���");
			binmode(OUT);
			print OUT "$IN{'file'}";
			close(OUT);
			undef $IN{'file'};
			chmod 0666, "$DATA_DIR/$up_file_name";
			$IN{'file_url'} = "$DATA_DIR_URL/$up_file_name";
		}
	}
}
