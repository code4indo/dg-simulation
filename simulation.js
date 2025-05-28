// --- DOM Elements ---
const sceneContainer = document.getElementById('scene-container');
const currentStageEl = document.getElementById('current-stage');
const arsipProcessedEl = document.getElementById('arsip-processed-count');
const arsipTotalEl = document.getElementById('arsip-total-count');
const arsipAvailableEl = document.getElementById('arsip-available-count');
const ikuResultEl = document.getElementById('iku-result');
const startButton = document.getElementById('start-simulation');
const logListEl = document.getElementById('log-list');

// --- Three.js Setup ---
let scene, camera, renderer, controls;
let arsipObjects = []; // Array untuk menyimpan objek 3D arsip
let agentObjects = {}; // Objek untuk menyimpan agen AI
const TOTAL_ARSIP = 5; // Jumlah arsip untuk disimulasikan

function init3D() {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xeeeeff);

    camera = new THREE.PerspectiveCamera(75, sceneContainer.clientWidth / sceneContainer.clientHeight, 0.1, 1000);
    camera.position.set(0, 15, 25); // Posisi kamera

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(sceneContainer.clientWidth, sceneContainer.clientHeight);
    sceneContainer.appendChild(renderer.domElement);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 7);
    scene.add(directionalLight);

    // Controls (opsional)
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;

    // Ground plane
    const planeGeometry = new THREE.PlaneGeometry(50, 50);
    const planeMaterial = new THREE.MeshStandardMaterial({ color: 0xcccccc, side: THREE.DoubleSide });
    const plane = new THREE.Mesh(planeGeometry, planeMaterial);
    plane.rotation.x = -Math.PI / 2; // Putar agar horizontal
    plane.position.y = -1;
    scene.add(plane);

    // Create "Agent" visual placeholders
    createAgentVisuals();

    animate();
}

function createAgentVisuals() {
    const agentColors = {
        lifecycle: 0xff0000, // Merah
        metadata: 0x00ff00, // Hijau
        quality: 0x0000ff, // Biru
        policy: 0xffff00, // Kuning
        coordinator: 0xff00ff // Magenta
    };
    const agentPositions = {
        lifecycle: { x: -15, y: 0, z: 0 },
        metadata: { x: -5, y: 0, z: 0 },
        quality: { x: 5, y: 0, z: 0 },
        policy: { x: 15, y: 0, z: 0 },
        coordinator: { x: 0, y: 0, z: -10 } // Koordinator di tengah belakang
    };

    for (const agentName in agentColors) {
        const geometry = new THREE.SphereGeometry(1.5, 16, 16);
        const material = new THREE.MeshStandardMaterial({ color: agentColors[agentName] });
        const agentMesh = new THREE.Mesh(geometry, material);
        agentMesh.position.set(agentPositions[agentName].x, agentPositions[agentName].y, agentPositions[agentName].z);
        scene.add(agentMesh);
        agentObjects[agentName] = agentMesh;

        // Tambah label teks untuk Agen (sederhana)
        // Untuk label yang lebih baik, Anda perlu menggunakan teknik sprite atau HTML overlay
        const label = createTextLabel(agentName.toUpperCase(), agentPositions[agentName]);
        scene.add(label);
    }
}

function createTextLabel(text, position) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    context.font = 'Bold 20px Arial';
    context.fillStyle = 'rgba(0,0,0,0.95)';
    context.fillText(text, 0, 20); // Teks sedikit di atas posisi

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    texture.wrapS = THREE.ClampToEdgeWrapping;
    texture.wrapT = THREE.ClampToEdgeWrapping;

    const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.scale.set(5, 2.5, 1.0); // Sesuaikan skala label
    sprite.position.set(position.x, position.y + 3, position.z); // Posisikan label di atas agen
    return sprite;
}


function animate() {
    requestAnimationFrame(animate);
    if (controls) controls.update();
    renderer.render(scene, camera);
}

window.addEventListener('resize', () => {
    camera.aspect = sceneContainer.clientWidth / sceneContainer.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(sceneContainer.clientWidth, sceneContainer.clientHeight);
});

// --- Simulasi Logic ---
let currentArsipIndex = 0;
let arsipAvailable = 0;
let simulationRunning = false;

function addLog(message) {
    const li = document.createElement('li');
    li.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logListEl.insertBefore(li, logListEl.firstChild); // Tambah di awal
}

function updateUI() {
    arsipProcessedEl.textContent = currentArsipIndex;
    arsipTotalEl.textContent = TOTAL_ARSIP;
    arsipAvailableEl.textContent = arsipAvailable;
    if (currentArsipIndex === TOTAL_ARSIP && TOTAL_ARSIP > 0) {
        const iku = (arsipAvailable / TOTAL_ARSIP) * 100;
        ikuResultEl.textContent = iku.toFixed(2);
    } else if (TOTAL_ARSIP === 0) {
        ikuResultEl.textContent = '-';
    }
}

// Fungsi untuk memvisualisasikan perpindahan arsip (sangat disederhanakan)
async function moveArsipVisual(arsip3D, targetPosition, duration = 1000) {
    const startPosition = arsip3D.position.clone();
    const startTime = Date.now();

    return new Promise(resolve => {
        function step() {
            const t = Math.min(1, (Date.now() - startTime) / duration);
            arsip3D.position.lerpVectors(startPosition, targetPosition, t);
            if (t < 1) {
                requestAnimationFrame(step);
            } else {
                resolve();
            }
        }
        requestAnimationFrame(step);
    });
}

// Fungsi untuk memvisualisasikan "aktivitas" agen
function animateAgent(agentName, active = true) {
    if (agentObjects[agentName]) {
        const originalScale = agentObjects[agentName].scale.x;
        if (active) {
            agentObjects[agentName].material.emissive.setHex(0x555555); // Berkilau sedikit
            agentObjects[agentName].scale.set(1.2, 1.2, 1.2);
        } else {
            agentObjects[agentName].material.emissive.setHex(0x000000);
            agentObjects[agentName].scale.set(1,1,1);
        }
    }
}


async function simulateArsipProcessing(arsipData, arsip3D) {
    addLog(`[Arsip #${arsipData.id}] Masuk sistem.`);
    currentStageEl.textContent = `Memproses Arsip #${arsipData.id} - Akuisisi`;
    await moveArsipVisual(arsip3D, agentObjects.lifecycle.position); // Pindah ke Agen Siklus Hidup

    // 1. DG & Agent Siklus Hidup: Identifikasi & Registrasi
    animateAgent('lifecycle');
    addLog(`[Arsip #${arsipData.id}] Agen Siklus Hidup: Identifikasi, registrasi awal.`);
    arsipData.status = 'registered'; // DG: Data Lifecycle Mgt
    await new Promise(r => setTimeout(r, 1000)); // Delay simulasi
    animateAgent('lifecycle', false);
    currentStageEl.textContent = `Memproses Arsip #${arsipData.id} - Metadata`;
    await moveArsipVisual(arsip3D, agentObjects.metadata.position);

    // 2. DG & Agent Metadata: Ekstraksi & Validasi Standar
    animateAgent('metadata');
    addLog(`[Arsip #${arsipData.id}] Agen Metadata: Ekstraksi metadata otomatis.`);
    // Simulasi ekstraksi metadata (DG: Metadata Mgt)
    arsipData.metadata = Math.random() > 0.3 ? { title: `Dokumen ${arsipData.id}`, date: "2024-01-01" } : {};
    addLog(`[Arsip #${arsipData.id}] Agen Kebijakan/Standar: Validasi kelengkapan metadata.`);
    animateAgent('policy'); // Agen kebijakan juga aktif
    arsipData.metadataStandardCompliant = Object.keys(arsipData.metadata).length > 0; // DG: Policy & Standards Mgt
    if (!arsipData.metadataStandardCompliant) {
        addLog(`[Arsip #${arsipData.id}] GAGAL: Metadata tidak sesuai standar.`);
    } else {
         addLog(`[Arsip #${arsipData.id}] OK: Metadata sesuai standar.`);
    }
    await new Promise(r => setTimeout(r, 1500));
    animateAgent('metadata', false);
    animateAgent('policy', false);
    currentStageEl.textContent = `Memproses Arsip #${arsipData.id} - Kualitas Data`;
    await moveArsipVisual(arsip3D, agentObjects.quality.position);

    // 3. DG & Agent Kualitas Data: Pengecekan Kualitas
    animateAgent('quality');
    addLog(`[Arsip #${arsipData.id}] Agen Kualitas Data: Pengecekan kualitas isi & metadata.`);
    arsipData.dataQualityOk = Math.random() > 0.2; // DG: Data Quality Mgt
    if (!arsipData.dataQualityOk) {
        addLog(`[Arsip #${arsipData.id}] GAGAL: Kualitas data/metadata rendah.`);
    } else {
        addLog(`[Arsip #${arsipData.id}] OK: Kualitas data/metadata baik.`);
    }
    await new Promise(r => setTimeout(r, 1000));
    animateAgent('quality', false);

    // 4. (Opsional) Pengecekan Ketersediaan File Digital (jika relevan)
    arsipData.fileAccessible = Math.random() > 0.1; // Simulasi akses file
    if (!arsipData.fileAccessible) {
        addLog(`[Arsip #${arsipData.id}] GAGAL: File digital tidak dapat diakses/rusak.`);
    } else {
        addLog(`[Arsip #${arsipData.id}] OK: File digital dapat diakses.`);
    }


    // 5. Keputusan Ketersediaan & Penyimpanan
    const isAvailable = arsipData.metadataStandardCompliant && arsipData.dataQualityOk && arsipData.fileAccessible;
    if (isAvailable) {
        arsipAvailable++;
        addLog(`[Arsip #${arsipData.id}] Dinyatakan TERSEDIA. Disimpan ke repositori.`);
        arsip3D.material.color.set(0x00cc00); // Hijau jika tersedia
    } else {
        addLog(`[Arsip #${arsipData.id}] Dinyatakan TIDAK TERSEDIA (memerlukan perbaikan).`);
        arsip3D.material.color.set(0xcc0000); // Merah jika tidak
    }
    updateUI();
    await moveArsipVisual(arsip3D, new THREE.Vector3(0, 0, 10)); // "Repositori"
    currentStageEl.textContent = `Arsip #${arsipData.id} Selesai Diproses`;

    // Pindahkan arsip keluar dari scene setelah selesai
    await new Promise(r => setTimeout(r, 1000));
    scene.remove(arsip3D);
    arsip3D.geometry.dispose();
    arsip3D.material.dispose();

}

async function runSimulation() {
    if (simulationRunning) return;
    simulationRunning = true;
    startButton.disabled = true;
    addLog("Simulasi Dimulai...");

    currentArsipIndex = 0;
    arsipAvailable = 0;
    updateUI();
    logListEl.innerHTML = ''; // Bersihkan log lama

    for (let i = 0; i < TOTAL_ARSIP; i++) {
        currentArsipIndex = i + 1; // index UI mulai dari 1
        const arsipData = {
            id: currentArsipIndex,
            status: 'new',
            metadata: {},
            metadataStandardCompliant: false,
            dataQualityOk: false,
            fileAccessible: false
        };

        // Buat objek 3D untuk arsip
        const geometry = new THREE.BoxGeometry(2, 0.5, 3); // Bentuk seperti dokumen
        const material = new THREE.MeshStandardMaterial({ color: 0xaaaaaa });
        const arsip3D = new THREE.Mesh(geometry, material);
        arsip3D.position.set(-20, 0, Math.random() * 10 - 5); // Posisi masuk acak
        scene.add(arsip3D);
        arsipObjects.push(arsip3D);

        updateUI(); // Update hitungan arsip yang diproses
        await simulateArsipProcessing(arsipData, arsip3D);
    }

    addLog("Simulasi Selesai.");
    currentStageEl.textContent = "Simulasi Selesai";
    updateUI(); // Final IKU calculation
    simulationRunning = false;
    startButton.disabled = false;
}

// --- Inisialisasi ---
startButton.addEventListener('click', runSimulation);
init3D();
updateUI();