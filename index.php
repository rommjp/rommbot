<?php	

	$gmt_date=gmdate('Y-m-d', time());
	$start_date='2019-03-25';
	$my_robot_name='rommbot';
	$my_password='gamboa85';
	$table_html="";
	$r_activeRobots=[];
	$r_subscribedRobots_end_dates=[];
	$r_subscribedRobots_username=[];
	$activeRobots_display_names=[];
	$subscribedRobots_display_names=[];
	
	//Trade for me APIs
	$getSubscriptions="https://trade4.me/getSubscriptions.php?username={$my_robot_name}&password={$my_password}";
	$getActiveCopy="https://trade4.me/getActiveCopy.php?username={$my_robot_name}&password={$my_password}";
	$startCopy="https://trade4.me/startCopy.php?username={$my_robot_name}&password={$my_password}";
	$stopCopy="https://trade4.me/stopCopy.php?username={$my_robot_name}&password={$my_password}";
	$trade4me_members_url="https://trade4.me/members/";
	
	echo gmdate('D, d M Y H:i:s T', time()).'<br>';
	echo 'Start date: '.$start_date.'<br>';
	echo "Logged in as {$my_robot_name} <br>";
	
	/**
	 * Get a web file (HTML, XHTML, XML, image, json etc.) from a URL.  Return an
	 * array containing the HTTP server response header fields and content.
	 */
	function get_data_from_trade4me($url)
	{
		$options = array(
			CURLOPT_RETURNTRANSFER => true,     // return web page
			CURLOPT_HEADER         => false,    // don't return headers
			CURLOPT_FOLLOWLOCATION => true,     // follow redirects
			CURLOPT_ENCODING       => "",       // handle all encodings
			CURLOPT_USERAGENT      => "", 		// who am i
			CURLOPT_AUTOREFERER    => true,     // set referer on redirect
			CURLOPT_CONNECTTIMEOUT => 120,      // timeout on connect
			CURLOPT_TIMEOUT        => 120,      // timeout on response
			CURLOPT_MAXREDIRS      => 10,       // stop after 10 redirects
			CURLOPT_SSL_VERIFYPEER => false     // Disabled SSL Cert checks
		);

		$ch      = curl_init( $url );
		curl_setopt_array( $ch, $options );
		$content = curl_exec( $ch );
		$err     = curl_errno( $ch );
		$errmsg  = curl_error( $ch );
		$header  = curl_getinfo( $ch );
		curl_close( $ch );

		$header['errno']   = $err;
		$header['errmsg']  = $errmsg;
		$header['content'] = $content;
		return $header;
	}
	$table_html.="<br>
	<form method='post' action='https://trade4.me/wp-content/plugins/trade4me/includes/excel.php'>
						<input type='submit' class='exl-report btn btn-custom2' value='ROMMBOT EXPORT'>
						<input type='hidden' name='user_id' value='19257'>
						<input type='hidden' name='resetdate' value='2018-01-08 00:00:00'>
						<input type='hidden' name='monthbeforedate' value='2018-11-01'></form>
	
	<form method='post' action='https://trade4.me/wp-content/plugins/trade4me/includes/excel.php'>
							<input type='submit' class='exl-report btn btn-custom2' value='ROMMJP EXPORT'>
							<input type='hidden' name='user_id' value='8547'>
							<input type='hidden' name='resetdate' value='2018-01-08 00:00:00'>
							<input type='hidden' name='monthbeforedate' value='2018-11-01'>
	</form>";
				
	$activeRobots=json_decode(get_data_from_trade4me($getActiveCopy)['content']);
	$subscribedRobots=json_decode(get_data_from_trade4me($getSubscriptions)['content']);
		
	foreach($subscribedRobots as $provider){
		foreach ($provider as $user_name => $value){
			$r_subscribedRobots_username[$value->display_name]=$user_name;
			$r_subscribedRobots_end_dates[$value->display_name]=$value->end;
			array_push($subscribedRobots_display_names,$value->display_name);
		}
	}
	
	foreach($activeRobots as $user_name => $display_name){
		$r_activeRobots[$display_name]=$user_name;
		array_push($activeRobots_display_names,$display_name);
	}
	
	$link = mysqli_connect('localhost', 'root', 'gamboa85', 'binary_data');
	//$link = mysqli_connect('10.1.1.9', 'rommjp', 'gamboa85', 'binary_data');

	if (!$link) {
		$error = die("Connect Error: " . mysqli_connect_error());
	}
	
	$sql="select a.provider, ROUND((SUM(a.win_count)/SUM(a.num_of_trades))*100,1) as win_ratio, SUM(a.num_of_trades) as total_num_of_trades, SUM(a.win_count) as total_win_cnt, SUM(a.win_count) * 8.6 - 5 * SUM(a.num_of_trades) as profit_5  from trade_analysis a where a.close_date >= '{$start_date}'
		  group by a.provider
		  order by profit_5 desc";
		  
	$result = mysqli_query($link,$sql) or die(mysqli_error());
	
	$table_html.="<h3>Current Provider List</h3>
	<table>
	  <tr>
		<th>Position</th>
		<th>Status</th>
		<th>Display_name</th>
		<th>profit_5</th>
		<th>num_trades</th>
		<th>win_count</th>
		<th>winratio</th>
		<th>sub_end</th>
	  </tr>	
	  ";	
	$idx=1;  
	$win_ratio=0;
	$total_trades=0;
	$total_win_cnt=0;
	$profit_5=0;	  
		
	while ($row = mysqli_fetch_array($result)) {
		$status_string="";
		$sub_days="";
		$provider_url="";
		if (array_key_exists($row['provider'], $r_subscribedRobots_end_dates)) {
			$sub_days=$r_subscribedRobots_end_dates[$row['provider']];
		}
		
		if (in_array(trim($row['provider']), $activeRobots_display_names)){
			$status_string.='A';
		}	
		
		if (in_array(trim($row['provider']), $subscribedRobots_display_names)){
			if (strlen($status_string) > 0 ){
				$status_string.=',S';
			}else{
				$status_string.='S';
			}
		}
		
		if (in_array(trim($row['provider']), $subscribedRobots_display_names)){
			$provider_url=$trade4me_members_url.$r_subscribedRobots_username[$row['provider']]."/";
			$provider_link="<a href='{$provider_url}'>{$row['provider']}</a>";
		}else{
			$provider_link=$row['provider'];
		}
		
		$table_html.="
		  <tr>
			<td>{$idx}</td>
			<td>{$status_string}</td>
			<td>{$provider_link}</td>
			<td>{$row['profit_5']}</td>
			<td>{$row['total_num_of_trades']}</td>
			<td>{$row['total_win_cnt']}</td>
			<td>{$row['win_ratio']}</td>
			<td>{$sub_days}</td>
		  </tr>		
	  ";	  
	  $idx+=1;
	}
	
	$table_html.="</table><br>";
	
	$sql="select a.provider, ROUND((SUM(a.win_count)/SUM(a.num_of_trades))*100,1) as win_ratio, SUM(a.num_of_trades) as total_num_of_trades, SUM(a.win_count) as total_win_cnt, SUM(a.win_count) * 8.6 - 5 * SUM(a.num_of_trades) as profit_5  from rommbot_analysis a where a.close_date >= '{$start_date}'
		  group by a.provider
		  order by profit_5 desc";
		  
	$result = mysqli_query($link,$sql) or die(mysqli_error());
	
	$table_html.="<h3>Trade History</h3>
	<table>
	  <tr>
		<th>Position</th>
		<th>Status</th>
		<th>Display_name</th>
		<th>profit_5</th>
		<th>num_trades</th>
		<th>win_count</th>
		<th>winratio</th>
		<th>sub_end</th>
	  </tr>	
	  ";	
	$idx=1;  
	$total_win_ratio=0;
	$total_trades=0;
	$total_win_cnt=0;
	$profit_5=0;	  
	
	while ($row = mysqli_fetch_array($result)) {
		$total_trades+=$row['total_num_of_trades'];
		$total_win_cnt+=$row['total_win_cnt'];
		$profit_5+=$row['profit_5'];	
		$status_string="";
		$sub_days="";
		$provider_url="";
		
		if (array_key_exists(trim($row['provider']), $r_subscribedRobots_end_dates)) {
			$sub_days=$r_subscribedRobots_end_dates[trim($row['provider'])];
		}		
		
		if (in_array(trim($row['provider']), $activeRobots_display_names)){
			$status_string.='A';
		}	
		
		if (in_array(trim($row['provider']), $subscribedRobots_display_names)){
			if (strlen($status_string) > 0 ){
				$status_string.=',S';
			}else{
				$status_string.='S';
			}
		}
		
		if (in_array(trim($row['provider']), $subscribedRobots_display_names)){
			$provider_url=$trade4me_members_url.$r_subscribedRobots_username[trim($row['provider'])]."/";
			$provider_link="<a href='{$provider_url}'>{$row['provider']}</a>";
		}else{
			$provider_link=$row['provider'];
		}		
		
		$table_html.="
		  <tr>
			<td>{$idx}</td>
			<td>{$status_string}</td>
			<td>{$provider_link}</td>
			<td>{$row['profit_5']}</td>
			<td>{$row['total_num_of_trades']}</td>
			<td>{$row['total_win_cnt']}</td>
			<td>{$row['win_ratio']}</td>
			<td>{$sub_days}</td>
		  </tr>";	  
		  
	  $idx+=1;
	}
	
	if ($total_win_cnt>0 && $total_trades>0){
		$total_win_ratio=round(($total_win_cnt/$total_trades)*100,1);	
	}else{
		$total_win_ratio=0;		
	}	
		
	$table_html.="
	  <tr>
		<td>Net</td>
		<td>-</td>
		<td>-</td>
		<td>{$profit_5}</td>
		<td>{$total_trades}</td>
		<td>{$total_win_cnt}</td>
		<td>{$total_win_ratio}</td>
		<td>-</td>
	  </tr>";			
		
	
	$table_html.="</table><br>";	
	

	$sql = "select SUBSTRING_INDEX(a.close_date,' ',1) as close_date, count(a.provider) as provider_cnt, ROUND((sum(a.win_count)/sum(a.num_of_trades))*100,1) as win_ratio, sum(a.num_of_trades) as total_trades, sum(a.win_count) as total_win_cnt, (sum(a.win_count)*8.6 - 5*sum(a.num_of_trades)) as profit_5, (sum(a.win_count)*18 - 10*sum(a.num_of_trades)) as profit_10, (sum(a.win_count)*27 - 15*sum(a.num_of_trades)) as profit_15, (sum(a.win_count)*36 - 20*sum(a.num_of_trades)) as profit_20, (sum(a.win_count)*45 - 25*sum(a.num_of_trades)) as profit_25 , (sum(a.win_count)*91 - 50*sum(a.num_of_trades)) as profit_50 , (sum(a.win_count)*182 - 100*sum(a.num_of_trades)) as profit_100
			from trade_analysis a where a.win_ratio >= 56 and a.num_of_trades > 1 and a.close_date >= '{$start_date}' and a.close_date <= '{$gmt_date}' and a.provider != '{$my_robot_name}' and a.provider != 'rommjp'
			group by SUBSTRING_INDEX(a.close_date,' ',1)
			order by SUBSTRING_INDEX(a.close_date,' ',1)";
		
	$result = mysqli_query($link,$sql) or die(mysqli_error());
	
	$table_html.="<h3>Best Providers</h3>
	<table>
	  <tr>
		<th>close_date</th>
		<th>provider_cnt</th>
		<th>win_ratio</th>
		<th>total_trades</th>
		<th>total_win_cnt</th>
		<th>profit_5</th>
		<th>profit_10</th>
		<th>profit_15</th>
		<th>profit_20</th>
		<th>profit_25</th>
		<th>profit_50</th>
		<th>profit_100</th>
	  </tr>	
	  ";
	
	$win_ratio=0;
	$total_trades=0;
	$total_win_cnt=0;
	$profit_5=0;
	$profit_10=0;
	$profit_15=0;
	$profit_20=0;
	$profit_25=0;
	$profit_50=0;
	$profit_100=0;	
	
	while ($row = mysqli_fetch_array($result)) {
		//print_r($row);
		$total_trades+=$row['total_trades'];
		$total_win_cnt+=$row['total_win_cnt'];
		$profit_5+=$row['profit_5'];
		$profit_10+=$row['profit_10'];
		$profit_15+=$row['profit_15'];
		$profit_20+=$row['profit_20'];
		$profit_25+=$row['profit_25'];
		$profit_50+=$row['profit_50'];
		$profit_100+=$row['profit_100'];
		
		$table_html.="
		  <tr>
			<td>{$row['close_date']}</td>
			<td>{$row['provider_cnt']}</td>
			<td>{$row['win_ratio']}</td>
			<td>{$row['total_trades']}</td>
			<td>{$row['total_win_cnt']}</td>
			<td>{$row['profit_5']}</td>
			<td>{$row['profit_10']}</td>
			<td>{$row['profit_15']}</td>
			<td>{$row['profit_20']}</td>
			<td>{$row['profit_25']}</td>
			<td>{$row['profit_50']}</td>
			<td>{$row['profit_100']}</td>
		  </tr>		
	  ";	
	}
	
	if ($total_win_cnt>0 && $total_trades>0){
		$win_ratio=round(($total_win_cnt/$total_trades)*100,1);	
	}else{
		$win_ratio=0;		
	}	
	
	$table_html.="
	  <tr>
		<td>Net</td>
		<td>-</td>
		<td>{$win_ratio}</td>
		<td>{$total_trades}</td>
		<td>{$total_win_cnt}</td>
		<td>{$profit_5}</td>
		<td>{$profit_10}</td>
		<td>{$profit_15}</td>
		<td>{$profit_20}</td>
		<td>{$profit_25}</td>
		<td>{$profit_50}</td>
		<td>{$profit_100}</td>
	  </tr>		
  ";		

	$table_html.="</table><br>";	
	
	//Add my robot in the table
	$win_ratio=0;
	$total_trades=0;
	$total_win_cnt=0;
	$profit_5=0;
	$profit_10=0;
	$profit_15=0;
	$profit_20=0;
	$profit_25=0;
	$profit_50=0;
	$profit_100=0;	

	$sql = "select SUBSTRING_INDEX(a.close_date,' ',1) as close_date, ROUND((sum(a.win_count)/sum(a.num_of_trades))*100,1) as win_ratio, sum(a.num_of_trades) as total_trades, sum(a.win_count) as total_win_cnt, (sum(a.win_count)*8.6 - 5*sum(a.num_of_trades)) as profit_5, (sum(a.win_count)*18 - 10*sum(a.num_of_trades)) as profit_10, (sum(a.win_count)*27 - 15*sum(a.num_of_trades)) as profit_15, (sum(a.win_count)*36 - 20*sum(a.num_of_trades)) as profit_20, (sum(a.win_count)*45 - 25*sum(a.num_of_trades)) as profit_25 , (sum(a.win_count)*91 - 50*sum(a.num_of_trades)) as profit_50 , (sum(a.win_count)*182 - 100*sum(a.num_of_trades)) as profit_100
			from trade_analysis a where a.close_date >= '{$start_date}' and a.close_date <= '{$gmt_date}' and a.provider = '{$my_robot_name}'
			group by SUBSTRING_INDEX(a.close_date,' ',1)
			order by SUBSTRING_INDEX(a.close_date,' ',1)";
		
	$result = mysqli_query($link,$sql) or die(mysqli_error());
	
	$table_html.="<h3>{$my_robot_name}</h3>
	<table>
	  <tr>
		<th>close_date</th>
		<th>win_ratio</th>
		<th>total_trades</th>
		<th>total_win_cnt</th>
		<th>profit_5</th>
		<th>profit_10</th>
		<th>profit_15</th>
		<th>profit_20</th>
		<th>profit_25</th>
		<th>profit_50</th>
		<th>profit_100</th>
	  </tr>	
	  ";
	
	while ($row = mysqli_fetch_array($result)) {
		//print_r($row);
		$total_trades+=$row['total_trades'];
		$total_win_cnt+=$row['total_win_cnt'];
		$profit_5+=$row['profit_5'];
		$profit_10+=$row['profit_10'];
		$profit_15+=$row['profit_15'];
		$profit_20+=$row['profit_20'];
		$profit_25+=$row['profit_25'];
		$profit_50+=$row['profit_50'];
		$profit_100+=$row['profit_100'];
		
		$table_html.="
		  <tr>
			<td>{$row['close_date']}</td>
			<td>{$row['win_ratio']}</td>
			<td>{$row['total_trades']}</td>
			<td>{$row['total_win_cnt']}</td>
			<td>{$row['profit_5']}</td>
			<td>{$row['profit_10']}</td>
			<td>{$row['profit_15']}</td>
			<td>{$row['profit_20']}</td>
			<td>{$row['profit_25']}</td>
			<td>{$row['profit_50']}</td>
			<td>{$row['profit_100']}</td>
		  </tr>		
	  ";	
	}
	
	if ($total_win_cnt>0 && $total_trades>0){
		$win_ratio=round(($total_win_cnt/$total_trades)*100,1);	
	}else{
		$win_ratio=0;		
	}
		
	$table_html.="
	  <tr>
		<td>Net</td>
		<td>{$win_ratio}</td>
		<td>{$total_trades}</td>
		<td>{$total_win_cnt}</td>
		<td>{$profit_5}</td>
		<td>{$profit_10}</td>
		<td>{$profit_15}</td>
		<td>{$profit_20}</td>
		<td>{$profit_25}</td>
		<td>{$profit_50}</td>
		<td>{$profit_100}</td>
	  </tr>		
  ";	

	
?>
<!DOCTYPE html>
<html>
<head>
<style>
table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
}

td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
}

tr:nth-child(even) {
    background-color: #dddddd;
}
</style>
</head>
<body>
<?php echo $table_html; ?>
</body>
</html>