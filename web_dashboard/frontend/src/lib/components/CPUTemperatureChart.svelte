<script lang="ts">
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';
  import type { CPU } from '$lib/types';

  const { cpuData } = $props<{ cpuData: CPU[] }>();
  let canvas: HTMLCanvasElement;
  let chart = $state<Chart | undefined>(undefined);

  $effect(() => {
    if (chart && cpuData) {
      chart.data.labels = cpuData.map(reading => {
        const date = new Date(reading.datetime);
        return date.toLocaleTimeString();
      });
      chart.data.datasets[0].data = cpuData.map(reading => reading.temperature_c);
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
            suggestedMax: 30
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