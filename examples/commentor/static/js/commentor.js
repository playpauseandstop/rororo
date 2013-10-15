/**
 * Commentor JavaScript application.
 *
 * Requirements
 * ============
 *
 * * `underscore.js <http://underscorejs.org/>`_ 1.5.2 or higher
 * * `zepto.js <http://zeptojs.org/>`_ 1.0 or higher
 *
 */

var commentorApp = function(options) {
  var errorElem = $("#js-error");

  if (!_.has(options, "addCommentUrl") ||
      !_.has(options, "getCommentsUrl")) {
    errorElem.html("Application Error");
    return false;
  }

  _.defaults(options, {"limit": 30});
  _.extend($.ajaxSettings, {"timeout": 30000});

  var commentForm = $("form"),
      commentAuthorField = $("#author"),
      commentTextField = $("#text"),
      commentsElem = $("#js-comments"),
      commentsTemplate = _.template($("#js-comments-template").html()),

      getComments = function(limit) {
        $.ajax({
          "url": options.getCommentsUrl,
          "type": "GET",
          "cache": false,

          "data": {"limit": limit || options.limit},
          "dataType": "json",

          "beforeSend": function() {
            commentsElem.html("Loading...");
          },
          "success": function(data) {
            errorElem.hide();
            commentsElem.html(commentsTemplate({"comments": data})).show();
          },
          "error": showAjaxError
        });
      },

      showAjaxError = function(xhr, errorType, error) {
        var message;

        if (_.has(xhr, "statusText") && xhr.statusText) {
          message = xhr.statusText;
        } else if (errorType == "timeout") {
          message = "Timeout Error";
        } else {
          message = "Unknown Server Error";
        }

        commentsElem.hide();
        errorElem.text(message).show();
      };

  commentForm.on("submit", function() {
    $.ajax({
      "url": options.addCommentUrl,
      "type": "POST",

      "data": {
        "author": commentAuthorField.val(),
        "text": commentTextField.val()
      },
      "dataType": "json",

      "success": function(data) {
        commentTextField.val("");
        commentAuthorField.val("").focus();
        getComments();
      },
      "error": showAjaxError
    });
    return false;
  });

  getComments();
  commentAuthorField.focus();

  setInterval(getComments, 60000);

  return true;
};
