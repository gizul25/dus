<script lang="ts">
	import * as Card from '#lib/components/ui/card';
	import { Separator } from '#lib/components/ui/separator';
	import PieChart from './PieChart.svelte';
	import type { CurrentUser } from './types';
	import { fmtDuration } from './metrics';

	interface Props {
		user: CurrentUser;
	}
	
	let { user }: Props = $props();

	const initials = $derived(
		user.name
			.split(' ')
			.map((p) => p[0])
			.join('')
			.slice(0, 2)
			.toUpperCase()
	);
	const totalTracked = $derived(user.standingMin + user.sittingMin);
	const standShare = $derived(totalTracked > 0 ? (user.standingMin / totalTracked) * 100 : 0);
	const sitShare = $derived(100 - standShare);
</script>

{#snippet statChip(label: string, value: string, cls: string)}
	<div
		class="flex min-w-28 flex-col gap-1 rounded-lg border border-border bg-muted/50 px-3.5 py-2.5"
	>
		<span class="text-[10px] uppercase tracking-widest text-muted-foreground">{label}</span>
		<span class="text-lg font-semibold tabular-nums {cls}">{value}</span>
	</div>
{/snippet}

{#snippet legendRow(dot: string, label: string, value: string)}
	<div class="flex items-center gap-2">
		<span class="h-2.5 w-2.5 rounded-sm {dot}"></span>
		<span class="text-muted-foreground">{label}</span>
		<span class="font-semibold tabular-nums">{value}</span>
	</div>
{/snippet}

<Card.Root class="mb-5">
	<Card.Content class="flex flex-wrap items-center gap-5 p-5 md:gap-8">
		<div class="flex min-w-56 flex-1 items-center gap-3">
			<div
				class="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-primary text-sm font-bold text-primary-foreground"
			>
				{initials}
			</div>
			<div>
				<h1 class="text-lg font-semibold leading-tight">{user.name}</h1>
				<p class="mt-0.5 text-xs text-muted-foreground">Personal desk usage · today</p>
			</div>
		</div>

		<div class="flex flex-wrap gap-3">
			{@render statChip('Standing time', fmtDuration(user.standingMin), 'text-chart-2')}
			{@render statChip('Sitting time', fmtDuration(user.sittingMin), 'text-chart-1')}
			{@render statChip(
				'Current desk',
				user.deskId ?? 'none',
				user.deskId ? '' : 'text-muted-foreground'
			)}
		</div>

		<div class="flex w-full items-center justify-center gap-6 md:justify-start">
			<div class="relative flex shrink-0 items-center justify-center">
				<PieChart
					width={100}
					height={100}
					radius={40}
					background="#FFFFFF"
					data={[standShare, sitShare]}
				/>
				<div
					class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center"
				>
					<span class="text-base font-bold tabular-nums leading-none">{standShare.toFixed(0)}%</span
					>
					<span class="mt-1 text-[9px] uppercase tracking-widest text-muted-foreground"
						>standing</span
					>
				</div>
			</div>

			<div class="flex flex-col gap-2 text-xs">
				{@render legendRow('bg-chart-2', 'Standing', fmtDuration(user.standingMin))}
				{@render legendRow('bg-chart-1', 'Sitting', fmtDuration(user.sittingMin))}
				<Separator class="my-1" />
				<div class="flex items-center gap-2">
					<span class="text-muted-foreground">Total</span>
					<span class="font-semibold tabular-nums">{fmtDuration(totalTracked)}</span>
				</div>
			</div>
		</div>
	</Card.Content>
</Card.Root>
