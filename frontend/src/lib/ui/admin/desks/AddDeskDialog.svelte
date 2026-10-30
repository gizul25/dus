<script lang="ts">
	import * as Dialog from '#lib/components/ui/dialog/index.js';
	import * as Field from '#lib/components/ui/field/index.js';
	import { Button, buttonVariants } from '#lib/components/ui/button/index.js';
	import { Input } from '#lib/components/ui/input/index.js';
	import { Label } from '#lib/components/ui/label/index.js';

	let { desk = $bindable(), isOpen = $bindable(), createNewDesk } = $props();

	function onSubmit() {
		const res = createNewDesk(desk);
		if (res) {
			isOpen = false;
		}
	}
</script>

<Dialog.Root bind:open={isOpen}>
	<form>
		<Dialog.Content class="sm:max-w-sm">
			<Dialog.Header>
				<Dialog.Title>Add desk</Dialog.Title>
			</Dialog.Header>
			<Field.Group>
				<Field.Field>
					<Label for="name-1">Name</Label>
					<Input id="name-1" name="name" bind:value={desk.name} />
				</Field.Field>
			</Field.Group>
			<Dialog.Footer>
				<Dialog.Close type="button" class={buttonVariants({ variant: 'outline' })}>
					Cancel
				</Dialog.Close>
				<Button type="submit" onclick={onSubmit}>Create new desk</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</form>
</Dialog.Root>
