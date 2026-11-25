<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import Button from '#lib/components/ui/button/button.svelte';
    import { RiArrowRightUpLine } from 'remixicon-svelte';
</script>

<Card.Root class="h-full gap-2 py-2">
	<Card.Header class="border-b [.border-b]:pb-2">
		<div class="flex items-center justify-between">
			<Card.Title class="text-base font-medium">Mini-Map</Card.Title>
			<Button variant="ghost" size="icon-sm" class="size-6 p-0" href="/map"><RiArrowRightUpLine /></Button>
		</div>
	</Card.Header>
	<Card.Content>
	</Card.Content>
	<Card.Footer>
	</Card.Footer>
</Card.Root>
