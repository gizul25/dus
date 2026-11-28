import type { MetricDef, MetricKey } from './types';

export const fmtDuration = (min: number) => `${Math.floor(min / 60)}h ${String(Math.round(min % 60)).padStart(2, '0')}m`;
export const fmtTemp = (v: number) => `${v.toFixed(1)} °C`;
export const fmtHumidity = (v: number) => `${v.toFixed(0)} %`;
export const fmtLight = (v: number) => `${(v * 100).toFixed(0)} %`;
export const fmtInt = (v: number) => String(Math.round(v));

export const metrics: MetricDef[] = [
	{ key: 'timeUsedMin', label: 'Time used',     short: 'Used',   color: 'var(--chart-1)', format: fmtDuration },
	{ key: 'uniqueUsers', label: 'Unique users',  short: 'Users',  color: 'var(--chart-2)', format: fmtInt },
	{ key: 'temperature', label: 'Temperature',   short: 'Temp',   color: 'var(--chart-3)', format: fmtTemp },
	{ key: 'humidity',    label: 'Humidity',      short: 'Hum',    color: 'var(--chart-6)', format: fmtHumidity },
	{ key: 'light',       label: 'Light',         short: 'Light',  color: 'var(--chart-7)', format: fmtLight },
	{ key: 'errors',      label: 'Errors',        short: 'Errors', color: 'var(--chart-4)', format: fmtInt },
	{ key: 'warnings',    label: 'Warnings',      short: 'Warn',   color: 'var(--chart-5)', format: fmtInt },
];

export const metricMap = Object.fromEntries(metrics.map((m) => [m.key, m])) as Record<MetricKey, MetricDef>;