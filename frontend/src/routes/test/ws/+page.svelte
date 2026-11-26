<script>
    let text = $state("");
	let msg = $state("");

	const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
	var ws = new WebSocket(`${protocol}//${location.host}/ws`);
	ws.onmessage = function (event) {
		msg = event.data
        console.log('onmessage', event)
	};

	function sendMessage() {
		ws.send(text);
	}
</script>

<p>{msg}</p>
<input bind:value={text} />
<button onclick={sendMessage}>Send message</button>
