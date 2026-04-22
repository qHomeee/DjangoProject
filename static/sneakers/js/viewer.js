import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const viewers = document.querySelectorAll(".sneaker-viewer");

viewers.forEach((container) => {
    createViewer(container);
});

function createViewer(container) {
    const accent = new THREE.Color(container.dataset.accent || "#1495ff");
    const status = container.querySelector(".viewer-status");
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#e8eef3");

    const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
    camera.position.set(2.35, 1.05, 2.85);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.08;
    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.06;
    controls.autoRotate = false;
    controls.enablePan = false;
    controls.minDistance = 1.1;
    controls.maxDistance = 4.8;
    controls.maxPolarAngle = Math.PI / 2;
    controls.target.set(0, 0.08, 0);

    addLights(scene, accent);
    addStage(scene, accent);

    const modelPath = container.dataset.modelPath || window.SNEAKER_MODEL;
    if (modelPath) {
        loadModel(modelPath, scene, status, accent);
    } else {
        buildFallbackSneaker(scene, accent);
        hideStatus(status);
    }

    const resize = () => {
        const width = container.clientWidth;
        const height = container.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height, false);
    };

    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(container);
    resize();

    function animate() {
        controls.update();
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
    }

    animate();
}

function addLights(scene, accent) {
    scene.add(new THREE.HemisphereLight("#ffffff", "#c7d2e1", 3.2));

    const keyLight = new THREE.DirectionalLight("#ffffff", 4.8);
    keyLight.position.set(3.5, 4.5, 3.2);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.set(1024, 1024);
    scene.add(keyLight);

    const frontLight = new THREE.DirectionalLight("#ffffff", 2.4);
    frontLight.position.set(0, 1.7, 4);
    scene.add(frontLight);

    const rimLight = new THREE.PointLight(accent, 2.2, 12);
    rimLight.position.set(-3, 2.5, -2.5);
    scene.add(rimLight);
}

function addStage(scene, accent) {
    const floorMaterial = new THREE.MeshStandardMaterial({
        color: "#f8fafc",
        roughness: 0.7,
        metalness: 0.05,
    });
    const floor = new THREE.Mesh(new THREE.CircleGeometry(1.65, 96), floorMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.5;
    floor.receiveShadow = true;
    scene.add(floor);

    const ring = new THREE.Mesh(
        new THREE.TorusGeometry(1.35, 0.012, 10, 160),
        new THREE.MeshBasicMaterial({ color: accent })
    );
    ring.rotation.x = Math.PI / 2;
    ring.position.y = -0.47;
    scene.add(ring);
}

function loadModel(modelPath, scene, status, accent) {
    const loader = new GLTFLoader();
    loader.load(
        modelPath,
        (gltf) => {
            const model = gltf.scene;
            normalizeModel(model);
            scene.add(model);
            hideStatus(status);
        },
        (event) => {
            if (status && event.total) {
                const percent = Math.round((event.loaded / event.total) * 100);
                status.textContent = `Загрузка 3D модели... ${percent}%`;
            }
        },
        () => {
            buildFallbackSneaker(scene, accent);
            if (status) {
                status.textContent = "Показана резервная 3D модель";
                window.setTimeout(() => hideStatus(status), 1200);
            }
        }
    );
}

function normalizeModel(model) {
    const stageY = -0.46;
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const scale = 2.25 / Math.max(size.x, size.y, size.z);

    model.rotation.y = Math.PI * 0.82;
    model.scale.setScalar(scale);
    model.position.set(
        -center.x * scale,
        stageY - box.min.y * scale,
        -center.z * scale
    );

    model.updateMatrixWorld(true);
    const fittedBox = new THREE.Box3().setFromObject(model);
    const fittedCenter = fittedBox.getCenter(new THREE.Vector3());
    model.position.x -= fittedCenter.x;
    model.position.z -= fittedCenter.z;
    model.position.y += stageY - fittedBox.min.y - 0.55;

    model.traverse((node) => {
        if (!node.isMesh) {
            return;
        }
        node.castShadow = true;
        node.receiveShadow = true;
        const materials = Array.isArray(node.material) ? node.material : [node.material];
        materials.filter(Boolean).forEach((material) => {
            material.roughness = Math.min(material.roughness ?? 0.5, 0.4);
            material.metalness = material.metalness ?? 0.08;
            material.needsUpdate = true;
        });
    });
}

function buildFallbackSneaker(scene, accent) {
    const group = new THREE.Group();
    const dark = new THREE.MeshStandardMaterial({ color: "#0f172a", roughness: 0.36 });
    const midsole = new THREE.MeshStandardMaterial({ color: "#f8fafc", roughness: 0.52 });
    const upper = new THREE.MeshStandardMaterial({ color: accent, roughness: 0.42, metalness: 0.05 });
    const textile = new THREE.MeshStandardMaterial({ color: "#dbe4ea", roughness: 0.7 });

    const sole = new THREE.Mesh(new THREE.BoxGeometry(2.7, 0.28, 0.9), dark);
    sole.position.set(0, -0.18, 0);
    sole.scale.set(1, 1, 0.78);
    sole.castShadow = true;
    group.add(sole);

    const foam = new THREE.Mesh(new THREE.BoxGeometry(2.42, 0.22, 0.78), midsole);
    foam.position.set(0.05, 0.05, 0);
    foam.castShadow = true;
    group.add(foam);

    const body = new THREE.Mesh(new THREE.SphereGeometry(0.78, 48, 24), upper);
    body.scale.set(1.42, 0.42, 0.46);
    body.position.set(-0.18, 0.43, 0);
    body.castShadow = true;
    group.add(body);

    const toe = new THREE.Mesh(new THREE.SphereGeometry(0.46, 48, 20), upper);
    toe.scale.set(1.15, 0.5, 0.72);
    toe.position.set(1.0, 0.3, 0);
    toe.castShadow = true;
    group.add(toe);

    const collar = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.55, 0.66), textile);
    collar.position.set(-0.74, 0.72, 0);
    collar.rotation.z = -0.22;
    collar.castShadow = true;
    group.add(collar);

    for (let i = 0; i < 5; i += 1) {
        const lace = new THREE.Mesh(new THREE.BoxGeometry(0.58, 0.025, 0.035), dark);
        lace.position.set(-0.18 + i * 0.18, 0.76 - i * 0.035, 0.34);
        lace.rotation.z = 0.25;
        group.add(lace);
    }

    group.rotation.y = -0.35;
    group.position.y = -0.1;
    scene.add(group);
}

function hideStatus(status) {
    if (!status) {
        return;
    }
    status.style.opacity = "0";
    window.setTimeout(() => {
        status.style.display = "none";
    }, 260);
}
