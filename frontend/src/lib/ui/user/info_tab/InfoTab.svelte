<script lang="ts">
	import { onMount } from 'svelte';
	import { Button } from '#lib/components/ui/button';
	import * as Card from '#lib/components/ui/card';
	import { infoboard } from './infoboard.svelte';
	import UserSummaryCard from './UserSummaryCard.svelte';
	import DeskTable from './DeskTable.svelte';
	import ComparisonPanel from './ComparisonPanel.svelte';

	onMount(() => {
		infoboard.load();
		document.addEventListener('visibilitychange', infoboard.handleVisibility);
		return () => {
			infoboard.stopPolling();
			document.removeEventListener('visibilitychange', infoboard.handleVisibility);
		};
	});
</script>

<svelte:head>
	<title>Infoboard · desk usage</title>
</svelte:head>

{#if infoboard.currentUser?.status === 'away'}
	<div
		class="fixed inset-0 z-50 flex items-center justify-center bg-background/95 backdrop-blur-sm"
		role="dialog"
		aria-modal="true"
		aria-labelledby="away-title"
	>
		<Card.Root class="mx-4 max-w-md">
			<Card.Content class="p-6 text-center">
				<p id="away-title" class="text-2xl font-bold">You're away</p>
				<p class="mt-2 text-sm text-muted-foreground">
					Your status is set to <strong>away</strong>. Update it on the dashboard to continue using
					the system.
				</p>
				<Button class="mt-5" href="/dashboard">Go to dashboard</Button>
			</Card.Content>
		</Card.Root>
	</div>
{/if}

<div class="min-h-screen bg-background p-6 text-foreground">
	{#if infoboard.loading}
		<div class="flex min-h-[60vh] items-center justify-center">
			<p class="text-sm text-muted-foreground">Loading info page</p>
		</div>
	{:else if infoboard.errorMessage}
		<Card.Root class="mx-auto mt-16 max-w-md text-center">
			<Card.Content class="p-6">
				<p class="mb-4 text-sm text-destructive">{infoboard.errorMessage}</p>
				<div class="flex justify-center gap-3">
					<Button onclick={infoboard.load}>Retry</Button>
					<Button variant="outline" href="/">Log in</Button>
				</div>
			</Card.Content>
		</Card.Root>
	{:else if infoboard.currentUser}
		<UserSummaryCard
			user={infoboard.currentUser}
			sessionDurationMin={infoboard.sessionDurationMin}
		/>

		<div class="grid grid-cols-1 gap-5 lg:grid-cols-[1.65fr_1fr]">
			<DeskTable
				desks={infoboard.desks}
				currentDeskId={infoboard.currentUser.deskId}
				selectedIds={infoboard.selectedIds}
				activeMetrics={infoboard.activeMetrics}
				timeframe={infoboard.timeframe}
				onToggleRow={infoboard.toggleRow}
				onToggleAll={infoboard.toggleAll}
				onToggleMetric={infoboard.toggleMetric}
				onTimeframeChange={infoboard.setTimeframe}
			/>

			<ComparisonPanel
				desks={infoboard.selectedDesks}
				currentDeskId={infoboard.currentUser.deskId}
				activeMetrics={infoboard.activeMetrics}
				maxByMetric={infoboard.maxByMetric}
				timeframe={infoboard.timeframe}
				onMetricsChange={infoboard.setActiveMetrics}
			/>
		</div>
	{/if}
</div>