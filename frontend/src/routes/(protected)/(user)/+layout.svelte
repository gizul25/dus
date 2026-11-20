<script lang="ts">
    import { onMount } from 'svelte';
    import * as Sidebar from "#lib/components/ui/sidebar/index.js";
    import AppSidebar from "#lib/ui/user/sidebar/AppSidebar.svelte";
	import { Inset } from '../../../lib/components/ui/sidebar';
    
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
  <Sidebar.Inset>
    <header class="flex h-10 items-center px-2">
        <Sidebar.Trigger />
    </header>
    <main class="flex-1 px-6 pb-6">
        {@render children?.()}
    </main>
  </Sidebar.Inset>
</Sidebar.Provider>


{:else if errorMessage}
		<p>{errorMessage}</p>
{:else}
		<p>Loading...</p>
{/if}