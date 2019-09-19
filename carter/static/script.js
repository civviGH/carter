Chart.defaults.global.animation.duration = 0;
Chart.defaults.global.responsive = false;
Chart.scaleService.updateScaleDefaults('linear', {
  ticks:
  { max: 100,
    beginAtZero: true
  }
})

$(document).ready(function(){
  var socket = io.connect('https://' + document.domain + ':' + location.port);
  socket.on('update-module-of-client', function(data){
    var client_name = data['client_name'];
    var moduletype = data['type'];
    var updated_data = data['data'];
    id_string = 'c_' + client_name + '_' + moduletype;
    var ctx = document.getElementById(id_string);
    var chart = $(ctx).data('storedChart');
    chart.data = updated_data;
    chart.update();

  });
  socket.on('refresh-page', function(updates){
    location.reload();
  });
});
