import { serve } from "https://deno.land/std@0.208.0/http/server.ts";

const clients = new Set<WebSocket>();

let ralik1Active = false;
let ralik2Active = false;
let ralik1Value = 29;
let ralik2Value = 29;

function broadcast(message: string) {
  for (const client of clients) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  }
}

setInterval(() => {
  let changed = false;
  
  if (ralik1Active) {
    ralik1Value--;
    if (ralik1Value < 0) ralik1Value = 29;
    changed = true;
  }
  
  if (ralik2Active) {
    ralik2Value--;
    if (ralik2Value < 0) ralik2Value = 29;
    changed = true;
  }
  
  if (changed) {
    broadcast(JSON.stringify({
      type: "state",
      ralik1Active, ralik1Value,
      ralik2Active, ralik2Value
    }));
  }
}, 1000);

serve(async (req) => {
  if (req.headers.get("upgrade") === "websocket") {
    const { socket, response } = Deno.upgradeWebSocket(req);
    
    clients.add(socket);
    
    socket.send(JSON.stringify({
      type: "state",
      ralik1Active, ralik1Value,
      ralik2Active, ralik2Value
    }));
    
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "command") {
          if (data.ralik1Active !== undefined) {
            ralik1Active = data.ralik1Active;
            if (ralik1Active) ralik1Value = 29;
          }
          if (data.ralik2Active !== undefined) {
            ralik2Active = data.ralik2Active;
            if (ralik2Active) ralik2Value = 29;
          }
          if (data.clear) {
            ralik1Active = false;
            ralik2Active = false;
            ralik1Value = 29;
            ralik2Value = 29;
          }
          
          broadcast(JSON.stringify({
            type: "state",
            ralik1Active, ralik1Value,
            ralik2Active, ralik2Value
          }));
        }
      } catch (e) {}
    };
    
    socket.onclose = () => {
      clients.delete(socket);
    };
    
    return response;
  }
  
  return new Response(`
    <html>
    <body style="background:#1a1a1a; color:#00ff00; text-align:center; padding:50px;">
      <h1 style="color:#ff4444;">🔴 STALCRAFT RALIK СЕРВЕР</h1>
      <p>Ралик 1: ${ralik1Active ? "АКТИВЕН " + ralik1Value : "ОСТАНОВЛЕН"}</p>
      <p>Ралик 2: ${ralik2Active ? "АКТИВЕН " + ralik2Value : "ОСТАНОВЛЕН"}</p>
      <p>Клиентов: ${clients.size}</p>
    </body>
    </html>
  `, { headers: { "content-type": "text/html" } });
});
