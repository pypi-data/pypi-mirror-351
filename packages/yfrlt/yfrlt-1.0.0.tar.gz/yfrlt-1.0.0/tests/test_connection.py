#!/usr/bin/env python3
import yfrlt
import time
import threading

def test_callback(data):
    print(f"✅ Received: {data.symbol} = ${data.price:.2f} ({data.change_percent:+.2f}%)")

print("🧪 Testing YFRLT Connection...")
print("Connecting to Yahoo Finance WebSocket v2...")

client = yfrlt.Client()
client.subscribe(['BTC-USD'], test_callback)

# Start in background thread
def run_client():
    try:
        client.start()
    except Exception as e:
        print(f"❌ Error: {e}")

thread = threading.Thread(target=run_client, daemon=True)
thread.start()

print("⏳ Waiting for data... (will run for 30 seconds)")
try:
    time.sleep(30)
    print("✅ Test completed!")
except KeyboardInterrupt:
    print("⏹️ Test stopped by user")
finally:
    client.stop()