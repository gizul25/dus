<script lang="ts">
  import { onMount } from 'svelte';
  import { Button } from '#lib/components/ui/button';
  import * as Card from '#lib/components/ui/card';
  import { dashboard } from './dashboard.svelte';
  import UserSummaryCard from './UserSummaryCard.svelte';
  import DeskTable from './DeskTable.svelte';
  import ComparisonPanel from './ComparisonPanel.svelte';

  onMount(() => {
    dashboard.load();
    document.addEventListener('visibilitychange', dashboard.handleVisibility);
    return () => {
      dashboard.stopPolling();
      document.removeEventListener('visibilitychange', dashboard.handleVisibility);
    };
  });
</script>

<svelte:head>
  <title>Desk usage overview</title>
</svelte:head>

<div class="min-h-screen bg-background p-6 text-foreground">
  {#if dashboard.loading}
    <div class="flex min-h-[60vh] items-center justify-center">
      <p class="text-sm text-muted-foreground">Loading info page</p>
    </div>
  {:else if dashboard.errorMessage}
    <Card.Root class="mx-auto mt-16 max-w-md text-center">
      <Card.Content class="p-6">
        <p class="mb-4 text-sm text-destructive">{dashboard.errorMessage}</p>
        <div class="flex justify-center gap-3">
          <Button onclick={dashboard.load}>Retry</Button>
          <Button variant="outline" href="/">Log in</Button>
        </div>
      </Card.Content>
    </Card.Root>
  {:else if dashboard.currentUser}
    <UserSummaryCard user={dashboard.currentUser} />

    <div class="grid grid-cols-1 gap-5 lg:grid-cols-[1.65fr_1fr]">
      <DeskTable
        desks={dashboard.desks}
        currentDeskId={dashboard.currentUser.deskId}
        selectedIds={dashboard.selectedIds}
        activeMetrics={dashboard.activeMetrics}
        onToggleRow={dashboard.toggleRow}
        onToggleAll={dashboard.toggleAll}
        onToggleMetric={dashboard.toggleMetric}
      />

      <ComparisonPanel
        desks={dashboard.selectedDesks}
        currentDeskId={dashboard.currentUser.deskId}
        activeMetrics={dashboard.activeMetrics}
        maxByMetric={dashboard.maxByMetric}
        onMetricsChange={dashboard.setActiveMetrics}
      />
    </div>
  {/if}
</div>