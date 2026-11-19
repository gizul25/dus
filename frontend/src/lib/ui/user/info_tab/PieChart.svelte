<script lang="ts">
	interface Props {
		width?: number;
		height?: number;
		radius?: number;
		data: number[];
		background?: string;
		strokeWidth?: number;
	}

	let {
		width = 100,
		height = 100,
		radius = 40,
		data,
		background = '000000',
		strokeWidth = 14
	}: Props = $props();

	let colors: string[] = $state([]);

	function getCssColors(variableNames: string[]): string[] {
		if (typeof window === 'undefined') return [];

		const styles = getComputedStyle(document.documentElement);
		return variableNames.map((name) => styles.getPropertyValue(name).trim()).filter(Boolean);
	}

	$effect(() => {
		colors = getCssColors(['--chart-1', '--chart-2', '--chart-3', '--chart-4', '--chart-5']);
	});

	const cx = $derived(width / 2);
	const cy = $derived(height / 2);
	const C = $derived(2 * Math.PI * radius);
	const total = $derived(data.reduce((a, b) => a + b, 0));

	const slices = $derived.by(() => {
		let cumulative = 0;
		return data.map((value, i) => {
			const start = cumulative;
			cumulative += value;
			return { id: i, value, start, color: colors[i % colors.length] };
		});
	});
</script>

<svg
	viewBox={`0 0 ${width} ${height}`}
	class="h-32 w-32 -rotate-90"
	role="img"
	aria-label="Pie chart"
>
	{#if total > 0}
		<circle {cx} {cy} r={radius} fill="none" stroke={background} stroke-width={strokeWidth} />

		{#each slices as slice (slice.id)}
			<circle
				{cx}
				{cy}
				r={radius}
				fill="none"
				stroke={slice.color}
				stroke-width={strokeWidth}
				stroke-dasharray={`${(slice.value / total) * C} ${C}`}
				stroke-dashoffset={-(slice.start / total) * C}
				class="transition-[stroke-dasharray] duration-300"
			/>
		{/each}
	{/if}
</svg>
