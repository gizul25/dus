<script lang="ts">
    import { Button } from '#lib/components/ui/button';

    let currentDeskId = $state<number | null>(1);
    let currentDesk = $derived(deskArray.find((desk) => desk.id === currentDeskId));
    let deskArray = [
        {id: 1, name: "Desk 1", occupiedByOthers: false},
        {id: 2, name: "Desk 2", occupiedByOthers: true},
        {id: 3, name: "Desk 3", occupiedByOthers: false}
    ];

    let isCheckingOut = $state(false);
    let checkoutError = $state<string | null>(null);
    async function handleCheckOut()
    {
        checkoutError = null;
        isCheckingOut = true;

        try{
            await new Promise<void>((resolve) => setTimeout(resolve, 800));
            currentDeskId = null;
        }
        catch {
            checkoutError = 'Could not get checkout details.';
        }
        finally{
            isCheckingOut = false;
        }
    }
</script>

<main class="space-y-6 p-4 md:mx-16">
    <h1 class="text-3xl font-semibold tracking-tight">Desk check in/out</h1>
    <h2 class="text-lg font-semibold">Current desk</h2>
    {#if currentDesk}
        <p>{currentDesk.name}</p>
        <Button type="button" onclick={handleCheckOut} disabled={isCheckingOut}>
            {isCheckingOut ? 'Checking out…' : 'Check out'}
        </Button>
        {#if checkoutError}
            <p role="alert">{checkoutError}</p>
        {/if}
    {:else}
        <p>No desk assigned. Tap your card at an available desk to check in.</p>
    {/if}
    <h2 class="text-lg font-semibold">Desk availability</h2>
    <ul>
        {#each deskArray as desk (desk.id)}
            <li class="flex items-center justify-between gap-4 border-b py-3">
                <p>{desk.name}</p>
                {#if desk.id === currentDeskId}
                    <p>Your desk</p>
                {:else if desk.occupiedByOthers}
                    <p>Occupied</p>
                {:else}
                    <p>Available</p>
                {/if}
            </li>
        {/each}
    </ul>
</main>