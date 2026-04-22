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
    scene.userData.camera = camera;
    scene.userData.controls = controls;

    addLights(scene, accent);

    const modelPath = container.dataset.modelPath || window.SNEAKER_MODEL;
    if (modelPath) {
        loadModel(modelPath, scene, status, accent);
    } else {
        const fallback = buildFallbackSneaker(scene, accent);
        fitCameraToObject(fallback, camera, controls);
        addAdaptiveStage(scene, fallback, accent);
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

function loadModel(modelPath, scene, status, accent) {
    const loader = new GLTFLoader();
    loader.load(
        modelPath,
        (gltf) => {
            const model = gltf.scene;
            normalizeModel(model);
            scene.add(model);
            addAdaptiveStage(scene, model, accent);
            fitCameraToObject(model, scene.userData.camera, scene.userData.controls);
            hideStatus(status);
        },
        (event) => {
            if (status && event.total) {
                const percent = Math.round((event.loaded / event.total) * 100);
                status.textContent = `Загрузка 3D модели... ${percent}%`;
            }
        },
        () => {
            const fallback = buildFallbackSneaker(scene, accent);
            addAdaptiveStage(scene, fallback, accent);
            fitCameraToObject(fallback, scene.userData.camera, scene.userData.controls);
            if (status) {
                status.textContent = "Показана резервная 3D модель";
                window.setTimeout(() => hideStatus(status), 1200);
            }
        }
    );
}

function normalizeModel(model) {
    const floorY = -0.42;
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const targetWidth = 2.35;
    const targetHeight = 1.05;
    const targetDepth = 1.25;
    const scale = Math.min(
        targetWidth / Math.max(size.x, 0.001),
        targetHeight / Math.max(size.y, 0.001),
        targetDepth / Math.max(size.z, 0.001)
    );

    model.rotation.y = Math.PI * 0.82;
    model.scale.setScalar(scale);
    model.position.set(
        -center.x * scale,
        0,
        -center.z * scale
    );

    model.updateMatrixWorld(true);
    const metrics = getVisualMetrics(model);
    model.position.x -= metrics.center.x;
    model.position.z -= metrics.center.z;
    model.position.y += floorY - metrics.contactY;

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

function addAdaptiveStage(scene, object, accent) {
    const metrics = getVisualMetrics(object);
    const size = metrics.size;
    const center = metrics.center;
    const floorY = metrics.contactY - 0.012;
    const radius = Math.max(size.x, size.z) * 0.68;

    const floorMaterial = new THREE.MeshStandardMaterial({
        color: "#f8fafc",
        roughness: 0.72,
        metalness: 0.04,
    });
    const floor = new THREE.Mesh(new THREE.CircleGeometry(radius, 96), floorMaterial);
    floor.rotation.x = -Math.PI / 2;
    floor.position.set(center.x, floorY, center.z);
    floor.receiveShadow = true;
    scene.add(floor);

    const ring = new THREE.Mesh(
        new THREE.TorusGeometry(radius * 0.86, 0.01, 10, 160),
        new THREE.MeshBasicMaterial({ color: accent })
    );
    ring.rotation.x = Math.PI / 2;
    ring.position.set(center.x, floorY + 0.012, center.z);
    scene.add(ring);
}

function fitCameraToObject(object, camera, controls) {
    if (!camera || !controls) {
        return;
    }

    const metrics = getVisualMetrics(object);
    const center = metrics.center;
    const size = metrics.size;
    const maxSize = Math.max(size.x, size.y, size.z);
    const distance = Math.max(maxSize * 1.65, 2.2);

    controls.target.copy(center);
    controls.target.y += size.y * 0.08;
    camera.position.set(center.x + distance * 0.82, center.y + distance * 0.38, center.z + distance);
    camera.near = Math.max(distance / 100, 0.01);
    camera.far = distance * 100;
    camera.updateProjectionMatrix();
    controls.update();
}

function getVisualMetrics(object) {
    object.updateMatrixWorld(true);

    const points = collectVisibleMeshPoints(object);
    if (!points.length) {
        const box = new THREE.Box3().setFromObject(object);
        return {
            box,
            center: box.getCenter(new THREE.Vector3()),
            size: box.getSize(new THREE.Vector3()),
            contactY: box.min.y,
        };
    }

    const box = new THREE.Box3();
    const yValues = [];
    points.forEach((point) => {
        box.expandByPoint(point);
        yValues.push(point.y);
    });
    yValues.sort((a, b) => a - b);

    return {
        box,
        center: box.getCenter(new THREE.Vector3()),
        size: box.getSize(new THREE.Vector3()),
        contactY: percentile(yValues, 0.018),
    };
}

function collectVisibleMeshPoints(object) {
    const points = [];
    const point = new THREE.Vector3();
    const maxPointsPerMesh = 9000;

    object.traverse((node) => {
        if (!node.isMesh || !node.visible || !node.geometry?.attributes?.position) {
            return;
        }

        const positions = node.geometry.attributes.position;
        const step = Math.max(1, Math.floor(positions.count / maxPointsPerMesh));
        node.updateWorldMatrix(true, false);

        for (let index = 0; index < positions.count; index += step) {
            point.fromBufferAttribute(positions, index).applyMatrix4(node.matrixWorld);
            points.push(point.clone());
        }
    });

    return points;
}

function percentile(sortedValues, ratio) {
    if (!sortedValues.length) {
        return 0;
    }

    const index = Math.min(
        sortedValues.length - 1,
        Math.max(0, Math.floor(sortedValues.length * ratio))
    );
    return sortedValues[index];
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
    return group;
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
