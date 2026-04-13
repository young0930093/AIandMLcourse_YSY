import os
from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from auth import decode_token
import aiosqlite
from database import DB_PATH

router = APIRouter(prefix="/api/courses", tags=["courses"])

COURSES = [
    {
        "id": 1,
        "title": "Regularization — L1/L2, Dropout, Batch Normalization",
        "description": "과적합을 막는 세 가지 핵심 기법을 이론과 코드로 배웁니다.",
        "is_free": True,
        "duration": "45분",
        "level": "중급",
        "content": {
            "sections": [
                {
                    "title": "왜 Regularization이 필요한가?",
                    "body": "모델이 훈련 데이터에 지나치게 맞춰지면 새로운 데이터에서 성능이 떨어집니다.\n이를 **과적합(Overfitting)** 이라 하며, Regularization은 모델의 복잡도를 제한해 일반화 성능을 높입니다."
                },
                {
                    "title": "L1 Regularization (Lasso)",
                    "body": "가중치의 절댓값 합을 손실에 더합니다: `Loss = Loss_original + λ Σ|w|`\n\n- 일부 가중치를 **정확히 0**으로 만들어 희소(Sparse) 모델을 생성\n- 불필요한 특성을 자동으로 제거하는 효과",
                    "code": "import tensorflow as tf\nfrom tensorflow.keras import regularizers\n\nmodel = tf.keras.Sequential([\n    tf.keras.layers.Dense(\n        128,\n        activation='relu',\n        kernel_regularizer=regularizers.l1(0.01)  # λ=0.01\n    ),\n    tf.keras.layers.Dense(10, activation='softmax')\n])"
                },
                {
                    "title": "L2 Regularization (Ridge / Weight Decay)",
                    "body": "가중치의 제곱합을 손실에 더합니다: `Loss = Loss_original + λ Σw²`\n\n- 가중치를 0에 가깝게 만들지만 **완전히 0으로 만들지는 않음**\n- 딥러닝에서 가장 널리 사용되는 정규화 방법",
                    "code": "model = tf.keras.Sequential([\n    tf.keras.layers.Dense(\n        128,\n        activation='relu',\n        kernel_regularizer=regularizers.l2(0.01)  # λ=0.01\n    ),\n    tf.keras.layers.Dense(10, activation='softmax')\n])\n\n# L1 + L2 동시 사용 (Elastic Net)\nregularizers.l1_l2(l1=0.01, l2=0.01)"
                },
                {
                    "title": "Dropout",
                    "body": "훈련 중 무작위로 뉴런을 **비활성화**합니다 (p 확률로 출력을 0으로).\n\n- 추론(Inference) 시에는 모든 뉴런 사용 (출력에 p 곱함)\n- 앙상블 효과: 매 배치마다 다른 서브네트워크를 학습\n- 일반적으로 p=0.2~0.5 사용",
                    "code": "model = tf.keras.Sequential([\n    tf.keras.layers.Dense(512, activation='relu'),\n    tf.keras.layers.Dropout(0.5),   # 50% 뉴런 비활성화\n    tf.keras.layers.Dense(256, activation='relu'),\n    tf.keras.layers.Dropout(0.3),   # 30% 뉴런 비활성화\n    tf.keras.layers.Dense(10, activation='softmax')\n])"
                },
                {
                    "title": "Batch Normalization",
                    "body": "각 배치의 활성화값을 **정규화**합니다: `x̂ = (x - μ_B) / √(σ²_B + ε)`\n\n- 학습 속도 향상: Learning Rate를 크게 설정 가능\n- 가중치 초기화에 덜 민감\n- 약한 Regularization 효과 (Dropout과 함께 사용 가능)\n- Conv Layer 뒤에 자주 배치: `Conv → BN → ReLU`",
                    "code": "model = tf.keras.Sequential([\n    tf.keras.layers.Conv2D(32, (3,3), use_bias=False),\n    tf.keras.layers.BatchNormalization(),   # BN은 bias 불필요\n    tf.keras.layers.Activation('relu'),\n\n    tf.keras.layers.Conv2D(64, (3,3), use_bias=False),\n    tf.keras.layers.BatchNormalization(),\n    tf.keras.layers.Activation('relu'),\n\n    tf.keras.layers.GlobalAveragePooling2D(),\n    tf.keras.layers.Dense(10, activation='softmax')\n])"
                },
                {
                    "title": "핵심 요약",
                    "body": "| 기법 | 동작 원리 | 주요 효과 |\n|------|-----------|----------|\n| L1 | |w| 패널티 | 희소 모델, 특성 선택 |\n| L2 | w² 패널티 | 작은 가중치 유지 |\n| Dropout | 랜덤 뉴런 비활성화 | 앙상블 효과 |\n| Batch Norm | 활성화값 정규화 | 학습 안정화, 빠른 수렴 |"
                }
            ]
        }
    },
    {
        "id": 2,
        "title": "Overfitting vs Underfitting — 모델 복잡도와 성능",
        "description": "편향-분산 트레이드오프를 이해하고 최적의 모델 복잡도를 찾는 방법을 배웁니다.",
        "is_free": False,
        "duration": "40분",
        "level": "중급",
        "content": {
            "sections": [
                {
                    "title": "편향-분산 트레이드오프 (Bias-Variance Tradeoff)",
                    "body": "모델 오차는 세 가지로 분해됩니다:\n`Total Error = Bias² + Variance + Irreducible Noise`\n\n- **High Bias (Underfitting)**: 모델이 너무 단순 → 훈련/테스트 모두 성능 낮음\n- **High Variance (Overfitting)**: 모델이 너무 복잡 → 훈련 성능 높지만 테스트 성능 낮음\n- **목표**: Bias와 Variance를 동시에 낮추는 균형점 찾기"
                },
                {
                    "title": "Overfitting 진단 — 학습 곡선",
                    "body": "훈련 손실(loss)과 검증 손실을 함께 플롯해 과적합을 진단합니다.",
                    "code": "import matplotlib.pyplot as plt\n\nhistory = model.fit(X_train, y_train,\n                    validation_split=0.2,\n                    epochs=100)\n\nplt.figure(figsize=(12, 4))\n\nplt.subplot(1, 2, 1)\nplt.plot(history.history['loss'], label='Train Loss')\nplt.plot(history.history['val_loss'], label='Val Loss')\nplt.title('Loss Curve')\nplt.legend()\n\nplt.subplot(1, 2, 2)\nplt.plot(history.history['accuracy'], label='Train Acc')\nplt.plot(history.history['val_accuracy'], label='Val Acc')\nplt.title('Accuracy Curve')\nplt.legend()\nplt.show()\n\n# Overfitting 신호:\n# val_loss 증가하는데 train_loss는 계속 감소"
                },
                {
                    "title": "Early Stopping으로 Overfitting 방지",
                    "body": "검증 손실이 개선되지 않으면 학습을 자동으로 중단합니다.",
                    "code": "early_stop = tf.keras.callbacks.EarlyStopping(\n    monitor='val_loss',\n    patience=10,          # 10 epoch 동안 개선 없으면 중단\n    restore_best_weights=True  # 최적 가중치 복원\n)\n\nmodel.fit(X_train, y_train,\n          validation_split=0.2,\n          epochs=200,\n          callbacks=[early_stop])\n\nprint(f\"실제 학습 epoch: {early_stop.stopped_epoch}\")"
                },
                {
                    "title": "Underfitting 해결 방법",
                    "body": "Underfitting은 모델 용량(capacity)이 부족할 때 발생합니다.",
                    "code": "# 1. 모델 복잡도 증가\nmodel_larger = tf.keras.Sequential([\n    tf.keras.layers.Dense(512, activation='relu'),  # 128 → 512\n    tf.keras.layers.Dense(256, activation='relu'),  # 레이어 추가\n    tf.keras.layers.Dense(128, activation='relu'),\n    tf.keras.layers.Dense(10, activation='softmax')\n])\n\n# 2. 더 많은 epoch 학습\nmodel.fit(X_train, y_train, epochs=200)  # epoch 늘리기\n\n# 3. Learning Rate 조정\noptimizer = tf.keras.optimizers.Adam(learning_rate=0.001)"
                },
                {
                    "title": "모델 복잡도 비교 실험",
                    "body": "동일 데이터에 복잡도가 다른 모델 세 개를 비교합니다.",
                    "code": "def build_model(units, layers):\n    model = tf.keras.Sequential()\n    for _ in range(layers):\n        model.add(tf.keras.layers.Dense(units, activation='relu'))\n    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))\n    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])\n    return model\n\n# 세 모델 비교\nunderfit = build_model(units=4, layers=1)    # 너무 단순\ngood_fit = build_model(units=64, layers=2)   # 적절\noverfit  = build_model(units=512, layers=5)  # 너무 복잡"
                },
                {
                    "title": "핵심 요약",
                    "body": "| 상태 | Train Loss | Val Loss | 해결책 |\n|------|-----------|---------|--------|\n| Underfitting | 높음 | 높음 | 모델 복잡도 ↑, epoch ↑ |\n| Good Fit | 낮음 | 낮음 | 유지 |\n| Overfitting | 낮음 | 높음 | Regularization, Dropout, Early Stopping |"
                }
            ]
        }
    },
    {
        "id": 3,
        "title": "Data Augmentation — 이미지 데이터 증강으로 모델 강화하기",
        "description": "적은 데이터로도 강력한 모델을 만드는 데이터 증강 기법을 실습합니다.",
        "is_free": False,
        "duration": "50분",
        "level": "중급",
        "content": {
            "sections": [
                {
                    "title": "Data Augmentation이란?",
                    "body": "기존 훈련 데이터를 변형해 **인위적으로 데이터셋을 확장**하는 기법입니다.\n\n- 데이터 수집 비용 없이 훈련 샘플 증가\n- 모델이 다양한 변형에 강인(Robust)해짐\n- 특히 의료 이미지, 위성 이미지처럼 데이터가 부족한 분야에서 필수"
                },
                {
                    "title": "Keras ImageDataGenerator",
                    "body": "Keras의 내장 증강 도구로 실시간 변환을 적용합니다.",
                    "code": "from tensorflow.keras.preprocessing.image import ImageDataGenerator\nimport numpy as np\nimport matplotlib.pyplot as plt\n\ndatagen = ImageDataGenerator(\n    rotation_range=30,        # ±30도 회전\n    width_shift_range=0.2,    # 수평 이동 20%\n    height_shift_range=0.2,   # 수직 이동 20%\n    shear_range=0.2,          # 전단 변환\n    zoom_range=0.2,           # 20% 줌인/아웃\n    horizontal_flip=True,     # 좌우 반전\n    fill_mode='nearest'       # 빈 공간 채우기\n)\n\n# 모델 학습에 적용\nmodel.fit(\n    datagen.flow(X_train, y_train, batch_size=32),\n    epochs=50,\n    validation_data=(X_val, y_val)\n)"
                },
                {
                    "title": "TensorFlow tf.data 파이프라인 증강",
                    "body": "최신 방법: tf.keras.layers로 증강 레이어를 모델에 포함시킵니다.",
                    "code": "import tensorflow as tf\n\n# 증강 레이어를 모델 입력부에 포함\ndata_augmentation = tf.keras.Sequential([\n    tf.keras.layers.RandomFlip(\"horizontal\"),\n    tf.keras.layers.RandomRotation(0.1),\n    tf.keras.layers.RandomZoom(0.1),\n    tf.keras.layers.RandomContrast(0.1),\n])\n\n# 모델 구성\ninputs = tf.keras.Input(shape=(224, 224, 3))\nx = data_augmentation(inputs)       # 증강 (훈련 시에만 적용)\nx = tf.keras.applications.MobileNetV2(include_top=False)(x)\nx = tf.keras.layers.GlobalAveragePooling2D()(x)\noutputs = tf.keras.layers.Dense(10, activation='softmax')(x)\n\nmodel = tf.keras.Model(inputs, outputs)"
                },
                {
                    "title": "Albumentations — 고급 증강 라이브러리",
                    "body": "Albumentations는 80+ 변환을 지원하는 고성능 증강 라이브러리입니다.",
                    "code": "# pip install albumentations\nimport albumentations as A\nimport cv2\nimport numpy as np\n\ntransform = A.Compose([\n    A.RandomCrop(width=224, height=224),\n    A.HorizontalFlip(p=0.5),\n    A.RandomBrightnessContrast(p=0.2),\n    A.GaussNoise(p=0.1),\n    A.Blur(blur_limit=3, p=0.1),\n    A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.05, rotate_limit=15, p=0.5),\n])\n\n# 이미지에 적용\nimage = cv2.imread(\"cat.jpg\")\nimage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)\naugmented = transform(image=image)\naugmented_image = augmented['image']"
                },
                {
                    "title": "핵심 요약",
                    "body": "| 기법 | 효과 | 주의사항 |\n|------|------|----------|\n| Flip | 방향 불변성 | 텍스트/숫자엔 부적합 |\n| Rotation | 각도 불변성 | 큰 각도는 정보 손실 |\n| Zoom | 스케일 불변성 | 과도하면 객체 잘림 |\n| Color Jitter | 조명 강인성 | 색상이 중요한 경우 주의 |\n| Cutout/Mixup | 일반화 성능 ↑ | 레이블 smoothing 필요 |"
                }
            ]
        }
    },
    {
        "id": 4,
        "title": "Transfer Learning — MobileNetV2로 나만의 분류기 만들기",
        "description": "ImageNet으로 사전학습된 MobileNetV2를 활용해 커스텀 이미지 분류기를 만듭니다.",
        "is_free": False,
        "duration": "60분",
        "level": "고급",
        "content": {
            "sections": [
                {
                    "title": "Transfer Learning이란?",
                    "body": "대규모 데이터셋에서 학습된 모델의 **지식을 새로운 태스크에 전이**하는 기법입니다.\n\n- ImageNet(1.2M 이미지, 1000 클래스)으로 학습된 모델의 특성 추출기를 재사용\n- 적은 데이터와 짧은 학습 시간으로 높은 성능 달성\n- 두 단계: Feature Extraction → Fine-Tuning"
                },
                {
                    "title": "MobileNetV2 아키텍처",
                    "body": "MobileNetV2는 모바일/임베디드용으로 설계된 경량 CNN입니다.\n\n- **Inverted Residual Block**: 확장(Expand) → Depthwise Conv → 축소(Project)\n- **Linear Bottleneck**: 마지막 레이어에 비선형 활성화 없음\n- ImageNet Top-5 정확도: 91.3% (파라미터 수: 3.4M)"
                },
                {
                    "title": "1단계: Feature Extraction (기반 레이어 동결)",
                    "body": "기반 모델의 가중치를 동결하고, 최상단 분류기만 학습합니다.",
                    "code": "import tensorflow as tf\n\n# 1. 기반 모델 로드 (분류 헤드 제외)\nbase_model = tf.keras.applications.MobileNetV2(\n    input_shape=(224, 224, 3),\n    include_top=False,          # ImageNet 분류 헤드 제외\n    weights='imagenet'          # 사전학습 가중치\n)\n\n# 2. 기반 모델 동결\nbase_model.trainable = False\n\n# 3. 커스텀 분류 헤드 추가\ninputs = tf.keras.Input(shape=(224, 224, 3))\nx = tf.keras.applications.mobilenet_v2.preprocess_input(inputs)\nx = base_model(x, training=False)\nx = tf.keras.layers.GlobalAveragePooling2D()(x)\nx = tf.keras.layers.Dropout(0.2)(x)\noutputs = tf.keras.layers.Dense(5, activation='softmax')(x)  # 5개 클래스\n\nmodel = tf.keras.Model(inputs, outputs)\n\n# 4. 분류 헤드만 학습\nmodel.compile(\n    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),\n    loss='categorical_crossentropy',\n    metrics=['accuracy']\n)\n\nmodel.fit(train_dataset, epochs=10, validation_data=val_dataset)"
                },
                {
                    "title": "2단계: Fine-Tuning (상위 레이어 해동)",
                    "body": "기반 모델 상위 레이어를 해동해 낮은 학습률로 미세 조정합니다.",
                    "code": "# 기반 모델의 상위 30개 레이어 해동\nbase_model.trainable = True\nfine_tune_at = len(base_model.layers) - 30\n\nfor layer in base_model.layers[:fine_tune_at]:\n    layer.trainable = False\n\nprint(f\"전체 레이어: {len(base_model.layers)}\")\nprint(f\"학습 가능 레이어: {sum(1 for l in base_model.layers if l.trainable)}\")\n\n# 낮은 Learning Rate로 재컴파일 (중요!)\nmodel.compile(\n    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),  # 10배 낮춤\n    loss='categorical_crossentropy',\n    metrics=['accuracy']\n)\n\nmodel.fit(\n    train_dataset,\n    epochs=20,\n    validation_data=val_dataset,\n    callbacks=[tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True)]\n)"
                },
                {
                    "title": "커스텀 데이터셋으로 꽃 분류기 만들기",
                    "body": "TensorFlow Flowers 데이터셋(5 클래스)으로 전체 파이프라인을 실행합니다.",
                    "code": "import tensorflow_datasets as tfds\n\n# 데이터 로드\n(train_ds, val_ds), info = tfds.load(\n    'tf_flowers',\n    split=['train[:80%]', 'train[80%:]'],\n    as_supervised=True,\n    with_info=True\n)\n\nIMG_SIZE = 224\nBATCH_SIZE = 32\n\ndef preprocess(image, label):\n    image = tf.image.resize(image, [IMG_SIZE, IMG_SIZE])\n    return image, tf.one_hot(label, 5)\n\ntrain_ds = train_ds.map(preprocess).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)\nval_ds = val_ds.map(preprocess).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)\n\n# 위 모델로 학습 후 평가\nloss, acc = model.evaluate(val_ds)\nprint(f\"Validation Accuracy: {acc:.2%}\")"
                },
                {
                    "title": "핵심 요약",
                    "body": "| 단계 | 동결 레이어 | Learning Rate | 목적 |\n|------|------------|---------------|------|\n| Feature Extraction | 전체 기반 모델 | 0.001 | 분류기 헤드 학습 |\n| Fine-Tuning | 하위 레이어만 | 0.00001 | 상위 특성 미세 조정 |\n\n**언제 각 방법을 사용할까?**\n- 데이터가 적고 기반 모델과 유사 → Feature Extraction만\n- 데이터가 중간 → Feature Extraction 후 Fine-Tuning\n- 데이터가 많고 다른 도메인 → 처음부터 학습"
                }
            ]
        }
    },
    {
        "id": 5,
        "title": "CNN 실습 — MNIST 손글씨 인식 모델 구현",
        "description": "CNN의 핵심 구성 요소를 이해하고 MNIST 데이터셋으로 99% 정확도 모델을 만듭니다.",
        "is_free": False,
        "duration": "55분",
        "level": "중급",
        "content": {
            "sections": [
                {
                    "title": "CNN 핵심 구성 요소",
                    "body": "CNN(Convolutional Neural Network)은 이미지 처리를 위해 설계된 신경망입니다.\n\n**Conv2D**: 작은 필터(커널)로 이미지를 슬라이딩하며 특성 추출\n- 파라미터 공유로 일반 Dense 대비 파라미터 수 대폭 감소\n- 위치 불변성(Translation Invariance) 확보\n\n**MaxPooling2D**: 공간 해상도를 줄이며 주요 특성 보존\n- 계산량 감소, 약한 위치 불변성 추가\n\n**Flatten → Dense**: 추출된 특성을 벡터화 후 분류"
                },
                {
                    "title": "MNIST 데이터 준비",
                    "body": "MNIST: 28×28 흑백 손글씨 숫자 이미지 70,000장 (0~9)",
                    "code": "import tensorflow as tf\nimport numpy as np\nimport matplotlib.pyplot as plt\n\n# 데이터 로드\n(X_train, y_train), (X_test, y_test) = tf.keras.datasets.mnist.load_data()\n\nprint(f\"훈련 데이터: {X_train.shape}\")   # (60000, 28, 28)\nprint(f\"테스트 데이터: {X_test.shape}\")  # (10000, 28, 28)\n\n# 전처리\nX_train = X_train.reshape(-1, 28, 28, 1).astype('float32') / 255.0\nX_test  = X_test.reshape(-1, 28, 28, 1).astype('float32') / 255.0\n\ny_train = tf.keras.utils.to_categorical(y_train, 10)\ny_test  = tf.keras.utils.to_categorical(y_test, 10)\n\n# 샘플 시각화\nfig, axes = plt.subplots(2, 5, figsize=(12, 5))\nfor i, ax in enumerate(axes.flat):\n    ax.imshow(X_train[i].reshape(28, 28), cmap='gray')\n    ax.set_title(f\"Label: {y_train[i].argmax()}\")\n    ax.axis('off')\nplt.show()"
                },
                {
                    "title": "CNN 모델 구현",
                    "body": "두 개의 Conv 블록과 완전연결층으로 구성된 MNIST 분류기입니다.",
                    "code": "model = tf.keras.Sequential([\n    # Block 1\n    tf.keras.layers.Conv2D(32, (3,3), padding='same', input_shape=(28,28,1)),\n    tf.keras.layers.BatchNormalization(),\n    tf.keras.layers.Activation('relu'),\n    tf.keras.layers.Conv2D(32, (3,3), padding='same'),\n    tf.keras.layers.BatchNormalization(),\n    tf.keras.layers.Activation('relu'),\n    tf.keras.layers.MaxPooling2D(2,2),\n    tf.keras.layers.Dropout(0.25),\n\n    # Block 2\n    tf.keras.layers.Conv2D(64, (3,3), padding='same'),\n    tf.keras.layers.BatchNormalization(),\n    tf.keras.layers.Activation('relu'),\n    tf.keras.layers.Conv2D(64, (3,3), padding='same'),\n    tf.keras.layers.BatchNormalization(),\n    tf.keras.layers.Activation('relu'),\n    tf.keras.layers.MaxPooling2D(2,2),\n    tf.keras.layers.Dropout(0.25),\n\n    # Classifier\n    tf.keras.layers.Flatten(),\n    tf.keras.layers.Dense(512, activation='relu'),\n    tf.keras.layers.BatchNormalization(),\n    tf.keras.layers.Dropout(0.5),\n    tf.keras.layers.Dense(10, activation='softmax')\n])\n\nmodel.summary()\n# Total params: ~1.2M"
                },
                {
                    "title": "학습 및 평가",
                    "body": "Learning Rate Scheduler와 Early Stopping을 사용해 최적 성능을 달성합니다.",
                    "code": "model.compile(\n    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),\n    loss='categorical_crossentropy',\n    metrics=['accuracy']\n)\n\ncallbacks = [\n    tf.keras.callbacks.EarlyStopping(\n        monitor='val_accuracy', patience=5, restore_best_weights=True\n    ),\n    tf.keras.callbacks.ReduceLROnPlateau(\n        monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6\n    )\n]\n\nhistory = model.fit(\n    X_train, y_train,\n    batch_size=128,\n    epochs=50,\n    validation_split=0.1,\n    callbacks=callbacks\n)\n\ntest_loss, test_acc = model.evaluate(X_test, y_test)\nprint(f\"테스트 정확도: {test_acc:.4f}\")  # 목표: 99%+"
                },
                {
                    "title": "오분류 분석",
                    "body": "모델이 틀린 예측을 시각화해 약점을 파악합니다.",
                    "code": "y_pred = model.predict(X_test)\ny_pred_classes = np.argmax(y_pred, axis=1)\ny_true_classes = np.argmax(y_test, axis=1)\n\n# 오분류 인덱스\nwrong_idx = np.where(y_pred_classes != y_true_classes)[0]\nprint(f\"오분류 수: {len(wrong_idx)} / {len(y_test)}\")\n\n# Confusion Matrix\nfrom sklearn.metrics import confusion_matrix\nimport seaborn as sns\n\ncm = confusion_matrix(y_true_classes, y_pred_classes)\nplt.figure(figsize=(10, 8))\nsns.heatmap(cm, annot=True, fmt='d', cmap='RdPu')\nplt.title('Confusion Matrix')\nplt.ylabel('True Label')\nplt.xlabel('Predicted Label')\nplt.show()"
                },
                {
                    "title": "핵심 요약",
                    "body": "**MNIST CNN 아키텍처 요약:**\n```\nInput (28×28×1)\n  → Conv(32) → BN → ReLU → Conv(32) → BN → ReLU → MaxPool → Dropout\n  → Conv(64) → BN → ReLU → Conv(64) → BN → ReLU → MaxPool → Dropout\n  → Flatten → Dense(512) → BN → Dropout → Dense(10, softmax)\n```\n\n**성능 목표:**\n- 기본 Dense: ~98%\n- CNN (위 구조): ~99.3%\n- 데이터 증강 추가: ~99.5%+"
                }
            ]
        }
    }
]


async def get_user_subscription(user_id: int) -> bool:
    if not user_id:
        return False
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id FROM subscriptions WHERE user_id=? AND status='active' LIMIT 1",
            (user_id,)
        )
        row = await cursor.fetchone()
        return row is not None


def get_user_id_from_header(authorization: Optional[str] = Header(None)) -> Optional[int]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1]
    return decode_token(token)


@router.get("")
async def list_courses():
    return [
        {
            "id": c["id"],
            "title": c["title"],
            "description": c["description"],
            "is_free": c["is_free"],
            "duration": c["duration"],
            "level": c["level"],
        }
        for c in COURSES
    ]


@router.get("/{course_id}")
async def get_course(
    course_id: int,
    authorization: Optional[str] = Header(None)
):
    course = next((c for c in COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    user_id = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        user_id = decode_token(token)

    is_subscribed = await get_user_subscription(user_id) if user_id else False
    can_view = course["is_free"] or is_subscribed

    return {
        "id": course["id"],
        "title": course["title"],
        "description": course["description"],
        "is_free": course["is_free"],
        "duration": course["duration"],
        "level": course["level"],
        "content": course["content"] if can_view else None,
        "locked": not can_view,
    }
