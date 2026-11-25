<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import Button from '#lib/components/ui/button/button.svelte';
	import { RiSettings4Line } from 'remixicon-svelte';
    import Timer from './Timer.svelte';
</script>

<Card.Root class="h-full gap-2 py-2">
	<Card.Header class="border-b [.border-b]:pb-2">
		<div class="flex items-center justify-between">
			<Card.Title class="text-base font-medium">Health Timer</Card.Title>
			<Button onclick={() => true} variant="ghost" size="icon-sm" class="size-6 p-0"><RiSettings4Line /></Button>
		</div>
	</Card.Header>
	<Card.Content class="flex justify-center">
		<Timer />
	</Card.Content>
	<Card.Footer />
</Card.Root>
