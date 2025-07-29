function refreshOrder() {
  $("#sections  .form-container").each(function (i) {
    const order = i + 1;
    let id = $(this).attr("data-order-field");
    console.log(id);
    $("#" + id).val(order);
  });
}

function refreshQuestions() {
  let questions = $(".question-sortable");
  questions.each(function (i) {
    let id = $(this).attr("data-pk");
    $(questions[i])
      .find(".question-container")
      .each(function (i) {
        let section = $(this).find("input[name=question-sections\\[\\]]")[0];
        $(section).val(id);
      });
  });
}

$(document).ready(function () {
  $("#sections").sortable({
    handle: ".outer-handle",
    animation: 150,
    onEnd: refreshOrder,
  });

  $(".question-sortable").sortable({
    handle: ".inner-handle",
    group: "questions",
    animation: 150,
    onEnd: refreshQuestions,
  });
});
