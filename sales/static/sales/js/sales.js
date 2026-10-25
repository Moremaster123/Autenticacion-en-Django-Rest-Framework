$(document).ready(function () {
  var salesCanvas = $('#salesChart');

  $.ajax({
    url: salesCanvas.data('url'),
    method: 'GET',
    dataType: 'json',
    success: function (data) {
      new Chart(salesCanvas, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Ventas ($)',
            data: data.totals,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          scales: { y: { beginAtZero: true } }
        }
      });

      new Chart($('#statusChart'), {
        type: 'doughnut',
        data: {
          labels: data.status_labels,
          datasets: [{
            data: data.status_counts,
            backgroundColor: ['#6c757d', '#198754', '#0d6efd', '#dc3545']
          }]
        }
      });
    },
    error: function () {
      $('#chartError').text('No se pudieron cargar los datos de ventas.').show();
    }
  });
});
