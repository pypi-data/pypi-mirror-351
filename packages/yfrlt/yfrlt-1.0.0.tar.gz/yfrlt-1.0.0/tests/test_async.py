#!/usr/bin/env python3
import asyncio
import yfrlt

async def test_async():
    print("🧪 Testing Async Client...")
    
    try:
        async with yfrlt.AsyncClient() as client:
            await client.subscribe(['JPY=X'])
            
            # count = 0
            async for data in client.stream():
                print(f"📊 {data.symbol}: ${data.price:.4f}")
                # count += 1
                # if count >= 5:  # Get 5 updates then stop
                #     break
                    
        print("✅ Async test completed!")
        
    except Exception as e:
        print(f"❌ Async test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_async())