<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import type { LayoutProps } from '../$types';

    let { children }: LayoutProps = $props();
    let loading = $state(true);

    onMount(async () => {
        try {
            const response = await fetch('http://localhost:8000/auth/me', { credentials: 'include'});

            if (response.status === 401) {
                await goto('/login');
                return;
            }

            if (!response.ok) {
                throw new Error('Could not verify authentication')
            }

            loading = false;
        }
        catch (error) {
            console.error('Authentication check failed:', error);
            await goto('/login');
        }
    });
</script>

{#if loading}
    <p>Authenticating...</p>
{:else}
    {@render children()}
{/if}