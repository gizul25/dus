<script lang="ts">
	import * as Dialog from '#lib/components/ui/dialog/index.js';
	import * as Field from '#lib/components/ui/field/index.js';
	import { Button, buttonVariants } from '#lib/components/ui/button/index.js';
	import { Input } from '#lib/components/ui/input/index.js';
	import { Label } from '#lib/components/ui/label/index.js';

	let { user = $bindable(), isOpen = $bindable(), createNewUser } = $props();

	function onSubmit() {
		const res = createNewUser(user);
		if (res) {
			isOpen = false;
		}
	}
</script>

<Dialog.Root bind:open={isOpen}>
	<form>
		<Dialog.Content class="sm:max-w-sm">
			<Dialog.Header>
				<Dialog.Title>Add user</Dialog.Title>
			</Dialog.Header>
			<Field.Group>
				<Field.Field>
					<Label for="first-name-1">First name</Label>
					<Input id="first-name-1" name="first-name" bind:value={user.firstName} />
				</Field.Field>
				<Field.Field>
					<Label for="last-name-1">Last name</Label>
					<Input id="last-name-1" name="last-name" bind:value={user.lastName} />
				</Field.Field>
				<Field.Field>
					<Label for="email-1">Email</Label>
					<Input id="email-1" name="email" bind:value={user.email} />
				</Field.Field>
			</Field.Group>
			<Dialog.Footer>
				<Dialog.Close type="button" class={buttonVariants({ variant: 'outline' })}>
					Cancel
				</Dialog.Close>
				<Button type="submit" onclick={onSubmit}>Create new user</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</form>
</Dialog.Root>
