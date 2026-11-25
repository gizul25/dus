<script>
	import Button from '#lib/components/ui/button/button.svelte';
	import ScrollArea from '#lib/components/ui/scroll-area/scroll-area.svelte';
    import { RiSettings4Line, RiDeleteBinLine, RiPencilLine, RiAddCircleLine} from "remixicon-svelte";
    import AddProfileDialog from './AddProfileDialog.svelte';
	import EditProfileDialog from './EditProfileDialog.svelte';

    let isEditing = $state(false);
    let editProfileDialogOpen = $state(false);
    let addProfileDialogOpen = $state(false);

</script>

<div class="flex flex-col">
	<div class="flex items-center justify-between">
		<p class="font-medium">Saved Profiles</p>
		<div class="flex gap-1 pl-2">
            <Button onclick={() => ( addProfileDialogOpen = true)} variant="ghost" size="icon-sm" class="size-6"><RiAddCircleLine /></Button>
			<Button onclick={() => isEditing = !isEditing} variant="ghost" size="icon-sm" class="size-6" ><RiSettings4Line /></Button>
		</div>
	</div>

	<!-- List of profiles -->
	<ScrollArea class="max-h-[315px]">
		<div class="flex flex-col gap-2 p-2">
            <div class="flex items-center gap-1">
                <Button variant="secondary" class="flex-1 items-center justify-between rounded-md bg-muted p-4">
				<p>Sitting</p>
				<p>68 cm</p>
                </Button>
                {#if isEditing}
                <Button onclick={() => ( editProfileDialogOpen = true)} variant="ghost" size="icon-xs" class="text-muted-foreground hover:text-foreground"><RiPencilLine /></Button>
                <Button variant="ghost" size="icon-xs" class="text-muted-foreground hover:text-destructive"><RiDeleteBinLine /></Button>
                {/if}
            </div>
			<div class="flex items-center gap-1">
                <Button variant="secondary" class="flex-1 items-center justify-between rounded-md bg-muted p-4">
				<p>Standing</p>
				<p>68 cm</p>
                </Button>
                {#if isEditing}
                <Button onclick={() => ( editProfileDialogOpen = true)} variant="ghost" size="icon-xs"><RiPencilLine /></Button>
                <Button variant="ghost" size="icon-xs"><RiDeleteBinLine /></Button>
                {/if}
            </div>
		</div>
	</ScrollArea>
    <EditProfileDialog bind:open={editProfileDialogOpen} />
    <AddProfileDialog bind:open={addProfileDialogOpen} />
</div>
