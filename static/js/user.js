$(document).on("submit", "#follow_form", function (e) {
	e.preventDefault();
	$.ajax({
		type: "POST",
		url: "/follow_request",
		data: {
			follower_id: $("#follower").val(),
			following_id: $("#following").val(),
		},
	});
});

const follow_button = document.querySelector("#follow_btn");

follow_button.addEventListener("click", function () {
	if (follow_button.innerText === "Follow") {
		follow_button.innerText = "Following";
	} else {
		follow_button.innerText = "Follow";
	}
});
