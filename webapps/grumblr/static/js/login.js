
$('#login-form').on('submit', function(event) {
    event.preventDefault();
    var loginForm = $("#login-form").serialize();
    console.log("I am here!");
    $.post("/grumblr/login", loginForm, function(response) {

    });

});
