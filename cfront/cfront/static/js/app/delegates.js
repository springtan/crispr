$(document).on("click",".show-less",function(){
    $(this).parent().addClass("showing-less");
    $(this).parent().removeClass("showing-more");
})
$(document).on("click",".show-more",function(){
    $(this).parent().addClass("showing-more");
    $(this).parent().removeClass("showing-less");
})
$(document).on("click","#email-complete",function(){
    $.getJSON("/j/email_complete/"+current_job.id,
	      {do_email:$(this).is(":checked")},
	      function(data){
		  console.log("email callback returned")
		  console.log("new value: ", data)
	      })
})