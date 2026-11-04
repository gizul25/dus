<script lang="ts">
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import type { LayoutProps } from '../../$types';

    let { children }: LayoutProps = $props();
    let loading = $state(true);

    onMount(async () => {
        try {
            const response = await fetch('/api/user/me', {
                credentials: 'include'
            });

            if (!response.ok) { await goto('/login');
                await goto('/login')
                return;
            }

            const user = await response.json();

            if (user.role !== 'admin' || user.mode !== 'admin') {
                await goto('/test_user_page');
                return;
            }

            loading = false;
            }
        
        catch (error) {
            console.error('Admin authorization fialed', error);
            await goto('/login');
        }
    });
</script>

{#if loading}
    <p>Authorising...</p>
{:else}
    {@render children()}
{/if}