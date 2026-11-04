<script lang="ts">
    import { goto } from '$app/navigation'
    import * as Card from '#lib/components/ui/card/index.ts';
    import * as ToggleGroup from '#lib/components/ui/toggle-group/index.ts'
    import { Input } from '#lib/components/ui/input/index.ts';
    import { Label } from '#lib/components/ui/label/index.ts';
    import { Checkbox } from '#lib/components/ui/checkbox/index.ts';
    import { Button } from '#lib/components/ui/button/index.ts';

    let email = $state('');
    let password = $state('');
    let rememberMe = $state(false);
    let mode = $state<'user' | 'admin'>('user');
    let errorMessage = $state('');


    async function handleLogin(event) {
        event.preventDefault();
        errorMessage = '';

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    remember_me: rememberMe,
                    mode: mode
                    })
            });

            const data = await response.json();

            if (!response.ok) {
                errorMessage = data.detail || "Login unsuccessful";
                return;
            }

            console.log('Login successful', data)

            if (mode === 'admin') {
                await goto('/admin/dashboard');
            }
            else 
                await goto('/placeholder_user_page');
        }

        catch (error) {
            errorMessage = error.message;
            console.error('Error:', error);

            // errorMessage = "Could not connect to the server";
            // console.error(error);
        }
    }
    
</script>

<main class="flex min-h-screen items-center justify-center bg-secondary"
      class:dark={mode === 'admin'}>

    <Card.Root class="w-full max-w-md">
        <Card.Header class="text-center">
            <Card.Title>
                Log In As
            </Card.Title>
        </Card.Header>
        <Card.Content>
            <form onsubmit={handleLogin} class="space-y-6">
            <div class="flex justify-center pb-6">
                <ToggleGroup.Root type="single" variant="outline" value={mode}
                                  onValueChange={(value) => { if (value === 'user' || value === 'admin') {mode = value}}}>
                    <ToggleGroup.Item value="user">User</ToggleGroup.Item>
                    <ToggleGroup.Item value="admin">Admin</ToggleGroup.Item>
                </ToggleGroup.Root>
            </div>

                <div class="space-y-2">
                    <Label for="email">Email</Label>
                    <Input id="email" type="email" required bind:value={email} />
                </div>
                
                <div class="space-y-2">
                    <Label for="password">Password</Label>
                    <Input id="password" type="password" required bind:value={password} />
                </div>
                

                <div class="space-y-2">
                    <Label for="rememberMe"> 
                        <Checkbox id="rememberMe" bind:checked={rememberMe} />
                        Remember me
                    </Label>
                </div>

                {#if errorMessage}
                    <p role="alert" class="text-center text-destructive">{errorMessage}</p>
                {/if}

                <div class="flex justify-center">
                    <Button type="submit">Log In</Button>
                </div>
            </form>
        </Card.Content>
    </Card.Root>
</main>


