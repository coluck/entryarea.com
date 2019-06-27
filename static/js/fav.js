function fav() {
    let like = $(this);
    let pk = like.data('id');

    $.ajax({
        url : "/entry/fav/" + pk,
        type : 'Get',
        success : function (json) {
            like.find("[data-count='fav']").text(json.cnt);
            // like.find(".heart fa fa-heart-o");
            like.addClass('heart fa fa-heart');
        }
    });

    return false;
}

$(function() {
    $('[data-action="fav"]').click(fav);
});