$(document).ready(function(){
  var socket = io.connect('https://' + document.domain + ':' + location.port);
  socket.on('update-module-of-client', function(updates){
    id_string = 'c_' + updates['client_name'] + '_' + updates['module']['type'];
    var ctx = document.getElementById(id_string);
    var chart = new Chart(ctx, updates['module']['render_options']);
  });
  socket.on('refresh-page', function(updates){
    location.reload();
  });
});
