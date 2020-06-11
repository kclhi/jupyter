define(['base/js/events'], function(events) {
  events.on('execute.CodeCell', function(){
    console.log("Sending run.")
    $.get( "http://localhost/panda", function(data) {});
  });
});
