<script lang="ts">
  import { onMount } from 'svelte';
  import type { GPS, Baro, CPU} from '$lib/types';
  import BaroTemperatureChart from '$lib/components/BaroTemperatureChart.svelte';
  import CPUTemperatureChart from '$lib/components/CPUTemperatureChart.svelte';
	import CPULoadChart from '$lib/components/CPULoadChart.svelte';

  let GPSReading = $state<GPS | null>(null);
  let BaroReading = $state<Baro | null>(null);
  let CPUReading = $state<CPU | null>(null);  

  let baroHist = $state<Baro[]>([]);
  let cpuHist = $state<CPU[]>([]);

  onMount(async () => {

    const gpsEventSource = new EventSource('http://10.0.0.241:8000/gps');
    const baroEventSource = new EventSource('http://10.0.0.241:8000/baro');
    const cpuEventSource = new EventSource('http://10.0.0.241:8000/cpu');

    gpsEventSource.addEventListener('gps_sensor_update', (event) => {
      GPSReading = JSON.parse(event.data);
      console.log(GPSReading);
    });

    baroEventSource.addEventListener('baro_sensor_update', (event) => {
      BaroReading = JSON.parse(event.data);
      baroHist = [...baroHist, BaroReading].slice(-30);
      console.log(BaroReading);
    });

    cpuEventSource.addEventListener('cpu_sensor_update', (event) => {
      CPUReading = JSON.parse(event.data);
      cpuHist = [...cpuHist, CPUReading].slice(-30);
      console.log(CPUReading);
    });

    return () => {
      gpsEventSource.close();
      baroEventSource.close();
      cpuEventSource.close();
    };
  });

</script>

<main class="container">
  <h1>Cyberdeck Dashboard</h1>

  <hr class="solid">

  {#if BaroReading}
    <h2>Barometric Sensor</h2>
    <div class="dashboard-grid">
      <div class="card">
        <h2>Datetime</h2>
        <p class="reading">{BaroReading.datetime}</p>
      </div>

      <div class="card span-2">
        <h2>Temperature</h2>
        <p class="reading">{BaroReading.temperature_c} C</p>
        <BaroTemperatureChart baroData={baroHist}/>
      </div>

      <div class="card">
        <h2>Pressure</h2>
        <p class="reading">{BaroReading.pressure_hpa} hPA</p>
      </div>

      <div class="card">
        <h2>Altitude</h2>
        <p class="reading">{BaroReading.altitude_m} M</p>
      </div>
    </div>
  <hr class="solid">
  {/if}


  {#if CPUReading}
    <h2>CPU Stats</h2>
    <div class="dashboard-grid">
      <div class="card">
        <h2>Datetime</h2>
        <p class="reading">{CPUReading.datetime}</p>
      </div>

      <div class="card">
        <h2>Temperature</h2>
        <p class="reading">{CPUReading.temperature_c} C</p>
        <CPUTemperatureChart cpuData={cpuHist}/>
      </div>

      <div class="card">
        <h2>Load</h2>
        <p class="reading">{CPUReading.cpu_load}</p>
        <CPULoadChart cpuData={cpuHist}/>
      </div>

      <div class="card">
        <h2>Memory Usage MB</h2>
        <p class="reading">{CPUReading.memory_usage_mb} MB</p>
      </div>

      <div class="card">
        <h2>Memory Usage %</h2>
        <p class="reading">{CPUReading.memory_usage_percent} %</p>
      </div>
    </div>
    <hr class="solid">
  {/if}

  {#if GPSReading}
    <h2>GPS Sensor</h2>
    <div class="dashboard-grid">
      <div class="card">
        <h2>Datetime</h2>
        <p class="reading">{GPSReading.datetime}</p>
      </div>

      <div class="card">
        <h2>Longitude</h2>
        <p class="reading">{GPSReading.longitude} {GPSReading.longitude_direction}</p>
      </div>

      <div class="card">
        <h2>Latitude</h2>
        <p class="reading">{GPSReading.latitude} {GPSReading.latitude_direction}</p>
      </div>
    </div>
  {/if}
</main>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  .dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin-top: 2rem;
  }

  .card {
    background: #000000;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .reading {
    font-size: 2rem;
    font-weight: bold;
    margin: 1rem 0;
  }

  hr.solid {
    border-top: 3px solid #bbb;
  }
</style>