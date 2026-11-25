<script lang="ts">
	import Button from '#lib/components/ui/button/button.svelte';
	import * as Card from '#lib/components/ui/card/index.js';
	import Separator from '../../../../components/ui/separator/separator.svelte';
	import AvailabilitySelect from './AvailabilitySelect.svelte';

</script>

<Card.Root class="h-full gap-2 py-2">
	<Card.Header class="border-b [.border-b]:pb-2">
		<Card.Title class="text-base font-medium">My Session</Card.Title>
	</Card.Header>
	<Card.Content class="flex flex-col gap-4">
		<div class="flex flex-col items-center">
			<p class="font-semibold text-2xl">Desk B019</p>
			<p>Checked-in</p>
		</div>
		<Separator />
		<div class="flex flex-col gap-4">
			<div class="flex justify-between">
				<p>Session time</p>
				<p class="tabular-nums">08:23</p>
			</div>
			<div class="flex justify-between">
				<p>Availability</p>
				<AvailabilitySelect />
			</div>
            <Button class="w-40 self-center">Check out</Button>
		</div>
	</Card.Content>
	<Card.Footer />
</Card.Root>
