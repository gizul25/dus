<script lang="ts">
	import * as Card from '#lib/components/ui/card/index.js';
	import DeskHeight from './DeskHeight.svelte';
	import Profiles from './Profiles.svelte';
	import Separator from '../../../../components/ui/separator/separator.svelte';
</script>

<Card.Root class="h-full gap-2 py-2">
	<Card.Header class="border-b [.border-b]:pb-2">
		<Card.Title class="text-base font-medium">Desk Height</Card.Title>
	</Card.Header>
	<Card.Content class="flex flex-col gap-4">
		<DeskHeight />
		<Separator />
		<Profiles />
	</Card.Content>
	<Card.Footer></Card.Footer>
</Card.Root>
