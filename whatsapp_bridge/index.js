const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const axios = require('axios');

const GATEWAY_URL = process.env.NOIR_GATEWAY_URL || "https://noir-agent-gateway.si-umkm-ikm-pbd.workers.dev";
const API_KEY = process.env.NOIR_API_KEY || "NOIR_SOVEREIGN_KEY_V72";

// Tentukan device_id yang ingin dikontrol via WA (bisa HP atau PC)
const TARGET_DEVICE_ID = "NOIR_PC_CORE"; 

console.log("Initializing WhatsApp Bridge...");

const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

client.on('qr', (qr) => {
    console.log('\n--- SCAN THIS QR CODE WITH WHATSAPP ---');
    qrcode.generate(qr, {small: true});
});

client.on('ready', () => {
    console.log('\n✅ NOIR WhatsApp Bridge is READY!');
    console.log('Send commands like: !pc echo "hello" or !pc shell whoami');
});

client.on('message', async msg => {
    const text = msg.body.trim();
    
    // Command format: !pc <cmd_type> <parameters>
    if (text.startsWith('!pc ')) {
        const parts = text.slice(4).split(' ');
        const cmdType = parts[0];
        const params = parts.slice(1).join(' ');
        
        console.log(`[WA] Received command: ${cmdType} | params: ${params}`);
        msg.reply(`⏳ Executing ${cmdType} on PC...`);
        
        try {
            // Queue command to Cloudflare Gateway
            const response = await axios.post(`${GATEWAY_URL}/agent/command`, {
                device_id: TARGET_DEVICE_ID,
                action: { type: cmdType, params: { cmd: params } }
            }, {
                headers: { 'Authorization': `Bearer ${API_KEY}` }
            });
            
            if (response.status === 200) {
                msg.reply(`✅ Command queued in Cloud Gateway! ID: ${response.data.command_id}`);
            }
        } catch (error) {
            console.error(error);
            msg.reply(`❌ Failed to send command to gateway.`);
        }
    }
});

client.initialize();
