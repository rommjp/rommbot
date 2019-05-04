<?php
//Script to call googleapi server and fetch geocoded info based on address string
//Author: R Poggenberg -- 28/04/2019

$address = isset($_GET['address'])? $_GET['address'] : "92 View Street, St Albans, Victoria, 3021";
$url_address= urlencode($address);
$gmaps_api_key="AIzaSyAND32vUTbl50UMkn8SQMm3ZUXsxOkOIuI";
$url="https://maps.googleapis.com/maps/api/geocode/json?address={$url_address}&key={$gmaps_api_key}";
$data_address=array();

// get the json response
$resp_json = file_get_contents($url);

// decode the json
$resp = json_decode($resp_json, true);

// response status will be 'OK', if able to geocode given address 

if($resp['status']=='OK'){
	$address_components=array();
	// get the important data
	$lati = isset($resp['results'][0]['geometry']['location']['lat']) ? $resp['results'][0]['geometry']['location']['lat'] : "";
	$longi = isset($resp['results'][0]['geometry']['location']['lng']) ? $resp['results'][0]['geometry']['location']['lng'] : "";
	$formatted_address = isset($resp['results'][0]['formatted_address']) ? $resp['results'][0]['formatted_address'] : "";
	if (isset($resp['results'][0]['address_components'])){
		foreach($resp['results'][0]['address_components'] as $values){
			array_push($address_components,$values['long_name']);
		}
	}
	 
	if (count($address_components)==8){
		$idx=0;
		foreach($address_components as $values){
			switch ($idx) {
				case 0:
					array_push($data_address, array('unit_num' => $values));
					break;
				case 1:
					array_push($data_address, array('street_num' => $values));
					break;
				case 2:
					array_push($data_address, array('street_name' => $values));
					break;
				case 3:
					array_push($data_address, array('suburb' => $values));
					break;
				case 4:
					array_push($data_address, array('council' => $values));
					break;
				case 5:
					array_push($data_address, array('state' => $values));
					break;
				case 6:
					array_push($data_address, array('country' => $values));
					break;
				case 7:
					array_push($data_address, array('postcode' => $values));
					break;	
			}
			
			$idx++;			
		}			
	}else{
		$idx=0;
		foreach($address_components as $values){
			switch ($idx) {
				case 0:
					array_push($data_address, array('street_num' => $values));
					break;
				case 1:
					array_push($data_address, array('street_name' => $values));
					break;
				case 2:
					array_push($data_address, array('suburb' => $values));
					break;
				case 3:
					array_push($data_address, array('council' => $values));
					break;
				case 4:
					array_push($data_address, array('state' => $values));
					break;
				case 5:
					array_push($data_address, array('country' => $values));
					break;
				case 6:
					array_push($data_address, array('postcode' => $values));
					break;	
			}
			
			$idx++;			
		}	
	}
	
	array_push($data_address, array('lat' => $lati));
	array_push($data_address, array('lng' => $longi));
	array_push($data_address, array('full_address' => $formatted_address));
	array_push($data_address, array('status' => 'OK'));
	 	
}else{
	array_push($data_address, array('status' => 'Unable to geocode'));
}

//Return address dictionary			
echo json_encode($data_address);

?>