<script lang="ts">
	import * as Card from '#lib/components/ui/card';
	import * as ToggleGroup from '#lib/components/ui/toggle-group';
	import ColumnChart, { type ChartGroup, type ChartSeries } from './ColumnChart.svelte';
	import type { Desk, MetricKey } from './types';
	import { metrics } from './metrics';

	interface Props {
		desks: Desk[];
		currentDeskId: string | null;
		activeMetrics: MetricKey[];
		maxByMetric: Record<MetricKey, number>;
		onMetricsChange: (keys: MetricKey[]) => void;
	}
	let { desks, currentDeskId, activeMetrics, maxByMetric, onMetricsChange }: Props = $props();

	const groups = $derived<ChartGroup[]>(
		desks.map((d) => ({
			id: d.id,
			label: d.id,
			highlight: d.id === currentDeskId,
			values: Object.fromEntries(metrics.map((m) => [m.key, d[m.key]]))
		}))
	);

	const series = $derived<ChartSeries[]>(
		metrics
			.filter((m) => activeMetrics.includes(m.key))
			.map((m) => ({ key: m.key, label: m.label, color: m.color, format: m.format }))
	);
</script>

<Card.Root>
	<Card.Header>
		<div class="flex items-baseline justify-between gap-3">
			<Card.Title class="text-sm">Comparison</Card.Title>
			<span class="text-xs tabular-nums text-muted-foreground">
				{desks.length} desk(s)
			</span>
		</div>
	</Card.Header>

	<Card.Content>
		{#if desks.length === 0}
			<p class="my-8 text-center text-[13px] text-muted-foreground">
				Select at least one desk in the table to visualize it.
			</p>
		{:else if activeMetrics.length === 0}
			<p class="my-8 text-center text-[13px] text-muted-foreground">
				Select at least one topic in the table header.
			</p>
		{:else}
			<ColumnChart {groups} {series} max={maxByMetric} />
		{/if}

		<div class="mt-4 border-t border-border pt-3.5">
			<ToggleGroup.Root
				type="multiple"
				value={activeMetrics}
				onValueChange={(v) => onMetricsChange(v as MetricKey[])}
				variant="outline"
				size="sm"
				class="flex flex-wrap gap-1.5"
			>
				{#each metrics as m (m.key)}
					<ToggleGroup.Item value={m.key} class="rounded-full text-[11px]">
						<span
							class="h-2 w-2 rounded-full"
							class:opacity-30={!activeMetrics.includes(m.key)}
							style={`background:${m.color}`}
						/>
						{m.label}
					</ToggleGroup.Item>
				{/each}
			</ToggleGroup.Root>
		</div>
	</Card.Content>
</Card.Root>
