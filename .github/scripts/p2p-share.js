// ==========================================
// M4Mental Hub - P2P WebRTC Warp Drop Engine
// ==========================================

// Live Link Interceptor Guard
window.addEventListener('click', function(e) {
  let target = e.target.closest('a');
  if (target && target.href) {
    if (target.href.includes('nullcpy/rvb')) {
      target.href = target.href.replace(/nullcpy\/rvb/g, 'm4mental/my-rvb-builder');
    }
    if (target.href.includes('nullcpy.github.io')) {
      target.href = target.href.replace(/nullcpy\.github\.io/g, 'm4mental.github.io');
    }
  }
}, true);

let peer = null, peerConn = null, myPinCode = '';
let incomingFileMeta = null, incomingChunks = [];
let html5QrScanner = null;

function generatePin() {
  return Math.floor(1000 + Math.random() * 9000).toString();
}

function openP2PModal() {
  let modal = document.getElementById('m4mP2PModal');
  if (!modal) {
    injectP2PModalDOM();
    modal = document.getElementById('m4mP2PModal');
  }
  if (modal) {
    modal.style.display = 'flex';
    modal.classList.add('m4m-active');
  }
  initP2PPeer();
}

function closeP2PModal() {
  stopCameraScanner();
  const modal = document.getElementById('m4mP2PModal');
  if (modal) {
    modal.style.display = 'none';
    modal.classList.remove('m4m-active');
  }
}

function copyMyPin() {
  const pinEl = document.getElementById('myPinDisplay');
  if (!pinEl) return;
  const pinText = pinEl.innerText.trim();
  if (pinText && pinText !== '----') {
    navigator.clipboard.writeText(pinText).then(() => {
      const toast = document.getElementById('p2pStatus');
      if (toast) toast.innerText = `📋 PIN ${pinText} copied to clipboard!`;
    }).catch(() => {});
  }
}

function copyShareLink() {
  const pinEl = document.getElementById('myPinDisplay');
  if (!pinEl) return;
  const pinText = pinEl.innerText.trim();
  if (pinText && pinText !== '----') {
    const link = `https://m4mental.github.io/#p2p=${pinText}`;
    navigator.clipboard.writeText(link).then(() => {
      const toast = document.getElementById('p2pStatus');
      if (toast) toast.innerText = `🔗 Direct Share Link copied! Send to receiver.`;
    }).catch(() => {});
  }
}

function renderQRCode(pin) {
  const qrBox = document.getElementById('p2pQrContainer');
  if (!qrBox) return;
  qrBox.innerHTML = '';
  const shareUrl = `https://m4mental.github.io/#p2p=${pin}`;
  
  if (typeof QRCode !== 'undefined') {
    try {
      new QRCode(qrBox, {
        text: shareUrl,
        width: 120,
        height: 120,
        colorDark: "#06b6d4",
        colorLight: "#0f172a",
        correctLevel: QRCode.CorrectLevel.M
      });
      return;
    } catch(e) {}
  }
  
  // Fallback SVG QR Code API if local lib hasn't loaded yet
  const img = document.createElement('img');
  img.src = `https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=${encodeURIComponent(shareUrl)}&bgcolor=0f172a&color=06b6d4&margin=4`;
  img.alt = 'P2P QR Code';
  img.style.borderRadius = '8px';
  img.style.maxWidth = '120px';
  qrBox.appendChild(img);
}

function startCameraScanner() {
  const scannerBox = document.getElementById('p2pScannerBox');
  const startBtn = document.getElementById('startScannerBtn');
  if (!scannerBox) return;
  
  scannerBox.style.display = 'block';
  if (startBtn) startBtn.style.display = 'none';

  const st = document.getElementById('p2pStatus');
  if (st) st.innerHTML = '<span style="color:#06b6d4;">📷 Starting Camera Scanner... Point at the other device\'s QR code.</span>';

  if (typeof Html5Qrcode === 'undefined') {
    if (st) st.innerHTML = '<span style="color:#ef4444;">⚠️ QR Scanner library loading... please retry in 2 seconds.</span>';
    return;
  }

  if (html5QrScanner) {
    try { html5QrScanner.stop().catch(() => {}); } catch(e) {}
  }

  html5QrScanner = new Html5Qrcode("p2pQrReader");
  const config = { fps: 10, qrbox: { width: 200, height: 200 } };

  html5QrScanner.start(
    { facingMode: "environment" },
    config,
    (decodedText) => {
      // Success callback
      let detectedPin = '';
      if (decodedText.includes('p2p=')) {
        detectedPin = decodedText.split('p2p=')[1].split('&')[0];
      } else if (/^\d{4}$/.test(decodedText.trim())) {
        detectedPin = decodedText.trim();
      }

      if (detectedPin && detectedPin.length === 4) {
        if (navigator.vibrate) navigator.vibrate(100);
        stopCameraScanner();
        
        const pinInput = document.getElementById('connectPinInput');
        if (pinInput) pinInput.value = detectedPin;
        
        if (st) st.innerHTML = `<span style="color:#22c55e; font-weight:700;">✅ QR Scanned! Connecting to PIN ${detectedPin}...</span>`;
        connectToSender(detectedPin);
      }
    },
    (errorMessage) => {
      // Scanning frame error (ignore)
    }
  ).catch((err) => {
    if (st) st.innerHTML = `<span style="color:#ef4444;">⚠️ Camera Error: ${err || 'Camera permission denied.'}</span>`;
    stopCameraScanner();
  });
}

function stopCameraScanner() {
  const scannerBox = document.getElementById('p2pScannerBox');
  const startBtn = document.getElementById('startScannerBtn');
  if (scannerBox) scannerBox.style.display = 'none';
  if (startBtn) startBtn.style.display = 'inline-flex';

  if (html5QrScanner) {
    try {
      html5QrScanner.stop().then(() => {
        html5QrScanner.clear();
        html5QrScanner = null;
      }).catch(() => {
        html5QrScanner = null;
      });
    } catch(e) {
      html5QrScanner = null;
    }
  }
}

function checkHashForP2P() {
  const hash = window.location.hash;
  if (hash && hash.includes('p2p=')) {
    const pin = hash.split('p2p=')[1].split('&')[0];
    if (pin && pin.length === 4) {
      setTimeout(() => {
        openP2PModal();
        const pinInput = document.getElementById('connectPinInput');
        if (pinInput) {
          pinInput.value = pin;
          connectToSender(pin);
        }
      }, 800);
    }
  }
}

function initP2PPeer() {
  if (typeof Peer === 'undefined') {
    const st = document.getElementById('p2pStatus');
    if (st) st.innerHTML = '<span style="color:#38bdf8;">⏳ Loading WebRTC engine...</span>';
    setTimeout(initP2PPeer, 400);
    return;
  }
  if (peer && !peer.destroyed && peer.open) return;

  const rawPin = generatePin();
  myPinCode = 'm4m-' + rawPin;
  const st = document.getElementById('p2pStatus');
  if (st) st.innerHTML = '<span style="color:#38bdf8;">⏳ Connecting to P2P Signal Network...</span>';

  // High-Availability STUN & OpenRelay TURN servers for 5G (Jio/Airtel/Vi) CGNAT Traversal
  peer = new Peer(myPinCode, {
    debug: 1,
    config: {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },
        { urls: 'stun:global.stun.twilio.com:3478' },
        { urls: 'turn:openrelay.metered.ca:80', username: 'openrelay', credential: 'openrelay' },
        { urls: 'turn:openrelay.metered.ca:443', username: 'openrelay', credential: 'openrelay' },
        { urls: 'turn:openrelay.metered.ca:443?transport=tcp', username: 'openrelay', credential: 'openrelay' }
      ]
    }
  });

  peer.on('open', (id) => {
    const el = document.getElementById('myPinDisplay');
    const pin = myPinCode.replace('m4m-', '');
    if (el) el.innerText = pin;
    renderQRCode(pin);
    const st = document.getElementById('p2pStatus');
    if (st) st.innerHTML = '<span style="color:#22c55e;">✅ Device Ready! Scan QR or share PIN to connect.</span>';
  });

  peer.on('connection', (conn) => {
    peerConn = conn;
    setupConnListeners();
  });

  peer.on('error', (err) => {
    const st = document.getElementById('p2pStatus');
    if (err.type === 'unavailable-id') {
      if (st) st.innerText = '🔄 Generating fresh PIN...';
      peer.destroy();
      peer = null;
      setTimeout(initP2PPeer, 300);
    } else {
      if (st) st.innerHTML = `<span style="color:#ef4444;">⚠️ P2P Notice: ${err.type || 'Retrying signal connection...'}</span>`;
    }
  });
}

function setupConnListeners() {
  const el = document.getElementById('p2pStatus');
  if (el) el.innerHTML = '<span style="color:#22c55e; font-weight:700;">⚡ Connected to Peer Device! You can now send files.</span>';
  const dcBtn = document.getElementById('disconnectBtn');
  if (dcBtn) dcBtn.style.display = 'inline-block';
  stopCameraScanner();

  incomingChunks = [];
  incomingFileMeta = null;

  peerConn.on('data', (data) => {
    if (typeof data === 'string') {
      try {
        const parsed = JSON.parse(data);
        if (parsed.type === 'file-start') {
          incomingFileMeta = parsed;
          incomingChunks = [];
          const st = document.getElementById('p2pStatus');
          if (st) st.innerHTML = `<span style="color:#06b6d4;">📥 Receiving <b>${parsed.name}</b> (0%)...</span>`;
        } else if (parsed.type === 'file-end') {
          const blob = new Blob(incomingChunks, { type: incomingFileMeta.fileType || 'application/octet-stream' });
          const url = URL.createObjectURL(blob);
          const st = document.getElementById('p2pStatus');

          let fileBox = document.getElementById('receivedFilesList');
          if (!fileBox) {
            if (st) st.innerHTML = `<b>🎉 Received Files:</b><div id="receivedFilesList" style="margin-top:12px; display:flex; flex-direction:column; gap:8px; align-items:center;"></div>`;
            fileBox = document.getElementById('receivedFilesList');
          }

          if (fileBox) {
            const link = document.createElement('a');
            link.href = url;
            link.download = incomingFileMeta.name;
            link.style = "background:linear-gradient(135deg, #10b981, #059669); color:#fff; padding:10px 20px; border-radius:10px; text-decoration:none; display:inline-flex; align-items:center; gap:8px; font-weight:bold; margin-top:6px; box-shadow:0 4px 14px rgba(16,185,129,0.3);";
            link.innerHTML = `💾 Download <b>${incomingFileMeta.name}</b> (${(incomingFileMeta.size / (1024*1024)).toFixed(2)} MB)`;
            fileBox.appendChild(link);
          }

          if (st) st.innerHTML = `<span style="color:#10b981; font-weight:700;">🎉 File "${incomingFileMeta.name}" received successfully!</span>`;
          incomingChunks = [];
        }
      } catch(e) {}
    } else {
      incomingChunks.push(data);
      if (incomingFileMeta) {
        const receivedBytes = incomingChunks.length * 16384;
        const pct = Math.min(100, Math.round((receivedBytes / incomingFileMeta.size) * 100));
        const st = document.getElementById('p2pStatus');
        if (st) st.innerHTML = `<span style="color:#06b6d4;">📥 Receiving <b>${incomingFileMeta.name}</b>: <b>${pct}%</b> [${(receivedBytes/(1024*1024)).toFixed(1)} / ${(incomingFileMeta.size/(1024*1024)).toFixed(1)} MB]</span>`;
      }
    }
  });

  peerConn.on('close', () => {
    const el = document.getElementById('p2pStatus');
    if (el) el.innerHTML = '<span style="color:#94a3b8;">🔌 Peer Device Disconnected.</span>';
    const dcBtn = document.getElementById('disconnectBtn');
    if (dcBtn) dcBtn.style.display = 'none';
    peerConn = null;
  });
}

function connectToSender(providedPin) {
  let pin = providedPin;
  if (!pin) {
    const pinInput = document.getElementById('connectPinInput');
    if (pinInput) pin = pinInput.value.trim();
  }
  if (!pin || pin.length !== 4) {
    alert('Please enter or scan a valid 4-digit PIN.');
    return;
  }
  const el = document.getElementById('p2pStatus');
  if (el) el.innerHTML = `<span style="color:#38bdf8;">🔄 Connecting to Device PIN: <b>${pin}</b>...</span>`;
  if (!peer || peer.destroyed) initP2PPeer();
  peerConn = peer.connect('m4m-' + pin, { reliable: true });
  peerConn.on('open', setupConnListeners);
  peerConn.on('error', () => {
    if (el) el.innerHTML = `<span style="color:#ef4444;">❌ Failed to connect to PIN ${pin}. Please check PIN & retry.</span>`;
  });
}

function disconnectDevice() {
  if (peerConn) {
    peerConn.close();
    peerConn = null;
  }
  stopCameraScanner();
  const el = document.getElementById('p2pStatus');
  if (el) el.innerHTML = '<span style="color:#94a3b8;">🔌 Disconnected cleanly. Generating new PIN...</span>';
  const dcBtn = document.getElementById('disconnectBtn');
  if (dcBtn) dcBtn.style.display = 'none';

  if (peer) {
    peer.destroy();
    peer = null;
  }
  setTimeout(initP2PPeer, 400);
}

async function sendP2PFiles() {
  const fileInput = document.getElementById('p2pFileInput');
  if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
    alert('Please select at least one file.');
    return;
  }
  if (!peerConn || !peerConn.open) {
    alert('⚠️ Please connect to a device PIN or scan QR first!');
    return;
  }

  const files = Array.from(fileInput.files);
  const el = document.getElementById('p2pStatus');
  const CHUNK_SIZE = 16384; // 16 KB Binary Chunks for zero-crash WebRTC data streaming

  for (let fIdx = 0; fIdx < files.length; fIdx++) {
    const file = files[fIdx];

    peerConn.send(JSON.stringify({
      type: 'file-start',
      name: file.name,
      fileType: file.type,
      size: file.size
    }));

    const buffer = await file.arrayBuffer();
    let offset = 0;

    while (offset < buffer.byteLength) {
      const chunk = buffer.slice(offset, offset + CHUNK_SIZE);
      peerConn.send(chunk);
      offset += CHUNK_SIZE;

      const pct = Math.min(100, Math.round((offset / buffer.byteLength) * 100));
      if (el) {
        el.innerHTML = `<span style="color:#06b6d4;">📤 Sending (<b>${fIdx + 1}/${files.length}</b>): <b>${file.name}</b> (${pct}%) [${(offset/(1024*1024)).toFixed(1)} / ${(buffer.byteLength/(1024*1024)).toFixed(1)} MB]</span>`;
      }

      // Backpressure pacing to avoid buffer overflow
      if (offset % (CHUNK_SIZE * 15) === 0) {
        await new Promise(r => setTimeout(r, 20));
      }
    }

    peerConn.send(JSON.stringify({ type: 'file-end' }));
    await new Promise(r => setTimeout(r, 300));
  }

  if (el) el.innerHTML = `<span style="color:#10b981; font-weight:700;">🎉 All ${files.length} file(s) sent successfully!</span>`;
  fileInput.value = '';
}

function injectP2PModalDOM() {
  if (document.getElementById('m4mP2PModal')) return;
  const modalDiv = document.createElement('div');
  modalDiv.id = 'm4mP2PModal';
  modalDiv.style.cssText = 'display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(5,9,18,0.85); backdrop-filter:blur(8px); -webkit-backdrop-filter:blur(8px); z-index:99999; align-items:center; justify-content:center; padding:15px; box-sizing:border-box;';
  modalDiv.innerHTML = `
    <div style="background:#0f172a; border:1px solid #1e293b; border-radius:20px; max-width:720px; width:100%; max-height:92vh; overflow-y:auto; padding:26px; text-align:center; position:relative; box-shadow:0 25px 50px -12px rgba(0,0,0,0.9), 0 0 30px rgba(6,182,212,0.15); font-family:inherit;">
      <button onclick="closeP2PModal()" style="position:absolute; top:16px; right:16px; background:#1e293b; border:1px solid #334155; color:#94a3b8; width:34px; height:34px; border-radius:10px; font-size:1.1rem; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all 0.2s;">✕</button>
      
      <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(6,182,212,0.1); border:1px solid rgba(6,182,212,0.3); padding:4px 12px; border-radius:20px; font-size:0.8rem; font-weight:700; color:#06b6d4; margin-bottom:10px;">
        ⚡ M4Mental High-Speed Warp Drop
      </div>
      
      <div style="font-size:1.6rem; font-weight:800; color:#f8fafc; margin-bottom:6px;">🚀 P2P Direct File Transfer</div>
      <div style="font-size:0.88rem; color:#94a3b8; margin-bottom:20px; line-height:1.4;">
        Direct encrypted transfer between Android, Windows, iOS & Mac.<br>
        <b style="color:#38bdf8;">Scan QR Code • Zero Cloud Uploads • No Size Limits</b>
      </div>

      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:16px; margin-bottom:16px;">
        <!-- Step 1: Device PIN & QR Code -->
        <div style="background:#090d16; border:1px solid #1e293b; border-radius:16px; padding:18px; text-align:center; display:flex; flex-direction:column; align-items:center;">
          <div style="font-weight:700; color:#e2e8f0; font-size:0.92rem; margin-bottom:2px;">1. Your Device PIN & QR</div>
          <div style="font-size:0.75rem; color:#64748b; margin-bottom:8px;">(Scan with other phone or enter PIN)</div>
          
          <div id="myPinDisplay" style="font-size:2rem; font-weight:900; color:#06b6d4; letter-spacing:6px; background:#0f172a; padding:6px 14px; border-radius:10px; border:1px dashed #334155; margin-bottom:10px; user-select:all;">----</div>
          
          <div id="p2pQrContainer" style="background:#0f172a; padding:8px; border-radius:12px; border:1px solid #1e293b; margin-bottom:12px; min-height:120px; display:flex; align-items:center; justify-content:center;">
            <span style="font-size:0.75rem; color:#64748b;">Generating QR...</span>
          </div>

          <div style="display:flex; gap:6px; justify-content:center; flex-wrap:wrap;">
            <button onclick="copyMyPin()" style="background:#1e293b; color:#cbd5e1; border:1px solid #334155; padding:6px 12px; border-radius:8px; font-size:0.8rem; font-weight:600; cursor:pointer;">📋 Copy PIN</button>
            <button onclick="copyShareLink()" style="background:#0284c7; color:#fff; border:none; padding:6px 12px; border-radius:8px; font-size:0.8rem; font-weight:600; cursor:pointer;">🔗 Share Link</button>
          </div>
        </div>

        <!-- Step 2: Connect via Camera QR Scanner or PIN -->
        <div style="background:#090d16; border:1px solid #1e293b; border-radius:16px; padding:18px; text-align:center; display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div style="font-weight:700; color:#e2e8f0; font-size:0.92rem; margin-bottom:2px;">2. Connect & Pair</div>
            <div style="font-size:0.75rem; color:#64748b; margin-bottom:10px;">(Scan QR with Camera or type PIN)</div>

            <!-- Live Camera Scanner Box -->
            <div id="p2pScannerBox" style="display:none; margin-bottom:12px; background:#0f172a; border:1px solid #06b6d4; border-radius:12px; padding:8px; overflow:hidden;">
              <div id="p2pQrReader" style="width:100%; max-height:220px;"></div>
              <button onclick="stopCameraScanner()" style="margin-top:8px; background:#dc2626; color:#fff; border:none; padding:6px 12px; border-radius:8px; font-size:0.75rem; font-weight:700; cursor:pointer;">✕ Stop Camera</button>
            </div>

            <!-- Scan QR Button -->
            <button id="startScannerBtn" onclick="startCameraScanner()" style="background:linear-gradient(135deg, rgba(6,182,212,0.15), rgba(56,189,248,0.15)); border:1px solid #06b6d4; color:#38bdf8; padding:10px; border-radius:10px; font-weight:700; font-size:0.9rem; cursor:pointer; width:100%; margin-bottom:10px; display:inline-flex; align-items:center; justify-content:center; gap:8px;">
              📷 Scan QR with Camera
            </button>

            <div style="font-size:0.75rem; color:#64748b; margin:4px 0;">— OR ENTER PIN MANUALLY —</div>

            <input type="number" id="connectPinInput" style="width:100%; background:#0f172a; border:1px solid #334155; color:#fff; font-size:1.15rem; font-weight:700; text-align:center; padding:9px; border-radius:10px; margin:8px 0; outline:none; box-sizing:border-box;" placeholder="e.g. 5678">
          </div>

          <button onclick="connectToSender()" style="background:linear-gradient(135deg, #0284c7, #0369a1); color:#fff; border:none; padding:10px; border-radius:10px; font-weight:700; font-size:0.9rem; cursor:pointer; width:100%; box-shadow:0 4px 12px rgba(2,132,199,0.3);">⚡ Connect Device</button>
        </div>
      </div>

      <!-- Step 3: Drag & Select Files -->
      <div style="border:2px dashed #334155; border-radius:16px; padding:20px; cursor:pointer; background:#090d16; transition:all 0.2s;" onclick="document.getElementById('p2pFileInput').click()">
        <div style="font-size:2rem; margin-bottom:4px;">📦</div>
        <div style="font-weight:700; color:#f1f5f9; font-size:0.95rem;">Click or Drop files to Send</div>
        <div style="font-size:0.78rem; color:#64748b; margin-top:2px;">Send APKs, ZIPs, Videos, Photos, or Documents</div>
        <input type="file" id="p2pFileInput" multiple style="display:none;" onchange="sendP2PFiles()">
      </div>

      <!-- Live Status Box -->
      <div id="p2pStatus" style="margin-top:14px; font-size:0.9rem; font-weight:600; min-height:22px; color:#38bdf8;">
        Status: Ready to connect.
      </div>

      <div style="margin-top:16px; display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">
        <button id="disconnectBtn" onclick="disconnectDevice()" style="display:none; background:#dc2626; color:#fff; border:none; padding:9px 18px; border-radius:10px; cursor:pointer; font-weight:bold; font-size:0.85rem;">🔌 Disconnect</button>
        <button onclick="closeP2PModal()" style="background:#1e293b; border:1px solid #334155; color:#94a3b8; padding:9px 20px; border-radius:10px; cursor:pointer; font-weight:bold; font-size:0.85rem;">Close Window</button>
      </div>
    </div>
  `;
  document.body.appendChild(modalDiv);
}

document.addEventListener('DOMContentLoaded', () => {
  injectP2PModalDOM();
  checkHashForP2P();
});
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  injectP2PModalDOM();
  checkHashForP2P();
}
