$(document).ready(function () {
  var RATE_LIMIT_IN_MS = 1000;
  var NUMBER_OF_REQUESTS_ALLOWED = 2;
  var NUMBER_OF_REQUESTS = 0;

  setInterval(function () {
    NUMBER_OF_REQUESTS = 0;

  }, RATE_LIMIT_IN_MS);

// Setup AJAX
  $.ajaxSetup({
    headers: {"X-CSRFToken": getCookie("csrftoken")},
    beforeSend: function canSendAjaxRequest() {
      var can_send = NUMBER_OF_REQUESTS < NUMBER_OF_REQUESTS_ALLOWED;
      NUMBER_OF_REQUESTS++;
      return can_send;
    }
  });

  $(document).ready(function () {
    if ($("#lefting").is(':visible')) {
      if ($(".over > li").length === 0) {
        let data = JSON.parse(localStorage.getItem("threads"));
        if (data == null || localStorage.lang !== $("html").attr("lang")) {
          $(".taq:eq(0)").click();
        }
        $(".over>p").text(localStorage.label);
        to_list(data);
      }
    }
  });
  $(".taq").click(function (e) {
    e.preventDefault();
    // console.log("es");
    let tag = $(this).attr("href");
    let label = $(this).text();
    let lang = $("html").attr("lang");
    // if(localStorage.label !== label) {
    $.ajax({
      url: tag,
      success: function (data) {
        localStorage.setItem("threads", JSON.stringify(data));
        localStorage.label = label;
        localStorage.lang = lang;
        // console.log(data);
        $(".over>ul>li").empty();  // .remove()
        to_list(data);
      }
    });
    // }
  });

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function to_list(data) {
    $(".over>p").text(localStorage.label);
    for (let key in data) {
      $(".over>ul").append("<li><a href=/t/" + data[key].slug + ">" +
        data[key].title + "<span>" + data[key].cnt + "</span></a></li>");
    }
  }


  $(".taq").dblclick(function (e) {
    let url = $(this).attr("href");
    window.location.replace(url);
  });


  $(function () {
    $("#q").autocomplete({
      source: '/s',
      select: function (event, ui) {
        $("#q").val(ui.item.label);
        $(".search-btn").click();
      }
    });
  });
  $(".search-btn").click(function (e) {
    var q = $("#q").val();
    if (jQuery.trim(q) === "") {
      // console.log("prevented");
      e.preventDefault();
    }
  });

  $("#paginator").on("change", function (e) {
    // let $url = window.location.href;
    // let $page = $(this).val();
    let $href = $(this).find(":selected").data("href");
    window.location.replace($href);
  });

  $('#mesaj').delay(3000).fadeOut();


  function favorite() {
    let favo = $(this);
    let pk = favo.data('id');

    $.ajax({
      url: "/entry/favorite/" + pk,
      type: 'GET',
      success: function (json) {
        // console.log("devr");
        favo.toggleClass('True');
        favo.next().text(json.count);
      }
    });

    return false;
  }


  $(function () {
    $('[data-action="fav"]').click(favorite);
  });
});