<script lang="ts">
	import Button from '#lib/components/ui/button/button.svelte';
	import { RiPauseLargeFill } from 'remixicon-svelte';

	let cx = 50;
	let cy = 50;
	let radius = 45;
	let strokeWidth = 8;
	let remainingPercentage = 66;

	let totalDuration;
	let timeRemaining;
</script>

<div class="flex w-full flex-col items-center gap-4">
	<div class="relative w-full">
		<svg viewBox={`0 0 100 100`} class="h-48 w-full -rotate-90" role="img" aria-label="Timer">
			<circle {cx} {cy} r={radius} fill="none" stroke-width={strokeWidth} class="stroke-muted" />
			<circle
				{cx}
				{cy}
				transform="translate(0 100) scale(1 -1)"
				pathLength="100"
				stroke-dasharray={`${remainingPercentage} 100`}
				r={radius}
				fill="none"
				stroke-width={strokeWidth}
				class="stroke-primary transition-[stroke-dasharray] duration-300"
			/>
		</svg>
		<div class="absolute inset-0 flex flex-col items-center justify-center">
			<p class="text-sm text-muted-foreground">Sitting</p>
			<p class="text-4xl font-semibold tabular-nums">13:00</p>
			<Button variant="ghost" size="icon" class="font-bold">| |</Button>
		</div>
	</div>

	
	<Button variant="outline" class="">+ 5 min</Button>
	
</div>
