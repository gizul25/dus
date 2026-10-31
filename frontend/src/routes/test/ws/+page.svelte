<script>
    let text = $state("");
	let msg = $state("");

	var ws = new WebSocket('ws://localhost:8080/ws');
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