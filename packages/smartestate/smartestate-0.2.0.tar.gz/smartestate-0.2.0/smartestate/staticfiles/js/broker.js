function editInAdmin(modelType, modelId) {
	href = "/admin/";
	switch(modelType) {
		case "listing":
			href += "listings/listing/";
			break;
		case "seeking":
			href += "broker/seeking/";
			break;
		case "matching":
			href += "broker/matching/";
			break;
		default:
			break;
	}
	href += modelId + "/change/";
	window.location = href;
}
function prepareFormDataForRest(dataArray) {
	n = dataArray.length;
	returnObject = {};
	for(i = 0; i < n; i++) {
		field_name = dataArray[i].name;
		field_value = dataArray[i].value;
		switch(field_name) {
			default:
				if(field_value != "") {
					returnObject[field_name] = field_value;
				}
				break;

			/*
			TODO: See Feature #368.
			Rename some of these fields in the models, so that we can use
			use the same name for both seekings and listings??
			 * */
			case 'is_primary':
			case 'pets_ok':
			case 'has_pets':
			case 'has_internet':
			case 'must_have_internet':
			case 'is_furnished':
			case 'must_be_furnished':
			case 'is_smoker':
				returnObject[field_name] =
					field_value == "on" ? 'True' : 'False';
				break;
		}
	}
	return returnObject;
}
function getNiceDate(dateString) {
	dateObject = new Date(dateString);
	monthString = new Intl.DateTimeFormat('en-US', {month: 'long'}).format(dateObject);
	return monthString + ' ' + String(dateObject.getDate()) + ', ' + String(dateObject.getFullYear());
}
function getAge(dateString) {
	var today = new Date();
	var birthDate = new Date(dateString);
	var age = today.getFullYear() - birthDate.getFullYear();
	var m = today.getMonth() - birthDate.getMonth();
	if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
		age--;
	}
	return age;
}
function toggleRentalOrForSale() {
	model_type = $(".form-toggle-field:first").val();
	if(model_type == "rental") {
		$(".rental-form-fields").css({"display": "table-row"});
		$(".for-sale-form-fields").css({"display": "none"});
	} else if(model_type == "for_sale") {
		$(".rental-form-fields").css({"display": "none"});
		$(".for-sale-form-fields").css({"display": "table-row"});
	} else {
		$(".rental-form-fields").css({"display": "table-row"});
		$(".for-sale-form-fields").css({"display": "table-row"});
	}
}
$(".form-toggle-field").change(toggleRentalOrForSale);
$(".form-toggle-button").click(function() {
	$(".search-form").toggleClass("hidden-form");
});
function submitListingsSearch() {
	$.ajax({
		url : "/rest/listings/",
		type : 'GET',
		data : prepareFormDataForRest($("#listings-search").serializeArray()),
		dataType:'json',
		success : function(data) {
			html = "";
			n = data.length;
			for(i = 0; i < n; i++) {
				// See templates/broker/list-listing.html
				html += '<tr onclick="editInAdmin(\'listing\', '+data[i]['id']+');" class="broker-row">';
				try {
					html += '<td>'+data[i]['id']+'</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>'+data[i]['listing_type']+'</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>' + getNiceDate(data[i]['date_available']) + '</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				if(data[i]['listing_type'] == 'rental') {
					try {
						html += '<td>'+data[i]['rental_price']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}
				} else if(data[i]['listing_type'] == 'for_sale') {
					try {
						html += '<td>'+data[i]['for_sale_price']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}
				}

				try {
					html += '<td>'+data[i]['short_description']+'</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>' +
						data[i]['apartment']['house']['real_estate']['address']['street'] + ', ' +
						data[i]['apartment']['house']['real_estate']['address']['zip_code'] + ' ' +
						data[i]['apartment']['house']['real_estate']['address']['city'] +
						'</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>'+data[i]['apartment']['size_sq_m']+'m<sup>2</sup></td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>'+data[i]['apartment']['number_of_rooms']+'</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				html += '</tr>';
			}
			$("#listings-table-body").html(html);
		},
		error : function(request,error) {
			alert("Request: "+JSON.stringify(request));
		}
	});
}
$("#listings-search :input").change(submitListingsSearch);
$("#listings-search-submit").click(submitListingsSearch);
function submitSeekingsSearch() {
	$.ajax({
		url : "/rest/seekings/",
		type : 'GET',
		data : prepareFormDataForRest($("#seekings-search").serializeArray()),
		dataType:'json',
		success : function(data) {
			html = "";
			n = data.length;
			for(i = 0; i < n; i++) {
				// See templates/broker/list-seeking.html
				html += '<tr onclick="editInAdmin(\'seeking\', '+data[i]['id']+');" class="broker-row">';
				try {
					html += '<td>'+data[i]['id']+'</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>'+data[i]['seeking_type']+'</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>' + getNiceDate(data[i]['starting_date']) + '</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				if(data[i]['seeking_type'] == 'rental') {
					try {
						html += '<td>'+data[i]['max_rent']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}
				} else if(data[i]['seeking_type'] == 'for_sale') {
					try {
						html += '<td>'+data[i]['max_purchase_price']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}
				}
				try {
					html += '<td>'+data[i]['min_number_of_rooms']+'</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>' + data[i]['contact']['first_name'] + ' ' + 
						data[i]['contact']['last_name'] + '</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>' + String(getAge(data[i]['contact']['date_of_birth'])) + '</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>'+data[i]['number_of_persons']+'</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				try {
					html += '<td>'+data[i]['occupation']+'</td>';
				} catch(TypeError) {
					html += '<td></td>';
				}

				html += '</tr>';
			}
			$("#seekings-table-body").html(html);
		},
		error : function(request,error) {
			alert("Request: "+JSON.stringify(request));
		}
	});
}
$("#seekings-search :input").change(submitSeekingsSearch);
$("#seekings-search-submit").click(submitSeekingsSearch);
function resetSearchForm() {
	$(".search-form:first").trigger("reset");
	toggleRentalOrForSale();
	try {
		submitListingsSearch();
	} catch {}
	try {
		submitSeekingsSearch();
	} catch {}
}
$(".form-reset-button").click(resetSearchForm);


function toggleSuggestions(rowType, id, queryObject) {
	if($("#suggestions-row-"+rowType+String(id)).css("display") == "none") {
		$("#suggestions-row-"+rowType+String(id)).css("display", "table-row");
	} else {
		$("#suggestions-row-"+rowType+String(id)).css("display", "none");
	}
	var restUrl;
	if(rowType == "listing") {
		restUrl = "/rest/seekings/";
	} else if(rowType == "seeking") {
		restUrl = "/rest/listings/";
	} else {
		throw 'No rowType passed to toggleSuggestions!';
	}
	$.ajax({
		url : restUrl,
		type : 'GET',
		data : queryObject,
		dataType:'json',
		success : function(suggestionsData) {
			html = '<td colspan=8>';
			n = suggestionsData.length;
			n = n > 4 ? 4 : n;
			if(n == 0) {
				if(rowType == "listing") {
					html += '<h4>No matching Seekings found!</h4>';
					html += '<a href="/broker/seekings/">See all Seekings</a>';
				}
				else if(rowType == "seeking") {
					html += '<h4>No matching Listings found!</h4>';
					html += '<a href="/broker/listings/">See all Listings</a>';
				} else {
					throw 'No rowType passed to toggleSuggestions!';
				}
			} else {
				if(rowType == "listing") {
					html += '<table>';
					html += '<tr>';
					html += '<th>ID</th>';
					html += '<th>Type</th>';
					html += '<th>Start date</th>';
					html += '<th>Max price</th>';
					html += '<th>Tenant/Buyer name</th>';
					html += '<th>Number of persons</th>';
					html += '<th>Status</th>';
					html += '<th></th>';
					html += '</tr>';
				} else if(rowType == "seeking") {
					html += '<table>';
					html += '<tr>';
					html += '<th>ID</th>';
					html += '<th>Type</th>';
					html += '<th>Available on</th>';
					html += '<th>Price</th>';
					html += '<th>Description</th>';
					html += '<th>Address</th>';
					html += '<th>Size</th>';
					html += '<th>Rooms</th>';
					html += '<th>Status</th>';
					html += '<th></th>';
					html += '</tr>';
				} else {
					throw 'No rowType passed to toggleSuggestions!';
				}
			}
			if(rowType == "listing") {
				for(i = 0; i < n; i++) {
					var currentMatching = {};
					$.ajax({
						url: '/rest/matchings/',
						type : 'GET',
						data : {
							'listing_id': id,
							'seeking_id': suggestionsData[i]['id']
						},
						async: false,
						dataType:'json',
						success : function(matchingData) {
							if(matchingData.length > 0) {
								/*
								 ' TODO: See Feature #413.
								 * */
								currentMatching = matchingData[0];
							}
						},
						error : function(matchingData) {
							throw "Could not reach the API endpoint /rest/matchings/";
						},
					});

					html += '<tr>';

					try {
						html += '<td>'+suggestionsData[i]['id']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						html += '<td>'+suggestionsData[i]['seeking_type']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						html += '<td>' + getNiceDate(suggestionsData[i]['starting_date']) + '</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						if(suggestionsData[i]['seeking_type'] == 'rental') {
							html += '<td>'+suggestionsData[i]['max_rent']+'</td>';
						} else if(suggestionsData[i]['seeking_type'] == 'for_sale') {
							html += '<td>'+suggestionsData[i]['max_purchase_price']+'</td>';
						}
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						html += '<td>' + suggestionsData[i]['contact']['first_name'] + ' ' + 
							suggestionsData[i]['contact']['last_name'] + '</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						html += '<td>'+suggestionsData[i]['number_of_persons']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					html += '<td colspan=2>';
					if(Object.keys(currentMatching).length == 0) {
						/*
        					TODO: See Feature #401. When posting a new matching, also set the status.
						 * */
						/*
						html += '<td><select>' +
							'<option>Possible</option>' +
							'<option>Pending</option>' +
							'<option>Closed</option></select></td>';
						 * */
						html += '<span>New matching</span>';
						html += '<input type="button" value="Create new matching" ' +
							'onclick="postMatching('+id+', '+suggestionsData[i]['id']+')">';
						// TODO: See Feature #403.
						html += '<span class="ajax-reponse" ' +
							'id="post-matching-reponse-'+id+'-'+suggestionsData[i]['id']+'"></span>';
					} else {
						matchingStatuses = ["possible", "pending", "closed"];

						html += '<select name="matching-' + currentMatching['id'] + '-status" ' +
							'id="matching-' + currentMatching['id'] + '-status">';

						for(i = 0; i < 3; i++) {
							if(currentMatching['status'] == matchingStatuses[i]) {
								html += '<option selected>'+matchingStatuses[i]+'</option>';
							} else {
								html += '<option>'+matchingStatuses[i]+'</option>';
							}
						}
						html += '</select>';

						html += '<input type="button" value="Update matching" ' +
							'onclick="patchMatching('+currentMatching['id']+', ' +
							'document.getElementById(\'matching-' + currentMatching['id'] +
								'-status\').value)">';

						// TODO: See Feature #403.
						html += '<span class="ajax-reponse" id="patch-matching-reponse-'+currentMatching['id']+
							'"></span>';
					}
					html += '</td>';
					html += '</tr>';
				}
				if(suggestionsData.length > n) {
					/*
					 * TODO
					 * This will just go to the list view for all Seekings.
					 * But it should retain the search parameters of the Listing with which it matched.
					 * See Feature #382
					 * */
					html += '<tr><td><a href="/broker/seekings/">See more Seekings</a></td></tr>';
				}
			} else if(rowType == "seeking") {
				for(i = 0; i < n; i++) {
					var currentMatching = {};
					$.ajax({
						url: '/rest/matchings/',
						type : 'GET',
						data : {
							'listing_id': suggestionsData[i]['id'],
							'seeking_id': id
						},
						async: false,
						dataType:'json',
						success : function(matchingData) {
							if(matchingData.length > 0) {
								/*
								 ' TODO: See Feature #413.
								 * */
								currentMatching = matchingData[0];
							}
						},
						error : function(matchingData) {
							throw "Could not reach the API endpoint /rest/matchings/";
						},
					});
					html += '<tr>';

					try {
						html += '<td>'+suggestionsData[i]['id']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						html += '<td>'+suggestionsData[i]['listing_type']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						html += '<td>' + getNiceDate(suggestionsData[i]['date_available']) + '</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						if(suggestionsData[i]['listing_type'] == 'rental') {
							html += '<td>'+suggestionsData[i]['rental_price']+'</td>';
						} else if(suggestionsData[i]['listing_type'] == 'for_sale') {
							html += '<td>'+suggestionsData[i]['for_sale_price']+'</td>';
						}
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						html += '<td>'+suggestionsData[i]['short_description']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						html += '<td>' +
							suggestionsData[i]['apartment']['house']['real_estate']['address']['street'] + ', ' +
							suggestionsData[i]['apartment']['house']['real_estate']['address']['zip_code'] + ' ' +
							suggestionsData[i]['apartment']['house']['real_estate']['address']['city'] +
							'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						html += '<td>'+suggestionsData[i]['apartment']['size_sq_m']+'m<sup>2</sup></td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					try {
						html += '<td>'+suggestionsData[i]['apartment']['number_of_rooms']+'</td>';
					} catch(TypeError) {
						html += '<td></td>';
					}

					html += '<td colspan=2>';
					if(Object.keys(currentMatching).length == 0) {
						/*
        					TODO: See Feature #401. When posting a new matching, also set the status.
						 * */
						/*
						html += '<td><select>' +
							'<option>Possible</option>' +
							'<option>Pending</option>' +
							'<option>Closed</option></select></td>';
						 * */
						html += '<span>New matching</span>';
						html += '<input type="button" value="Create new matching" ' +
							'onclick="postMatching('+suggestionsData[i]['id']+', '+id+')">'
						// TODO: See Feature #403.
						html += '<span class="ajax-reponse" ' +
							'id="post-matching-reponse-'+suggestionsData[i]['id']+'-'+id+'"></span>';
					} else {
						matchingStatuses = ["possible", "pending", "closed"];

						html += '<select name="matching-' + currentMatching['id'] + '-status" ' +
							'id="matching-' + currentMatching['id'] + '-status">';

						for(i = 0; i < 3; i++) {
							if(currentMatching['status'] == matchingStatuses[i]) {
								html += '<option selected>'+matchingStatuses[i]+'</option>';
							} else {
								html += '<option>'+matchingStatuses[i]+'</option>';
							}
						}
						html += '</select>';

						html += '<input type="button" value="Update matching" ' +
							'onclick="patchMatching('+currentMatching['id']+', ' +
							'document.getElementById(\'matching-' + currentMatching['id'] +
								'-status\').value)">';

						// TODO: See Feature #403.
						html += '<span class="ajax-reponse" id="patch-matching-reponse-'+currentMatching['id']+
							'"></span>';
					}
					html += '</td>';
					html += '</tr>';
				}
				if(suggestionsData.length > n) {
					/*
					 * TODO
					 * This will just go to the list view for all Listings.
					 * But it should retain the search parameters of the Seeking with which it matched.
					 * See Feature #382
					 * */
					html += '<tr><td><a href="/broker/listings/">See more Listings</a></td></tr>';
				}
			} else {
				throw 'No rowType passed to toggleSuggestions!';
			}
			if(n > 0) {
				html += '</table>';
			}
			html += '</td>';
			$("#suggestions-row-"+rowType+String(id)).html(html);
		},
		error : function(request,error) {
			alert("Request: "+JSON.stringify(request));
		}
	});
}

function postMatching(listingId, seekingId) {
	var csrfToken = getCookie('csrftoken')
	$.ajax({
		url: '/rest/matchings/',
		type : 'POST',
		headers : {
			'X-CSRFToken': csrfToken
		},
		data : {
			'listing_id': listingId,
			'seeking_id': seekingId
		},
		dataType:'json',
		success : function(response) {
			/*
			 * TODO
			$("#post-matching-response-"+listingId+"-"+seekingId).css({"display": "inline"});
			$("#post-matching-response-"+listingId+"-"+seekingId).html("Successfully created new matching!");
			 * */
			alert("Successfully created matching!");
			document.location.reload();
		},
		error : function(response) {
			/*
			 * TODO
			$("#post-matching-response-"+listingId+"-"+seekingId).css({"display": "inline"});
			$("#post-matching-response-"+listingId+"-"+seekingId).html(JSON.stringify(response));
			 * */
			alert("Failed to create matching!");
		},
	});
}
function patchMatching(matchingId, matchingStatus) {
	var csrfToken = getCookie('csrftoken')
	$.ajax({
		url: '/rest/matchings/',
		type : 'PATCH',
		headers : {
			'X-CSRFToken': csrfToken
		},
		data : {
			'id': matchingId,
			'status': matchingStatus
		},
		dataType:'json',
		success : function(response) {
			alert("Successfully updated matching!");
			/*
			// TODO: See Feature #403.
			$("#patch-matching-response-"+matchingId).css({"display": "inline"});
			$("#patch-matching-response-"+matchingId).html("Successfully updated matching!");
			 * */
		},
		error : function(response) {
			alert("Failed to update matching!");
			/*
			// TODO: See Feature #403.
			$("#patch-matching-response-"+matchingId).css({"display": "inline"});
			$("#patch-matching-response-"+matchingId).html(JSON.stringify(response));
			 * */
		},
	});
}

// TODO: There should be a better, more central way to get a cookie...
//       We have a 'cookie-module' in smartestate/staticfiles/js, but for some reason...
//       - We cannot import it, so we have to copy paste it to the top of the file, which is already very ugly.
//       - In this file (broker.js), copy pasting that code does not work like it does in main.js, something about
//         not being able to use the 'export' statement unless in the top of a module....
//       See Bug #329...
// This code is simply copy-pasted from the Django-docs: https://docs.djangoproject.com/en/dev/howto/csrf/
function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
