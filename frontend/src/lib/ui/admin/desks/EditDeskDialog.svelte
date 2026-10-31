<script lang="ts">
	import * as Dialog from '#lib/components/ui/dialog/index.js';
	import * as Field from '#lib/components/ui/field/index.js';
	import { Button, buttonVariants } from '#lib/components/ui/button/index.js';
	import { Input } from '#lib/components/ui/input/index.js';
	import { Label } from '#lib/components/ui/label/index.js';

	let { desk = $bindable(), isOpen = $bindable(), onSubmit } = $props();

	function _onSubmit() {
		const res = onSubmit(desk);
		if (res) {
			isOpen = false;
		}
	}
</script>

<Dialog.Root bind:open={isOpen}>
	<form>
		<Dialog.Content class="sm:max-w-sm">
			<Dialog.Header>
				<Dialog.Title>Edit desk</Dialog.Title>
			</Dialog.Header>
			<Field.Group>
				<Field.Field>
					<Label for="id-1">ID</Label>
					<Input id="id-1" name="id" bind:value={desk.id} disabled />
				</Field.Field>
				<Field.Field>
					<Label for="name-1">Name</Label>
					<Input id="name-1" name="name" bind:value={desk.name} />
				</Field.Field>
			</Field.Group>
			<Dialog.Footer>
				<Dialog.Close type="button" class={buttonVariants({ variant: 'outline' })}>
					Cancel
				</Dialog.Close>
				<Button type="submit" onclick={_onSubmit}>Edit desk</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</form>
</Dialog.Root>
