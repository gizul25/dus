<script lang="ts">
	import * as Card from '#lib/components/ui/card';
	import * as Table from '#lib/components/ui/table';
	import * as Select from '#lib/components/ui/select';
	import { Checkbox } from '#lib/components/ui/checkbox';
	import type { Desk, MetricKey, Timeframe } from './types';
	import { metrics } from './metrics';

	interface Props {
		desks: Desk[];
		currentDeskId: string | null;
		selectedIds: string[];
		activeMetrics: MetricKey[];
		timeframe: Timeframe;
		onToggleRow: (id: string) => void;
		onToggleAll: (checked: boolean) => void;
		onToggleMetric: (key: MetricKey) => void;
		onTimeframeChange: (tf: Timeframe) => void;
	}
	let {
		desks,
		currentDeskId,
		selectedIds,
		activeMetrics,
		timeframe,
		onToggleRow,
		onToggleAll,
		onToggleMetric,
		onTimeframeChange
	}: Props = $props();

	const allSelected = $derived(desks.length > 0 && selectedIds.length === desks.length);
	const someSelected = $derived(selectedIds.length > 0 && !allSelected);

	const checkboxBorder = 'border-muted-foreground/60 dark:border-muted-foreground/50';

	const timeframeLabels: Record<Timeframe, string> = {
		today: 'Today',
		week: 'Last 7 days',
		month: 'Last 30 days',
		all: 'All time'
	};
</script>

<Card.Root>
	<Card.Header>
		<div class="flex flex-wrap items-center justify-between gap-3">
			<div class="flex items-baseline gap-2">
				<Card.Title class="text-sm">Desks in the system</Card.Title>
				<span class="text-xs tabular-nums text-muted-foreground">
					{selectedIds.length} / {desks.length} selected
				</span>
			</div>

			<Select.Root
				type="single"
				value={timeframe}
				onValueChange={(v) => v && onTimeframeChange(v as Timeframe)}
			>
				<Select.Trigger class="h-8 w-36 text-xs">
					{timeframeLabels[timeframe]}
				</Select.Trigger>
				<Select.Content>
					{#each Object.entries(timeframeLabels) as [value, label] (value)}
						<Select.Item value={value}>{label}</Select.Item>
					{/each}
				</Select.Content>
			</Select.Root>
		</div>
	</Card.Header>

	<Card.Content>
		<Table.Root>
			<Table.Header>
				<Table.Row>
					<Table.Head class="w-8">
						<span class="inline-flex size-4 shrink-0 items-center justify-center">
							<Checkbox
								class={checkboxBorder}
								checked={allSelected}
								indeterminate={someSelected}
								onCheckedChange={(c) => onToggleAll(c === true)}
								aria-label="Select all desks"
							/>
						</span>
					</Table.Head>
					<Table.Head class="whitespace-nowrap text-[10px] font-semibold uppercase tracking-widest">
						Desk
					</Table.Head>
					<Table.Head class="whitespace-nowrap text-[10px] font-semibold uppercase tracking-widest">
						Occupation
					</Table.Head>
					{#each metrics as m (m.key)}
						<Table.Head
							class="whitespace-nowrap text-right text-[10px] font-semibold uppercase tracking-widest"
						>
							<div
								class="flex w-full cursor-pointer select-none items-center justify-end gap-1.5"
								title="Show “{m.label}” in the chart"
							>
								<span class="inline-flex size-4 shrink-0 items-center justify-center">
									<Checkbox
										class={checkboxBorder}
										checked={activeMetrics.includes(m.key)}
										onCheckedChange={() => onToggleMetric(m.key)}
									/>
								</span>
								<span class="leading-none">{m.short}</span>
							</div>
						</Table.Head>
					{/each}
				</Table.Row>
			</Table.Header>

			<Table.Body>
				{#each desks as desk (desk.id)}
					<Table.Row
						class={desk.id === currentDeskId
							? 'bg-primary/5 shadow-[inset_3px_0_0_var(--primary)]'
							: ''}
					>
						<Table.Cell>
							<span class="inline-flex size-4 shrink-0 items-center justify-center">
								<Checkbox
									class={checkboxBorder}
									checked={selectedIds.includes(desk.id)}
									onCheckedChange={() => onToggleRow(desk.id)}
									aria-label={`Select ${desk.id}`}
								/>
							</span>
						</Table.Cell>
						<Table.Cell class="whitespace-nowrap font-semibold tabular-nums">
							{desk.id}
						</Table.Cell>
						<Table.Cell class="whitespace-nowrap">
							{#if desk.occupied}
								<span
									class="inline-block rounded-full border border-destructive/30 bg-destructive/15 px-2.5 py-1 text-[10px] font-bold tracking-wider text-destructive"
								>
									OCCUPIED
								</span>
							{:else}
								<span
									class="inline-block rounded-full border border-emerald-500/30 bg-emerald-500/15 px-2.5 py-1 text-[10px] font-bold tracking-wider text-emerald-600 dark:text-emerald-400"
								>
									FREE
								</span>
							{/if}
						</Table.Cell>
						{#each metrics as m (m.key)}
							<Table.Cell class="whitespace-nowrap text-right tabular-nums text-foreground/80">
								{m.format(desk[m.key])}
							</Table.Cell>
						{/each}
					</Table.Row>
				{/each}
			</Table.Body>
		</Table.Root>
	</Card.Content>
</Card.Root>