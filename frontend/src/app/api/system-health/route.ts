import { NextResponse } from 'next/server';
import os from 'os';

// Helper to get CPU times sample
function getCpuSample() {
  const cpus = os.cpus();
  let totalTicks = 0;
  let idleTicks = 0;

  cpus.forEach((core) => {
    totalTicks += core.times.user + core.times.nice + core.times.sys + core.times.idle + core.times.irq;
    idleTicks += core.times.idle;
  });

  return { total: totalTicks, idle: idleTicks };
}

// Helper to calculate CPU load percentage over 150ms delay
async function getCpuLoad(): Promise<number> {
  const start = getCpuSample();
  await new Promise((resolve) => setTimeout(resolve, 150));
  const end = getCpuSample();

  const totalDiff = end.total - start.total;
  const idleDiff = end.idle - start.idle;

  if (totalDiff === 0) return 0.0;
  const cpuLoad = 100.0 * (1.0 - idleDiff / totalDiff);
  return Math.min(100.0, Math.max(0.0, cpuLoad));
}

export async function GET() {
  try {
    // 1. Get real RAM load
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const ramUsagePercent = 100.0 * (1.0 - freeMem / totalMem);

    // 2. Get real CPU load
    const cpuUsagePercent = await getCpuLoad();

    return NextResponse.json({
      cpu: cpuUsagePercent,
      ram: ramUsagePercent,
      hostname: os.hostname(),
      platform: os.platform()
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
