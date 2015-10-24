$(document).ready(function() {	
	var buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9'];
	var b_count = 0;

	var hup = "hang_up";
	var pup = "pick_up";

	$("#mp_receiver")
		.html(pup)
		.click(function() {
			if($(this).html() == hup) {
				next_state = pup;
			} else if($(this).html() == pup) {
				next_state = hup;
			}

			$.ajax({
				url : $(this).html(),
				context : this
			}).done(function(json) {
				console.info(json);				
				$(this).html(next_state);
			});
		});
	
	for(var i=0; i<3; i++) {
		var tr = $(document.createElement('tr'));
		for(var j=0; j<3; j++) {
			var html = "<p class=\"num\">" + buttons[b_count] + "</p>";

			var td = $(document.createElement('td'));
			var a = $(document.createElement('a'))
				.html(html)
				.click(function() {
					var mapping = $($(this).find('.num')[0]).html();

					$.ajax({
						url : "mapping/" + Number(mapping)
					}).done(function(json) {
						console.info(json);
					});
				});

			$(td).append(a);
			$(tr).append(td);

			b_count ++;
		}

		$("#mp_main").append(tr);
	}
});