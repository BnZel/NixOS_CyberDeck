<script lang="ts">
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';
  import type { Baro } from '$lib/types';

  const { baroData } = $props<{ baroData: Baro[] }>();
  let canvas: HTMLCanvasElement;
  let chart = $state<Chart | undefined>(undefined);

  $effect(() => {
    if (chart && baroData) {
      chart.data.labels = baroData.map(reading => {
        const date = new Date(reading.datetime);
        return date.toLocaleTimeString();
      });
      chart.data.datasets[0].data = baroData.map(reading => reading.temperature_c);
      chart.update();
    }
  });

  onMount(() => {
    chart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: '°C',
          data: [],
          borderColor: '#3498db',
          tension: 0.4,
          fill: false
        }]
      },
      options: {
        responsive: true,
        animation: {
          duration: 0 // Disable animations for real-time updates
        },
        scales: {
          y: {
            beginAtZero: false,
            suggestedMin: 15,
            suggestedMax: 50
          }
        }
      }
    });

    return () => {
      if (chart) chart.destroy();
    };
  });
</script>

<canvas bind:this={canvas}></canvas>