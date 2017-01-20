

$(document).ready(function() {

    // CSRF set-up copied from Django docs
      function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
      }
      var csrftoken = getCookie('csrftoken');
      $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      });

    $(".addComment").on('keypress', function(e) {
        $(this).unbind('submit').bind('submit', function(event) {
            event.preventDefault();
            if(e.which == 13) {
                var addComment = $(this);
                var id = $(this).attr('id').trim();
                var status_id = id.split("_")[1];
                var comment_area = $(this).parent().siblings();
                var addCommentForm = $(this).serialize();
                var addComment_id = "addComment_" + status_id;
                $.post("/grumblr/addComment/"+status_id, addCommentForm, function(response) {
                    $(response).insertBefore("#comment_entry_bottom_" + status_id);
                    var input = $("#"+addComment_id).find("div").find("input");
                    input.val("");
                });
            }
        });
    });

//    $("#postStatusBtn").click(postStatus);
    $("#postStatusBtn").on('click', function(e) {
        $("#postStatus").unbind('submit').bind('submit', function(event) {
            event.preventDefault();
            var form = $("#postStatus").serialize();
            var last_post = findLastPost();
            $.post("/grumblr/post/"+last_post, form, function(response){
                $(response).insertAfter("#insertAfter");
                $("textarea").val("");
                addCommentsBatch();
            });
        });
    });

    function findLastPost() {
        var insertAfter_element = $('.comment-area:first');
        last_post = 0
        if (insertAfter_element.attr("id") != undefined) {
            last_post = insertAfter_element.attr("id").split("_")[1].trim();
        }
        return last_post;
    }

    function addCommentsBatch() {
        $(".addComment").on('keypress', function(e) {
            $(this).unbind('submit').bind('submit', function(event) {
                event.preventDefault();
                if(e.which == 13) {
                    var addComment = $(this);
                    var id = $(this).attr('id').trim();
                    var status_id = id.split("_")[1];
                    var comment_area = $(this).parent().siblings();
                    var addCommentForm = $(this).serialize();
                    var addComment_id = "addComment_" + status_id;

                    $.post("/grumblr/addComment/"+status_id, addCommentForm, function(response) {
                        $(response).insertBefore("#comment_entry_bottom_" + status_id);
                        var input = $("#"+addComment_id).find("div").find("input");
                        input.val("");
                    });

                }
            });
        });
        var last_comment = $("#insertAfter").attr("class").trim();
        $.post("/grumblr/refreshComment/" + last_comment, function(response){
            var user_list = new Object();
            $.each($.parseJSON(response["user_list"]), function(key, value){
                user_list[value.pk] = value;
            });
            var time_dict = response["time_dict"];
            handleComment_List(response["comment_list"], response["last_comment"], time_dict, user_list);
        });
    }

    function handleComment_List(comment_list, last_comment, time_dict, user_list) {
         $.each($.parseJSON(comment_list), function(key, value) {
                var status_id = value.fields.status;
                var element_id = "comment_entry_bottom_" + status_id;
                $('#comments_' + status_id).children(".comment_table").each(function(){
                    var existing_comment_id = $(this).attr("id").trim().split("_")[2];
                    if (existing_comment_id == value.pk) {
                        $(this).remove();
                    }
                });
                var new_comment = appendComment(value, time_dict[value.pk], user_list[value.fields.owner]);
                $(new_comment).insertBefore("#"+element_id);
            });
            var old_id = $("#insertAfter").attr("class");
            $( "#insertAfter" ).removeClass( old_id ).addClass( last_comment.toString());
    }

    window.setInterval(refreshPage, 5000);

    function refreshPage() {
        if (window.location.pathname == "/grumblr/" || window.location.pathname == "/") {
            var last_post = findLastPost();
            $.post("/grumblr/loadNewStatus/" + last_post, function(response){
                $(response).insertAfter("#insertAfter");
                addCommentsBatch();
            });
        }

        else if (window.location.pathname.startsWith("/grumblr/profile/")) {
            user_name = $("#profile_information").attr("name");
            var last_comment = $("#insertAfter").attr("class").trim();
            $.post("/grumblr/loadNewComment/"+ user_name +"/" + last_comment , function(response) {
            var user_list = new Object();
            $.each($.parseJSON(response["user_list"]), function(key, value){
                user_list[value.pk] = value;
            });
                handleComment_List(response["comment_list"], last_comment, response["time_dict"], user_list);
            })
        }
        else if (window.location.pathname.startsWith("/grumblr/following")) {
            var last_post = findLastPost();
            $.post("/grumblr/refreshFollowing/" + last_post, function(response){
                $(response).insertAfter("#insertAfter");
                var last_comment = $("#insertAfter").attr("class").trim();
                $.post("/grumblr/refreshFollowingComments/" + last_comment, function(response){
                        var user_list = new Object();
                        $.each($.parseJSON(response["user_list"]), function(key, value){
                            user_list[value.pk] = value;
                        });
                        $.each($.parseJSON(response["comment_list"]), function(key, value) {
                            var status_id = value.fields.status;
                            var element_id = "comment_entry_bottom_" + status_id;
                            var time_dict = response["time_dict"];
                            var new_comment = appendComment(value, time_dict[value.pk], user_list[value.fields.owner]);
                            $(new_comment).insertBefore("#"+element_id);
                    });
                });
            });
        }
    }

    function appendComment(comment, time, user){

        create_date = time;
        first_name = user.fields.first_name;
        last_name = user.fields.last_name;
        text = comment.fields.text;
        var image = "/static/images/thumbnail2.png";
        if (user.fields.selfi != "") {
            image = "/grumblr/photo/" + user.fields.user_name;
        }
        var comment_id = "comment_data_" + comment.pk;
        var profile = "/grumblr/profile/" + user.fields.user_name;
        var new_comment_str = "<table id=\"" + comment_id +  "\" class=\"comment_table\" type=\"table\"> \
                   <tr> \
                        <td class=\"comment_entry_image_td\"> \
                            <div class=\"comment_entry_image_div\"> \
                                <img src=\"" + image + "\" class=\"comment_thumbnail\" alt=\"oo\"> \
                            </div> \
                        </td> \
                        <td><div class=\"comment_entries_collection\"> \
                            <div class=\"comment_name\"> \
                                <a href=\"" + profile + "\">" + first_name + " " + last_name + "</a> \
                            </div> \
                            <div class=\"comment_entry\">" + text + "</div> \
                            <div class=\"time statu\">" +
                                create_date +
                            "</div> \
                        </div></td> \
                   </tr> \
                </table> "
        return new_comment_str;
    }

});
