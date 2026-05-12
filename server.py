import asyncio
import json
from websockets.asyncio.server import serve

connected_clients = set()
ralik1_active = False
ralik2_active = False
ralik1_value = 29
ralik2_value = 29

async def broadcast(message):
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

async def handler(websocket):
    global ralik1_active, ralik2_active, ralik1_value, ralik2_value
    connected_clients.add(websocket)
    print(f"✅ Клиент подключился. Всего: {len(connected_clients)}")
    
    try:
        # Отправляем текущее состояние
        await websocket.send(json.dumps({
            'ralik1_active': ralik1_active,
            'ralik1_value': ralik1_value,
            'ralik2_active': ralik2_active,
            'ralik2_value': ralik2_value
        }))
        
        # Слушаем сообщения
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"📨 Получено: {data}")
                
                cmd = data.get('cmd')
                if cmd == 'ralik1_toggle':
                    ralik1_active = not ralik1_active
                    if ralik1_active:
                        ralik1_value = 29
                    print(f"🔴 Ралик1: {'ВКЛ' if ralik1_active else 'ВЫКЛ'}")
                    
                elif cmd == 'ralik2_toggle':
                    ralik2_active = not ralik2_active
                    if ralik2_active:
                        ralik2_value = 29
                    print(f"🔵 Ралик2: {'ВКЛ' if ralik2_active else 'ВЫКЛ'}")
                    
                elif cmd == 'clear':
                    ralik1_active = False
                    ralik2_active = False
                    ralik1_value = 29
                    ralik2_value = 29
                    print(f"🔄 Все очищено")
                
                # Рассылаем новое состояние
                await broadcast(json.dumps({
                    'ralik1_active': ralik1_active,
                    'ralik1_value': ralik1_value,
                    'ralik2_active': ralik2_active,
                    'ralik2_value': ralik2_value
                }))
                
            except json.JSONDecodeError:
                print(f"❌ Неверный JSON: {message}")
            except Exception as e:
                print(f"❌ Ошибка обработки: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")
    finally:
        connected_clients.discard(websocket)
        print(f"❌ Клиент отключился. Всего: {len(connected_clients)}")

async def timer_updater():
    global ralik1_value, ralik2_value, ralik1_active, ralik2_active
    while True:
        await asyncio.sleep(1)
        changed = False
        
        if ralik1_active:
            ralik1_value -= 1
            if ralik1_value < 0:
                ralik1_value = 29
            changed = True
            
        if ralik2_active:
            ralik2_value -= 1
            if ralik2_value < 0:
                ralik2_value = 29
            changed = True
            
        if changed:
            await broadcast(json.dumps({
                'ralik1_active': ralik1_active,
                'ralik1_value': ralik1_value,
                'ralik2_active': ralik2_active,
                'ralik2_value': ralik2_value
            }))

async def main():
    print("🚀 Ralik WebSocket сервер запущен на порту 10000")
    async with serve(handler, "0.0.0.0", 10000):
        asyncio.create_task(timer_updater())
        print("✅ Сервер готов к работе")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
