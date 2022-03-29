#!/usr/local/bin/perl
############################################
#
#	̾  ����make_htaccess.cgi
#	��  �sun-system co.ltd ����ε��(�����ͭ)
#	��  ����2003/1/15 ���� .htaccess�ˤƥ����������¤򤹤뤿��Υġ���
#	�Ȥ��������֤��Ƽ¹Ԥ���Τ�
#	        use Cwd���Ȥ��ʤ������С��Ǥ�ư��ʤ���ǽ��������ޤ���
#
#############################


### �ѥ���ɥե�����̾�λ���
$passwordfile = 'pass.txt';

### ���粿�Ȥ�ID��PASS������Ǥ���褦�ˤ��뤫
$max_pair = 10;

### ����CGI̾
$myscript = 'make_htaccess.cgi';

### ��˻Ȥ���������
$color= '#adadf8';


######
# �ᥤ��
###
&parse_form_data( *IN );
use Cwd;
$dir = cwd();				# �����С��Υ롼�Ȥ���Υѥ�������

unless($IN{'mode'}){
	&check_htaccess_file;
	&disp_top_menu;			# �ȥåץ�˥塼��ɽ��
}elsif($IN{'mode'} eq 'input'){
	&disp_input_data;		# �������ϲ��̤�ɽ��
}elsif($IN{'mode'} eq 'save'){
	&save_htaccess;
}elsif($IN{'mode'} eq 'disp_htaccess'){
	&disp_htaccess;
}elsif($IN{'mode'} eq 'delete_htaccess1'){
	&delete_htaccess1;
}elsif($IN{'mode'} eq 'delete_htaccess2'){
	&delete_htaccess2;
}else{
	&disp_error("����CGI���������ƤӽФ���Ƥ��ޤ���");
}
exit; 


#-----------------------------------------------------------------------
sub check_htaccess_file{
	if( -e './.htaccess'){
		chmod 0666, './.htaccess';
		open FILE, '<./.htaccess' or &disp_error('��¸��.htaccess�ե�������ǧ���뤳�Ȥ��Ǥ��ޤ���');
		my $line = <FILE>;
		close FILE;
		#-- ��¸��.htaccess�ե����뤬���ä���硢����CGI�ǽ񤤤���Τ���ǧ
		if((index $line, "write by $myscript") < 0){
			&disp_top_menu('��CGI�ʳ��Ǥ��Ǥ˺������줿.htaccess������ޤ���<BR>���С������Ǥ��Խ����뤳�Ȥ��Ǥ��ޤ���<BR>��ǧ�ξ塢����ʤ���к�����ƺ��ټ¹Ԥ��Ƥ���������');
		}
	}
}


#-----------------------------------------------------------------------
sub disp_top_menu{
	my $message = shift;
	print "Content-type: text/html\n\n";
	&disp_header("�ȥåץ�˥塼");
	print <<"END";
<div align="center">
END

	if($message){
		print <<"END";
<table border="0">
 <tr>
  <td style="color: #FF0000; font-size: 10pt">$message</td>
 </tr>
</table><BR>
END
	}

	unless( -e './.htaccess'){
		print <<"END";
<form action="$myscript" method="POST">
<input type="hidden" name="mode" value="input">
<table border="0" width="450" cellpadding="2">
 <tr>
  <td class="td" style="font-size: 10pt" bgcolor="$color">
   ��BASICǧ�ڤ�����<BR>
  </td>
  <td width="50">
   <input type="submit" value="�¹Ԥ���">
  </td>
 </tr>
</table>
</form>
END
	}else{
		print <<"END";
<table border="0">
 <tr>
  <td style="color: #666666; font-size: 10pt">.htaccess��������ϡ������Τ��ᡢ���꤬�Ǥ��ʤ��褦�ˤʤäƤ��ޤ���<BR>������Ƥ�������򤪤��ʤ��ޤ���</td>
 </tr>
</table><BR>

<form action="$myscript" method="POST">
<input type="hidden" name="mode" value="disp_htaccess">
<table border="0" width="450" cellpadding="2">
 <tr>
  <td class="td" style="font-size: 10pt" bgcolor="$color">
   ��.htaccess��ɽ��
  </td>
  <td width="50">
   <input type="submit" value="�¹Ԥ���">
  </td>
 </tr>
</table>
</form>

<form action="$myscript" method="POST">
<input type="hidden" name="mode" value="delete_htaccess1">
<table border="0" width="450" cellpadding="2">
 <tr>
  <td class="td" style="font-size: 10pt" bgcolor="$color">
   ��.htaccess�κ��
   <div align="right">
   <table border="0" cellpadding="2" width="100%">
    <tr>
     <td class="td" style="font-size: 10pt" bgcolor="#ffffff">
��������ե������backup.htaccess�Ȥ�����¸����ޤ���<BR>
������ftp��telnet�����Ѥ���ɬ�פ�����ޤ���<BR>
��դ��Ƥ����ʤäƤ���������
     </td>
    </tr>
   </table>
   </div>
  </td>
  <td width="50">
   <input type="submit" value="�¹Ԥ���">
  </td>
 </tr>
</table>
</form>
END
	}
	print <<"END";
</div>
END
	&disp_footer;
	exit;
}


#-----------------------------------------------------------------------
sub disp_input_data {
	my $error = shift;

	if($IN{'dir'}){ $dir_text = $IN{'dir'}; }
	else{ $dir_text = $dir; }

	if($IN{'basic_text'}){ $basic_text = $IN{'basic_text'}; }
	else{ $basic_text = 'Secret Area'; }

	print "Content-type: text/html\n\n";
	&disp_header;
	print <<"END";
<div align="center" style="font-size: 10pt">
END
	if($error){
		print <<"END";
<table border="0">
 <tr>
  <td style="color: #FF0000" style="font-size: 10pt">$error</td>
 </tr>
</table><BR>
END
	}
	print <<"END";
<form action="$myscript" method="POST">
<input type="hidden" name="mode" value="save">
<table border="1" width="380" cellpadding="2">
 <tr>
  <td class="td" bgcolor="$color">���ꤹ��ǥ��쥯�ȥ�Υ롼�Ȥ���Υѥ�</td>
 </tr>
 <tr>
  <td class="td" style="color: #666666">
   <input name="dir" value="$dir_text" size="40"><BR>
   ��������˽���ͤ��ͤ����äƤ��������CGI�����֤���Ƥ���ǥ��쥯�ȥ�Ǥ����ѹ���ɬ�פϤ���ޤ���
  </td>
 </tr>
</table><BR>
<table border="1" width="380" cellpadding="2">
 <tr bgcolor="$color">
  <td class="td" width="20">num</td>
  <td class="td" width="180">ID</td>
  <td class="td" width="180">PASS</td>
 </tr>
END
	$i = 0;
	while($i < $max_pair){
		++$i;
		$id   = $IN{"id_$i"};
		$pass = $IN{"pass_$i"};
		print <<"END";
 <tr>
  <td class="td" align="right">$i</td>
  <td class="td"><input name="id_$i" size="16" value="$id" size="30"></td>
  <td class="td"><input name="pass_$i" size="16" value="$pass" size="30"></td>
 </tr>
END
		$id = $pass = ();
	}
	print <<"END";
</table><BR>

<table border="1" width="380" cellpadding="2">
 <tr>
  <td class="td" bgcolor="$color">BASICǧ�ڤΥ�����ɥ���ɽ��������ʸ����</td>
 </tr>
 <tr>
  <td class="td" style="color: #666666">
   <input name="basic_text" value="$basic_text" size="40"><BR>
  </td>
 </tr>
</table><BR>


<input type="hidden" name="permit" value="0666">

<!--
<table border="1" width="380" cellpadding="2">
 <tr>
  <td class="td" bgcolor="$color">.htaccess�ȥѥ���ɥե�����Υѡ��ߥå��������</td>
 </tr>
 <tr>
  <td class="td">
   <input type="radio" name="permit" value="0644" selected>0644 /
   <input type="radio" name="permit" value="0666">0666<BR>
  </td>
 </tr>
</table><BR>

<table border="1" width="380" cellpadding="2">
 <tr>
  <td class="td" bgcolor="$color">.htaccess�ȥѥ���ɥե������ɽ������</td>
 </tr>
 <tr>
  <td class="td">
   <input type="radio" name="disp" value="no" selected>ɽ�����ʤ� /
   <input type="radio" name="disp" value="yes">ɽ������<BR>
  </td>
 </tr>
</table><BR>


<table border="1" width="380" cellpadding="2">
 <tr>
  <td class="td" bgcolor="$color">���ɽ���ե�����</td>
 </tr>
 <tr>
  <td class="td" style="color: #666666">
   <input name="dir_index" value="$IN{'dir_index'}" size="30"><BR>
   index.html�ʳ�����ɽ���ڡ����˻��ꤹ����ϻ��ꤷ�ޤ���
  </td>
 </tr>
</table><BR>
-->

<input type="submit" value="���ꤹ��">
</form>

<a href="$myscript">�ȥåץ�˥塼�����</a><BR> <BR>
</div>
END
	&disp_footer;
	exit;
}


#-----------------------------------------------------------------------
sub save_htaccess {
	my ($id, $pass, $crypt_pass, $error, $pass_data, $set);

	unless( -e "$IN{'dir'}/$myscript"){
		$error .= "���ꤹ��ǥ��쥯�ȥ�Υ롼�Ȥ���Υѥ���$myscript�Τ���ѥ���������Ǥ��ޤ���<BR>";
	}

	for($i = 1; $i <= $max_pair; ++$i){
		$id   = $IN{"id_$i"};
		$pass = $IN{"pass_$i"};
		if($id){
			if($id =~ /\W/){
				$error .= "$i�Ȥ�ID������������ޤ���<BR>\n";
			}elsif(16 <= length($id)){
				$error .= "$i�Ȥ�ID��Ĺ�����ޤ���<BR>\n";
			}elsif(!$pass){
				$error .= "$i�Ȥϥѥ���ɤ����ꤵ��Ƥ��ޤ���\n";
			}elsif($pass =~ /\W/){
				$error .= "$i�Ȥϥѥ���ɤ�����������ޤ���\n";
			}elsif(16 <= length($pass)){
				$error .= "$i�Ȥϥѥ���ɤ�Ĺ�����ޤ���<BR>\n";
			}
			$crypt_pass = crypt($IN{"pass_$i"}, $IN{"id_$i"});
			$pass_data .= "$id:$crypt_pass\n";
			$set = 1;
		}
		$id = $pass = ();
	}
	if($IN{'dir_index'}){
		unless( -e "$IN{'dir_index'}"){
			$error .= "���ɽ���ե���������ꤵ�줿$IN{'dir_index'}��¸�ߤ��ޤ���<BR>\n";
		}
	}

	if($error){ &disp_input_data("$error"); }

	#-- �ѥ���ɥե��������¸
	if($set){
		open PASS, ">./$passwordfile" or &disp_error('�ѥ���ɥե����������Ǥ��ޤ���Ǥ�����');
		print PASS "$pass_data";
		close PASS;
		chmod 0666, "./$passwordfile";
	}

	#-- .htaccess�ե��������¸
	open FILE, '>./.htaccess' or &disp_error('.htaccess������Ǥ��ޤ���Ǥ�����');
	print FILE <<"END";
# write by $myscript
END

	#-- ��������������ʬ�λ���
	if($set){
		print FILE <<"END";
AuthUserFile $dir/$passwordfile
AuthGroupFile /dev/null
AuthName "$IN{'basic_text'}"
AuthType Basic
require valid-user
END
	}

	#-- .htaccess�ե������ɽ��/��ɽ���λ���
#	if($IN{'set'}){
#		print FILE <<"END";
#<Files ~ \"\^(\.htaccess\|$passwordfile)\$\">
#END
#	}else{
#		print FILE <<"END";
#<Files ~ \"\^\.htaccess\$\">
#END
#	}
#	if($IN{'disp'} eq 'no'){ print FILE "    deny from all\n"; }
#	else{ print FILE "    allow from all\n"; }
#	print FILE "</Files>\n";

	#-- ���ɽ���ڡ����λ���
	if($IN{'dir_index'}){
		print FILE <<"END";
DirectoryIndex $IN{'dir_index'}
END
	}
	close FILE;

	#-- .htaccess�Υѡ��ߥå����λ���
	if($IN{'permit'} eq '0644'){
		chmod 0644, '.htaccess';
		chmod 0644, "$passwordfile";
	}elsif($IN{'permit'} eq '0666'){
		chmod 0666, '.htaccess';
		chmod 0666, "$passwordfile";
	}
	&disp_complete('���꤬��λ�������ޤ�����');
}


#-----------------------------------------------------------------------
sub disp_htaccess {
	unless( -e './.htaccess'){
		&disp_error('ɽ�����褦�Ȥ��Ƥ���.htaccess�ե����뤬���Ĥ���ޤ���');
	}
	open FILE, './.htaccess' or &disp_error('.htaccess�ե�����򳫤����Ȥ��Ǥ��ޤ���');
	while(<FILE>){
		chomp;
		$htaccess_text .= "$_\n";		# text�ѥǡ���
		$_ =~ s/&/&amp;/g;
		$_ =~ s/"/&quot;/g;
		$_ =~ s/</&lt;/g;
		$_ =~ s/>/&gt;/g;
		$htaccess_html .= "$_<BR>\n";		# html�ѥǡ���
	}
	close FILE;

	print "Content-type: text/html\n\n";
	&disp_header('.htaccess������ɽ��');
	print <<"END";
<div align="center" style="font-size: 10pt">
<table border="1" width="200" cellpadding="4" cellspacing="6">
 <tr>
  <td class="td" bgcolor="#99CCFF">
$htaccess_html\n
<!--
$htaccess_text
-->
  </td>
 </tr>
</table><BR> <BR>


<div align="center" style="font-size: 10pt">
<table border="1" width="400" cellpadding="4" cellspacing="2">
 <tr>
  <td class="td" bgcolor="#eeeeee">
<B>��# write by make_htaccess.cgi</B><BR>
����CGI�Ǻ�ä�.htaccess��Ƚ�̤��뤿��Υ����ȹԤǤ���<BR>
<hr size="1">
<B>��AuthUserFile</B><BR>
�ѥ���ɥե�����λ���Ǥ������λ���ϡ������ФΥ롼�Ȥ���Υե�ѥ��ǵ��Ҥ���Ƥ��ʤ���Фʤ�ޤ���<BR>
<hr size="1">
<B>��AuthName</B><BR>
Basicǧ�ڤ򤫤����ΰ�̾�λ���Ǥ���<BR>
&quot;�ʥ��֥륯�����ȡˤǰϤޤ줿��ʬ�ϡ��ѥ�������ϻ���ɽ�������ʸ����ǡ��ѹ�����ǽ�Ǥ���
<hr size="1">
<B>��&lt;Files ~ &quot;^(\.htaccess|$passwordfile)\$&quot;&gt;</B><BR>
<B>����deny from all</B><BR>
<B>��&lt;/Files&gt;</B><BR>
.htaccess��ѥ���ɥե������ɽ����̵ͭ����ꤷ�ޤ���<BR>
ɽ����&quot;allow&quot;����ɽ����&quot;deny&quot;�ˤʤ�ޤ���
<hr size="1">
<B>��require valid-user</B><BR>
�ѥ���ɥե�����ǾȲ񤷤ơ�ǧ�ڤ����������桼���Τߤ˥�����������Ĥ��롢�Ȥ�����̣�Ǥ���<BR>
  </td>
 </tr>
</table><BR>


<a href="$myscript">�ȥåץ�˥塼�����</a><BR> <BR>
</div>
END
	&disp_footer;
	exit;
}




#-----------------------------------------------------------------------
sub delete_htaccess1{
	unless( -e './.htaccess'){
		&disp_error('������褦�Ȥ��Ƥ���.htaccess�ե����뤬���Ĥ���ޤ���');
	}
	print "Content-type: text/html\n\n";
	&disp_header('.htaccess�κ����ǧ����');
	print <<"END";
<div align="center" style="font-size: 10pt">
���Υǥ��쥯�ȥ�ˤ��� .htaccess �������褦�Ȥ��Ƥ��ޤ���<BR>
������Ƥ⹽���ޤ��󤫡�<BR> <BR>
���������ϡں���ۥܥ���򲡤��Ƥ���������

<form aciton="$myscript" method="POST">
<input type="hidden" name="mode" value="delete_htaccess2">
<input type="submit" value="���">
</form>

<a href="$myscript">�ȥåץ�˥塼�����</a><BR> <BR>
</div>
END
	&disp_footer;
	exit;
}


#-----------------------------------------------------------------------
sub delete_htaccess2{
	unless( -e './.htaccess'){
		&disp_error('������褦�Ȥ��Ƥ���.htaccess�ե����뤬���Ĥ���ޤ���');
	}else{
		chmod 0666, './.htaccess';
#		unlink './.htaccess' or &disp_error('.htaccess�ե�����κ���˼��Ԥ��ޤ�����<BR>�ե���������¤��ʤ���ǽ��������ޤ���');
		rename './.htaccess' => './backup.htaccess' or &disp_error('.htaccess�ե�����κ���˼��Ԥ��ޤ�����<BR>�ե���������¤��ʤ���ǽ��������ޤ���');
		&disp_complete('.htaccess�ե������backup.htaccess�Ȥ��ƥե�����̾���ѹ����ޤ�����', "$myscript");
	}
	exit;
}


#-----------------------------------------------------------------------
sub disp_header{
	my $sub_title = shift;
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
<META HTTP-EQUIV="Refresh" CONTENT="1;URL=$myscript?$IN{'query_string'}">
END
	}
	print <<"END";
<style>
.td { border-color: #CCCCCC #666666 #666666 #CCCCCC; border-style: solid; border-top-width: 1px; border-right-width: 1px; border-bottom-width: 1px; border-left-width: 1px; font-size: 10pt }
</style>
<title>BASICǧ������ $sub_title</title>
</head>
<div align="center">
<table border="0" width="450" cellpadding="4">
 <tr>
  <td style="font-size: 10pt" bgcolor="$color" align="center" class="td">BASICǧ������ $sub_title</td>
 </tr>
</table>
</div><BR>
END
}


#-----------------------------------------------------------------------
sub disp_footer{
	print <<"END";
<div align="center" style="font-size: 10pt">
<hr size="1" color="$color">
copyright(c) sun-co-ltd.com<BR>
</div>
</body>
</html>
END
}


#----------------------------------------------------------------------
sub disp_complete{
	my $message = shift;
	print "Content-type: text/html\n\n";
	&disp_header("�������ޤ�����", "$myscript");
	print <<"END";
<div align="center">
<BR> <BR> <BR>
<hr color="$color" width="450" size="1">
<div align="center" style="font-size: 10pt">$message</div>
<hr color="$color" width="450" size="1">
<BR> <BR> <BR>
<table border="0">
 <tr>
  <td style="font-size: 10pt">
�ڡ�������������ʤ����ϡ�
<a href="$myscript">�ڤ������</a>�򥯥�å����Ƥ���������<BR>
����ɤϤ��ʤ��Ǥ���������<BR>
  </td>
 </tr>
</table>
<BR> <BR> <BR>
</div>
END
	&disp_footer;
	exit;
}


#-----------------------------------------------------------------------
sub disp_error{
	print "Content-type: text/html\n\n";
	print <<"END";
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ja">
<HEAD>
<META http-equiv="content-type" content="text/html;charset=x-euc-jp">
<META http-equiv="Content-Style-Type" content="text/css">
<META http-equiv="Content-Script-Type" content="text/javascript">
<TITLE>$_[0]</TITLE>
<SCRIPT language="JavaScript">
<!--
function PageBack(){ history.back(); }
//-->
</SCRIPT>
</HEAD>
<body bgcolor="#FFFFFF">

<div align="center">
<table border="0" cellpadding="2" width="450">
 <tr>
  <th align="center" bgcolor="$color"> ���顼����</th>
 </tr>
</table><BR>

<table width="460" border="0">
 <tr>
  <td align="center">
   <div style="font-size: 10pt">$_[0]<BR>$_[1]<BR> <BR>
   ������<A HREF="JavaScript:history.back()">�ڤ������</A>�򲡤��Ƥ���������
   </div><BR> <BR> <BR>
  </td>
 </tr>
</table>
</div>
<BR> <BR> <BR>
END
	&disp_footer;
	exit;
}


#----------------------------------------------------------------------
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

		$value =~ s/&/&amp;/g; # �����ػ�
		$value =~ s/"/&quot;/g;
		$value =~ s/</&lt;/g;
		$value =~ s/>/&gt;/g;

		if( defined( $FORM_DATA{ $key }) ){
			$FORM_DATA{ $key } = join( "\0", $FORM_DATA{ $key }, $value );
		} else {
			$FORM_DATA{ $key } = $value;
		}
	}
}

exit;
