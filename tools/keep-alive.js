/**
 * Railway Free プラン用 Keep-Alive スクリプト
 * 定期的にAPIにリクエストを送ってスリープを防ぐ
 */

const RAILWAY_URL = process.env.RAILWAY_URL || 'https://your-app.railway.app';
const PING_INTERVAL = 10 * 60 * 1000; // 10分間隔
const HEALTH_ENDPOINT = '/health';

async function pingServer() {
  try {
    const response = await fetch(`${RAILWAY_URL}${HEALTH_ENDPOINT}`, {
      method: 'GET',
      headers: {
        'User-Agent': 'KeepAlive-Bot/1.0'
      }
    });
    
    if (response.ok) {
      console.log(`✅ [${new Date().toISOString()}] Server is alive`);
    } else {
      console.log(`⚠️ [${new Date().toISOString()}] Server responded with ${response.status}`);
    }
  } catch (error) {
    console.error(`❌ [${new Date().toISOString()}] Failed to ping server:`, error.message);
  }
}

// 定期実行
console.log(`🚀 Starting keep-alive for ${RAILWAY_URL}`);
console.log(`📡 Pinging every ${PING_INTERVAL / 60000} minutes`);

setInterval(pingServer, PING_INTERVAL);

// 初回実行
pingServer();