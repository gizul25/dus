<script lang="ts">
	import * as Popover from '#lib/components/ui/popover/index.js';
    import { RiInboxLine } from "remixicon-svelte";
	import ScrollArea from '#lib/components/ui/scroll-area/scroll-area.svelte';
</script>

<Popover.Root>
	<Popover.Trigger class="flex items-center justify-center"><RiInboxLine class="size-4" /></Popover.Trigger>
	<Popover.Content side="left" align="start">
        <h1>Notifications</h1>
        <ScrollArea>

        </ScrollArea>
    </Popover.Content>
</Popover.Root>
