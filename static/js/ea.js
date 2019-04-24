$(document).ready(function () {
  $('#mesaj').delay(1500).fadeOut();
});

// {% block script %}
//   <script>
//     $(document).ready(function () {
//       {#$("#latest_threads").click(function () {#}
//         $.ajax({
//             url: "/threads",
//             success: function (data) {
//               console.log("success", data);
//               {#$("li").html(data[0].title);#}
//               $("#frm>ul>li").remove();
//               for (let key in data) {
//                 $("#frm>ul").append("<li><a href=/t/" + data[key].slug + ">" + data[key].title +
//                   "</a><span>" + data[key].cnt + "</span></li>");
//               }
//             }
//           }
//         )
//       //});
//       $("#tag").click(function () {
//         $.ajax({
//           url: "/tags/fevri",
//           success: function (data) {
//             console.log("success", data);
//             {#$("li").html(data[0].title);#}
//             $("#frm>ul>li").remove();
//             for (let key in data) {
//               $("#frm>ul").append("<li><a href=/t/" + data[key].slug + ">" + data[key].title +
//                 "</a><span>" + data[key].cnt + "</span></li>");
//             }
//           }
//         })
//       });
//     });
//   </script>
// {% endblock %}