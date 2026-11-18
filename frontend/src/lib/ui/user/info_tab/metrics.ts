import type { MetricDef, MetricKey } from './types';

export const fmtDuration = (min: number) =>
 `${Math.floor(min / 60)}h ${String(Math.round(min % 60)).padStart(2, '0')}m`;
export const fmtTemp = (v: number) => `${v.toFixed(1)} °C`;
export const fmtInt = (v: number) => String(Math.round(v));

export const metrics: MetricDef[] = [
    { key: 'avgSitMin', label: 'Avg. sitting time', short: 'Ø Sit', color: 'var(--chart-1)', format: fmtDuration },
    { key: 'avgStandMin', label: 'Avg. standing time', short: 'Ø Stand', color: 'var(--chart-2)', format: fmtDuration },
    { key: 'temperature', label: 'Temperature', short: 'Temp', color: 'var(--chart-3)', format: fmtTemp },
    { key: 'errors', label: 'Errors', short: 'Errors', color: 'var(--chart-4)', format: fmtInt },
    { key: 'warnings', label: 'Warnings', short: 'Warn', color: 'var(--chart-5)', format: fmtInt },
];

export const metricMap = Object.fromEntries(
    metrics.map((m) => [m.key, m])
) as Record<MetricKey, MetricDef>;