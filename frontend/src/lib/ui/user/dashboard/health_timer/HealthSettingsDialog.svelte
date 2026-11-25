<script lang="ts">
	import * as Dialog from '#lib/components/ui/dialog/index.js';
	import * as Field from '#lib/components/ui/field/index.js';
	import { Button, buttonVariants } from '#lib/components/ui/button/index.js';
	import { Input } from '#lib/components/ui/input/index.js';
	import { Label } from '#lib/components/ui/label/index.js';


    let { open = $bindable() } = $props();
	async function onSubmit() {
        // change password
	}
</script>

<Dialog.Root bind:open>
	<form>
		<Dialog.Content class="sm:max-w-sm">
			<Dialog.Header>
				<Dialog.Title>Change Password</Dialog.Title>
			</Dialog.Header>
			<Field.Group>
				<Field.Field>
					<Label for="old-password">Old password</Label>
					<Input id="old-password" type="password" />
				</Field.Field>
				<Field.Field>
					<Label for="new-password">New password</Label>
					<Input id="new-password" type="password" />
				</Field.Field>
			</Field.Group>
			<Dialog.Footer>
				<Dialog.Close type="button" class={buttonVariants({ variant: 'outline' })}>
					Cancel
				</Dialog.Close>
				<Button type="submit" onclick={onSubmit}>Change password</Button>
			</Dialog.Footer>
		</Dialog.Content>
	</form>
</Dialog.Root>
