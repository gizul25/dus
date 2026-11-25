<script lang="ts">
    import { onMount } from 'svelte';
    import * as Sidebar from "#lib/components/ui/sidebar/index.js";
    import AppSidebar from "#lib/ui/user/layout/AppSidebar.svelte";
    import NotificationPopover from '#lib/ui/user/layout/NotificationPopover.svelte'; 

    let { children } = $props();
    let user = $state(null);
	let errorMessage = $state('');

    onMount(async () => {
		try {
			const response = await fetch('/api/user/me', { credentials: 'include' });

			const data = await response.json();

			if (!response.ok) {
				errorMessage = data.detail || 'Could not authenticate';
				return;
			}

			user = data;
		} 
        catch (error) {
			errorMessage = 'Could not connect to the server';
		}
	});
</script>

{#if user}


<Sidebar.Provider open={false}>
  <AppSidebar {user} />
  <Sidebar.Inset class="bg-muted">
    <header class="flex h-10 items-center px-2 justify-between">
        <Sidebar.Trigger />
        <NotificationPopover />
    </header>
    <main class="flex-1 px-10 pb-6">
        {@render children?.()}
    </main>
  </Sidebar.Inset>
</Sidebar.Provider>


{:else if errorMessage}
		<p>{errorMessage}</p>
{:else}
		<p>Loading...</p>
{/if}