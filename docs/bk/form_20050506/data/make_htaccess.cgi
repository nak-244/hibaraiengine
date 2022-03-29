#!/usr/local/bin/perl
############################################
#
#	名  前：make_htaccess.cgi
#	制  作：sun-system co.ltd 松本竜太(著作権保有)
#	説  明：2003/1/15 制作 .htaccessにてアクセス制限をするためのツール
#	使い方：設置して実行するのみ
#	        use Cwdが使えないサーバーでは動作しない可能性があります。
#
#############################


### パスワードファイル名の指定
$passwordfile = 'pass.txt';

### 最大何組のID＆PASSを設定できるようにするか
$max_pair = 10;

### このCGI名
$myscript = 'make_htaccess.cgi';

### 主に使う色コード
$color= '#adadf8';


######
# メイン
###
&parse_form_data( *IN );
use Cwd;
$dir = cwd();				# サーバーのルートからのパスを得る

unless($IN{'mode'}){
	&check_htaccess_file;
	&disp_top_menu;			# トップメニューの表示
}elsif($IN{'mode'} eq 'input'){
	&disp_input_data;		# 情報入力画面の表示
}elsif($IN{'mode'} eq 'save'){
	&save_htaccess;
}elsif($IN{'mode'} eq 'disp_htaccess'){
	&disp_htaccess;
}elsif($IN{'mode'} eq 'delete_htaccess1'){
	&delete_htaccess1;
}elsif($IN{'mode'} eq 'delete_htaccess2'){
	&delete_htaccess2;
}else{
	&disp_error("このCGIは正しく呼び出されていません。");
}
exit; 


#-----------------------------------------------------------------------
sub check_htaccess_file{
	if( -e './.htaccess'){
		chmod 0666, './.htaccess';
		open FILE, '<./.htaccess' or &disp_error('既存の.htaccessファイルを確認することができません。');
		my $line = <FILE>;
		close FILE;
		#-- 既存の.htaccessファイルがあった場合、このCGIで書いたものか確認
		if((index $line, "write by $myscript") < 0){
			&disp_top_menu('本CGI以外ですでに作成された.htaccessがあります。<BR>現バージョンでは編集することができません。<BR>確認の上、問題なければ削除して再度実行してください。');
		}
	}
}


#-----------------------------------------------------------------------
sub disp_top_menu{
	my $message = shift;
	print "Content-type: text/html\n\n";
	&disp_header("トップメニュー");
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
   ■BASIC認証の設定<BR>
  </td>
  <td width="50">
   <input type="submit" value="実行する">
  </td>
 </tr>
</table>
</form>
END
	}else{
		print <<"END";
<table border="0">
 <tr>
  <td style="color: #666666; font-size: 10pt">.htaccessがある場合は、安全のため、設定ができないようになっています。<BR>削除してから設定をおこないます。</td>
 </tr>
</table><BR>

<form action="$myscript" method="POST">
<input type="hidden" name="mode" value="disp_htaccess">
<table border="0" width="450" cellpadding="2">
 <tr>
  <td class="td" style="font-size: 10pt" bgcolor="$color">
   ■.htaccessの表示
  </td>
  <td width="50">
   <input type="submit" value="実行する">
  </td>
 </tr>
</table>
</form>

<form action="$myscript" method="POST">
<input type="hidden" name="mode" value="delete_htaccess1">
<table border="0" width="450" cellpadding="2">
 <tr>
  <td class="td" style="font-size: 10pt" bgcolor="$color">
   ■.htaccessの削除
   <div align="right">
   <table border="0" cellpadding="2" width="100%">
    <tr>
     <td class="td" style="font-size: 10pt" bgcolor="#ffffff">
削除したファイルはbackup.htaccessとして保存されます。<BR>
修復はftpやtelnetを利用する必要があります。<BR>
注意しておこなってください。
     </td>
    </tr>
   </table>
   </div>
  </td>
  <td width="50">
   <input type="submit" value="実行する">
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
  <td class="td" bgcolor="$color">設定するディレクトリのルートからのパス</td>
 </tr>
 <tr>
  <td class="td" style="color: #666666">
   <input name="dir" value="$dir_text" size="40"><BR>
   ※この欄に初期値で値が入っている場合は本CGIが設置されているディレクトリです。変更の必要はありません。
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
  <td class="td" bgcolor="$color">BASIC認証のウィンドウに表示させる文字列</td>
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
  <td class="td" bgcolor="$color">.htaccessとパスワードファイルのパーミッション設定</td>
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
  <td class="td" bgcolor="$color">.htaccessとパスワードファイルの表示許可</td>
 </tr>
 <tr>
  <td class="td">
   <input type="radio" name="disp" value="no" selected>表示しない /
   <input type="radio" name="disp" value="yes">表示する<BR>
  </td>
 </tr>
</table><BR>


<table border="1" width="380" cellpadding="2">
 <tr>
  <td class="td" bgcolor="$color">初期表示ファイル</td>
 </tr>
 <tr>
  <td class="td" style="color: #666666">
   <input name="dir_index" value="$IN{'dir_index'}" size="30"><BR>
   index.html以外を初期表示ページに指定する場合は指定します。
  </td>
 </tr>
</table><BR>
-->

<input type="submit" value="設定する">
</form>

<a href="$myscript">トップメニューに戻る</a><BR> <BR>
</div>
END
	&disp_footer;
	exit;
}


#-----------------------------------------------------------------------
sub save_htaccess {
	my ($id, $pass, $crypt_pass, $error, $pass_data, $set);

	unless( -e "$IN{'dir'}/$myscript"){
		$error .= "設定するディレクトリのルートからのパスは$myscriptのあるパスしか指定できません。<BR>";
	}

	for($i = 1; $i <= $max_pair; ++$i){
		$id   = $IN{"id_$i"};
		$pass = $IN{"pass_$i"};
		if($id){
			if($id =~ /\W/){
				$error .= "$i組はIDが正しくありません。<BR>\n";
			}elsif(16 <= length($id)){
				$error .= "$i組はIDが長すぎます。<BR>\n";
			}elsif(!$pass){
				$error .= "$i組はパスワードが指定されていません。\n";
			}elsif($pass =~ /\W/){
				$error .= "$i組はパスワードが正しくありません。\n";
			}elsif(16 <= length($pass)){
				$error .= "$i組はパスワードが長すぎます。<BR>\n";
			}
			$crypt_pass = crypt($IN{"pass_$i"}, $IN{"id_$i"});
			$pass_data .= "$id:$crypt_pass\n";
			$set = 1;
		}
		$id = $pass = ();
	}
	if($IN{'dir_index'}){
		unless( -e "$IN{'dir_index'}"){
			$error .= "初期表示ファイルに設定された$IN{'dir_index'}は存在しません。<BR>\n";
		}
	}

	if($error){ &disp_input_data("$error"); }

	#-- パスワードファイルの保存
	if($set){
		open PASS, ">./$passwordfile" or &disp_error('パスワードファイルを作成できませんでした。');
		print PASS "$pass_data";
		close PASS;
		chmod 0666, "./$passwordfile";
	}

	#-- .htaccessファイルの保存
	open FILE, '>./.htaccess' or &disp_error('.htaccessを作成できませんでした。');
	print FILE <<"END";
# write by $myscript
END

	#-- アクセス制限部分の指定
	if($set){
		print FILE <<"END";
AuthUserFile $dir/$passwordfile
AuthGroupFile /dev/null
AuthName "$IN{'basic_text'}"
AuthType Basic
require valid-user
END
	}

	#-- .htaccessファイルの表示/非表示の指定
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

	#-- 初期表示ページの指定
	if($IN{'dir_index'}){
		print FILE <<"END";
DirectoryIndex $IN{'dir_index'}
END
	}
	close FILE;

	#-- .htaccessのパーミッションの指定
	if($IN{'permit'} eq '0644'){
		chmod 0644, '.htaccess';
		chmod 0644, "$passwordfile";
	}elsif($IN{'permit'} eq '0666'){
		chmod 0666, '.htaccess';
		chmod 0666, "$passwordfile";
	}
	&disp_complete('設定が完了いたしました。');
}


#-----------------------------------------------------------------------
sub disp_htaccess {
	unless( -e './.htaccess'){
		&disp_error('表示しようとしている.htaccessファイルが見つかりません。');
	}
	open FILE, './.htaccess' or &disp_error('.htaccessファイルを開くことができません。');
	while(<FILE>){
		chomp;
		$htaccess_text .= "$_\n";		# text用データ
		$_ =~ s/&/&amp;/g;
		$_ =~ s/"/&quot;/g;
		$_ =~ s/</&lt;/g;
		$_ =~ s/>/&gt;/g;
		$htaccess_html .= "$_<BR>\n";		# html用データ
	}
	close FILE;

	print "Content-type: text/html\n\n";
	&disp_header('.htaccessの内容表示');
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
<B>　# write by make_htaccess.cgi</B><BR>
このCGIで作った.htaccessか判別するためのコメント行です。<BR>
<hr size="1">
<B>　AuthUserFile</B><BR>
パスワードファイルの指定です。この指定は、サーバのルートからのフルパスで記述されていなければなりません。<BR>
<hr size="1">
<B>　AuthName</B><BR>
Basic認証をかける領域名の指定です。<BR>
&quot;（ダブルクォート）で囲まれた部分は、パスワード入力時に表示される文字列で、変更が可能です。
<hr size="1">
<B>　&lt;Files ~ &quot;^(\.htaccess|$passwordfile)\$&quot;&gt;</B><BR>
<B>　　deny from all</B><BR>
<B>　&lt;/Files&gt;</B><BR>
.htaccessやパスワードファイルの表示の有無を指定します。<BR>
表示が&quot;allow&quot;、非表示が&quot;deny&quot;になります。
<hr size="1">
<B>　require valid-user</B><BR>
パスワードファイルで照会して、認証に成功したユーザのみにアクセスを許可する、という意味です。<BR>
  </td>
 </tr>
</table><BR>


<a href="$myscript">トップメニューに戻る</a><BR> <BR>
</div>
END
	&disp_footer;
	exit;
}




#-----------------------------------------------------------------------
sub delete_htaccess1{
	unless( -e './.htaccess'){
		&disp_error('削除しようとしている.htaccessファイルが見つかりません。');
	}
	print "Content-type: text/html\n\n";
	&disp_header('.htaccessの削除確認画面');
	print <<"END";
<div align="center" style="font-size: 10pt">
このディレクトリにある .htaccess を削除しようとしています。<BR>
削除しても構いませんか？<BR> <BR>
削除する場合は【削除】ボタンを押してください。

<form aciton="$myscript" method="POST">
<input type="hidden" name="mode" value="delete_htaccess2">
<input type="submit" value="削除">
</form>

<a href="$myscript">トップメニューに戻る</a><BR> <BR>
</div>
END
	&disp_footer;
	exit;
}


#-----------------------------------------------------------------------
sub delete_htaccess2{
	unless( -e './.htaccess'){
		&disp_error('削除しようとしている.htaccessファイルが見つかりません。');
	}else{
		chmod 0666, './.htaccess';
#		unlink './.htaccess' or &disp_error('.htaccessファイルの削除に失敗しました。<BR>ファイルの操作権限がない可能性があります。');
		rename './.htaccess' => './backup.htaccess' or &disp_error('.htaccessファイルの削除に失敗しました。<BR>ファイルの操作権限がない可能性があります。');
		&disp_complete('.htaccessファイルをbackup.htaccessとしてファイル名を変更しました。', "$myscript");
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
<title>BASIC認証設定 $sub_title</title>
</head>
<div align="center">
<table border="0" width="450" cellpadding="4">
 <tr>
  <td style="font-size: 10pt" bgcolor="$color" align="center" class="td">BASIC認証設定 $sub_title</td>
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
	&disp_header("更新しました。", "$myscript");
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
ページが更新されない場合は、
<a href="$myscript">【こちら】</a>をクリックしてください。<BR>
リロードはしないでください。<BR>
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
  <th align="center" bgcolor="$color"> エラー画面</th>
 </tr>
</table><BR>

<table width="460" border="0">
 <tr>
  <td align="center">
   <div style="font-size: 10pt">$_[0]<BR>$_[1]<BR> <BR>
   戻る場合は<A HREF="JavaScript:history.back()">【こちら】</A>を押してください。
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

		$value =~ s/&/&amp;/g; # タグ禁止
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
