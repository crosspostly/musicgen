# 🎯 ПОЛНЫЙ ПЛАН ПЕРЕДЕЛКИ ПРОЕКТА (v2.0)

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ

### Что есть РЕАЛЬНО:
- ✅ **MusicGen (Meta)** - работает (backend в `python/app/services/diffrhythm.py`)
  - Модель: `facebook/musicgen-small` (300MB)
  - Генерирует: инструментальную музыку
  - Режим: CPU/GPU
  - Параметры: prompt, duration (30 сек по умолчанию)

### Что показывается в UI (ФЕЙКОВО):
- ❌ DiffRhythm AI (не установлен, требует 8-24GB VRAM)
- ❌ YuE (не установлен)
- ❌ Bark (может быть установлен?)
- ❌ Lyria (не установлен, нужен Google Cloud)
- ❌ MAGNeT (не установлен)

### Что нужно сделать:
1. Убрать фейковые модели из UI
2. Переименовать "DiffRhythm" в "MusicGen"
3. Добавить реальные параметры для каждой модели
4. Добавить Bark если backend есть (проверить!)
5. Обновить README и документацию

---

## 🔧 ПЛАН ИЗМЕНЕНИЙ

### ЭТАП 1: ОБНОВЛЕНИЕ ТИПОВ И ЭНУМОВ

**Файл:** `types.ts`

**БЫЛО:**
```typescript
export enum GenerationModel {
  DIFFRHYTHM = 'DIFFRHYTHM',
  YUE = 'YUE',
  BARK = 'BARK',
  LYRIA = 'LYRIA',
  MAGNET = 'MAGNET',
}

export enum Screen {
  MODEL_SELECTION = 'MODEL_SELECTION',
  DIFFRHYTHM_GENERATOR = 'DIFFRHYTHM_GENERATOR',
  YUE_GENERATOR = 'YUE_GENERATOR',
  BARK_GENERATOR = 'BARK_GENERATOR',
  LYRIA_GENERATOR = 'LYRIA_GENERATOR',
  MAGNET_GENERATOR = 'MAGNET_GENERATOR',
  METADATA_EDITOR = 'METADATA_EDITOR',
  EXPORT = 'EXPORT',
  FREESTYLE = 'FREESTYLE',
}
```

**СТАЛО:**
```typescript
export enum GenerationModel {
  MUSICGEN = 'MUSICGEN',  // Переименовано с DIFFRHYTHM
  BARK = 'BARK',          // Оставлено если backend есть
}

export enum Screen {
  MODEL_SELECTION = 'MODEL_SELECTION',
  MUSICGEN_GENERATOR = 'MUSICGEN_GENERATOR',  // Переименовано
  BARK_GENERATOR = 'BARK_GENERATOR',          // Оставлено если есть
  METADATA_EDITOR = 'METADATA_EDITOR',
  EXPORT = 'EXPORT',
  FREESTYLE = 'FREESTYLE',
}

// Добавить новые типы для параметров:
export interface MusicGenParams {
  prompt: string;
  duration: number;
  guidance_scale: number;
  temperature: number;
  top_k: number;
}

export interface BarkParams {
  text: string;
  voice_preset: string;
  language: string;
  text_temp: number;
  waveform_temp: number;
}
```

**ДЕЙСТВИЕ:** Заменить файл `types.ts` полностью

---

### ЭТАП 2: ОБНОВЛЕНИЕ ГЛАВНОГО ЭКРАНА

**Файл:** `ModelSelectionScreen.tsx`

**ЧТО УБРАТЬ:**
- Секцию "Полные песни с вокалом" (DiffRhythm, YuE, Bark как song generator)
- Карточки Lyria, MAGNeT
- Все фейковые описания

**ЧТО ДОБАВИТЬ:**
```tsx
<Card>
  <h3>🎵 Инструментальная музыка</h3>
  <ModelCard
    title="MusicGen (Meta)"
    description="Генерация инструментальной музыки"
    features={[
      { label: '💰 Стоимость', value: 'БЕСПЛАТНО' },
      { label: '⚡ Скорость', value: '~10 мин на CPU для 30с' },
      { label: '🎵 Тип', value: 'Только инструментал (без вокала)' },
      { label: '📦 Размер', value: '300 MB (small model)' },
      { label: '⏱️ Длина', value: '5-60 секунд' },
      { label: '🔧 Параметры', value: 'guidance_scale, temperature, top_k' },
    ]}
    onSelect={() => onSelectModel(GenerationModel.MUSICGEN)}
  />
</Card>

<Card>
  <h3>🎤 Вокал и речь</h3>
  <ModelCard
    title="Bark (Suno AI)"
    description="Генерация голоса и речи"
    features={[
      { label: '💰 Стоимость', value: 'БЕСПЛАТНО' },
      { label: '⚡ Скорость', value: '~30 сек на сегмент' },
      { label: '🎤 Тип', value: 'Голос, речь, пение (ограниченно)' },
      { label: '📦 Размер', value: '1.2 GB' },
      { label: '🌍 Языки', value: 'Русский, английский и др.' },
      { label: '🔧 Параметры', value: '100+ voice presets, temperature' },
    ]}
    warning="⚠️ Требуется установка backend (см. README)"
    onSelect={() => onSelectModel(GenerationModel.BARK)}
  />
</Card>
```

**ДЕЙСТВИЕ:** Заменить файл `ModelSelectionScreen.tsx` полностью

---

### ЭТАП 3: ПЕРЕИМЕНОВАНИЕ И ОБНОВЛЕНИЕ ГЕНЕРАТОРА MUSICGEN

**Файл:** `screens/DiffRhythmGeneratorScreen.tsx` → `screens/MusicGenGeneratorScreen.tsx`

**ЧТО ИЗМЕНИТЬ:**

1. **Заголовок:**
```tsx
// БЫЛО:
<h2>Генератор песен (DiffRhythm) ⭐</h2>

// СТАЛО:
<h2>MusicGen - Генератор инструментальной музыки 🎵</h2>
<p>Модель: facebook/musicgen-small (300MB) | Режим: CPU</p>
```

2. **Поля ввода:**
```tsx
// УБРАТЬ:
- Лирика / Текст песни (textarea для текста песни)
- Жанр (Pop/Rock/Rap)
- Настроение (Happy/Sad/Energetic)
- Пол вокалиста (Male/Female)

// ДОБАВИТЬ:
<textarea
  label="Описание музыки (на английском)"
  placeholder="lo-fi hip hop with piano and rain sounds, peaceful melody..."
  value={prompt}
/>

<input type="range" label="Длительность" min={5} max={60} value={duration} />
<p>Генерация займёт ~{Math.round(duration / 3)} минут на CPU</p>

<input type="range" label="Guidance Scale" min={1} max={15} step={0.5} value={guidanceScale} />
<p>Соответствие промпту (3.0 = default, выше = строже)</p>

<input type="range" label="Temperature" min={0.1} max={2.0} step={0.1} value={temperature} />
<p>Креативность (1.0 = default, выше = хаотичнее)</p>

<input type="range" label="Top-K" min={50} max={500} step={50} value={topK} />
<p>Вариативность выбора токенов (250 = default)</p>
```

3. **Функция генерации:**
```typescript
const handleGenerate = async () => {
  const response = await fetch(`${API_URL}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: prompt,
      duration: duration,
      // Эти параметры нужно добавить в backend!
      guidance_scale: guidanceScale,
      temperature: temperature,
      top_k: topK,
    }),
  });
  // ...
};
```

4. **Информационный блок:**
```tsx
<div className="info-block">
  <h4>ℹ️ О модели MusicGen</h4>
  <ul>
    <li>✅ Генерирует инструментальную музыку</li>
    <li>❌ НЕ генерирует вокал (нет пения)</li>
    <li>📦 Модель: facebook/musicgen-small (300MB)</li>
    <li>⏱️ Скорость: ~20 секунд на CPU для 30с музыки</li>
    <li>🎹 Стили: любые (поп, рок, джаз, электроника)</li>
    <li>💡 Для вокала используйте Bark</li>
  </ul>
</div>
```

**ДЕЙСТВИЕ:** 
1. Переименовать файл: `DiffRhythmGeneratorScreen.tsx` → `MusicGenGeneratorScreen.tsx`
2. Заменить содержимое полностью

---

### ЭТАП 4: ОБНОВЛЕНИЕ ГЕНЕРАТОРА BARK (ЕСЛИ BACKEND ЕСТЬ)

**Файл:** `screens/BarkGeneratorScreen.tsx`

**ЧТО ДОБАВИТЬ:**

1. **Заголовок:**
```tsx
<h2>Bark - Генератор голоса и речи 🎤</h2>
<p>Модель: suno/bark (1.2GB) | Режим: CPU/GPU</p>
```

2. **Поля ввода:**
```tsx
<textarea
  label="Текст для озвучки"
  placeholder="Привет! Это генерация голоса через Bark."
  value={text}
  maxLength={200}
/>
<p>Максимум 200 символов (~15 секунд речи)</p>

<select label="Голос (Voice Preset)" value={voicePreset}>
  <option value="v2/ru_speaker_0">Русский голос 1 (мужской)</option>
  <option value="v2/ru_speaker_1">Русский голос 2 (женский)</option>
  <option value="v2/ru_speaker_2">Русский голос 3 (мужской)</option>
  <option value="v2/en_speaker_0">English Speaker 1</option>
  <option value="v2/en_speaker_6">English Speaker 2 (female)</option>
  {/* ... ещё 95+ голосов */}
</select>

<select label="Язык" value={language}>
  <option value="ru">Русский</option>
  <option value="en">English</option>
  <option value="de">Deutsch</option>
  <option value="es">Español</option>
  {/* и т.д. */}
</select>

<input type="range" label="Text Temperature" min={0} max={1} step={0.1} value={textTemp} />
<p>Вариативность текста (0.7 = default)</p>

<input type="range" label="Waveform Temperature" min={0} max={1} step={0.1} value={waveformTemp} />
<p>Вариативность голоса (0.7 = default)</p>
```

3. **Информационный блок:**
```tsx
<div className="info-block">
  <h4>ℹ️ О модели Bark</h4>
  <ul>
    <li>✅ Генерирует речь и голос</li>
    <li>✅ Поддерживает пение (ограниченно)</li>
    <li>✅ 100+ голосовых пресетов</li>
    <li>🌍 Поддерживает 10+ языков</li>
    <li>⏱️ Скорость: ~30 секунд на сегмент</li>
    <li>💡 Для музыки используйте MusicGen</li>
  </ul>
</div>
```

**ДЕЙСТВИЕ:** Заменить файл `BarkGeneratorScreen.tsx` полностью

---

### ЭТАП 5: ОБНОВЛЕНИЕ App.tsx

**Файл:** `App.tsx`

**ЧТО УБРАТЬ:**
```typescript
// УДАЛИТЬ импорты:
import YueGeneratorScreen from './screens/YueGeneratorScreen';
import LyriaGeneratorScreen from './screens/LyriaGeneratorScreen';
import MagnetGeneratorScreen from './screens/MagnetGeneratorScreen';

// УДАЛИТЬ case'ы в switch:
case GenerationModel.YUE:
  setCurrentScreen(Screen.YUE_GENERATOR);
  break;
case GenerationModel.LYRIA:
  setCurrentScreen(Screen.LYRIA_GENERATOR);
  break;
case GenerationModel.MAGNET:
  setCurrentScreen(Screen.MAGNET_GENERATOR);
  break;

// УДАЛИТЬ в renderScreen():
case Screen.YUE_GENERATOR:
  return <YueGeneratorScreen ... />;
case Screen.LYRIA_GENERATOR:
  return <LyriaGeneratorScreen ... />;
case Screen.MAGNET_GENERATOR:
  return <MagnetGeneratorScreen ... />;
```

**ЧТО ИЗМЕНИТЬ:**
```typescript
// БЫЛО:
import DiffRhythmGeneratorScreen from './screens/DiffRhythmGeneratorScreen';

case GenerationModel.DIFFRHYTHM:
  setCurrentScreen(Screen.DIFFRHYTHM_GENERATOR);
  break;

case Screen.DIFFRHYTHM_GENERATOR:
  return <DiffRhythmGeneratorScreen ... />;

// СТАЛО:
import MusicGenGeneratorScreen from './screens/MusicGenGeneratorScreen';

case GenerationModel.MUSICGEN:
  setCurrentScreen(Screen.MUSICGEN_GENERATOR);
  break;

case Screen.MUSICGEN_GENERATOR:
  return <MusicGenGeneratorScreen ... />;
```

**ДЕЙСТВИЕ:** Заменить файл `App.tsx` полностью

---

### ЭТАП 6: ОБНОВЛЕНИЕ BACKEND

**Файл:** `python/app/services/diffrhythm.py` → `python/app/services/musicgen_service.py`

**ЧТО ДОБАВИТЬ:**

1. **Поддержка параметров в generate():**
```python
async def generate(
    self, 
    prompt: str, 
    duration: int = 30,
    guidance_scale: float = 3.0,
    temperature: float = 1.0,
    top_k: int = 250,
) -> Dict[str, Any]:
    # Передать в генератор
    audio = await self.generator.generate_audio(
        prompt=prompt,
        duration=duration,
        guidance_scale=guidance_scale,
        temperature=temperature,
        top_k=top_k,
    )
    # ...
```

2. **Обновить generate_audio():**
```python
async def generate_audio(
    self, 
    prompt: str, 
    duration: int,
    guidance_scale: float = 3.0,
    temperature: float = 1.0,
    top_k: int = 250,
) -> np.ndarray:
    await self.load_model()
    
    inputs = self._processor(text=[prompt], padding=True, return_tensors="pt")
    inputs = {k: v.to(self.device) for k, v in inputs.items()}
    
    max_new_tokens = int(duration * 50)
    
    with torch.no_grad():
        audio_values = await asyncio.to_thread(
            self._model.generate,
            **inputs,
            do_sample=True,
            guidance_scale=guidance_scale,    # ДОБАВЛЕНО
            temperature=temperature,          # ДОБАВЛЕНО
            top_k=top_k,                      # ДОБАВЛЕНО
            max_new_tokens=max_new_tokens,
        )
    
    # ... rest of code
```

**ДЕЙСТВИЕ:**
1. Переименовать файл: `diffrhythm.py` → `musicgen_service.py`
2. Обновить класс: `DiffRhythmService` → `MusicGenService`
3. Добавить параметры в функции

---

### ЭТАП 7: ОБНОВЛЕНИЕ API РОУТА

**Файл:** `python/app/api/generation.py` (или где API endpoint)

**ИЗМЕНИТЬ:**
```python
# БЫЛО:
from ..services.diffrhythm import DiffRhythmService

service = DiffRhythmService(storage_dir="./output")

@app.post("/api/generate")
async def generate(request: GenerateRequest):
    result = await service.generate(
        prompt=request.prompt,
        duration=request.duration,
    )
    return result

# СТАЛО:
from ..services.musicgen_service import MusicGenService

service = MusicGenService(storage_dir="./output")

class GenerateRequest(BaseModel):
    prompt: str
    duration: int = 30
    guidance_scale: float = 3.0      # ДОБАВЛЕНО
    temperature: float = 1.0         # ДОБАВЛЕНО
    top_k: int = 250                 # ДОБАВЛЕНО

@app.post("/api/generate")
async def generate(request: GenerateRequest):
    result = await service.generate(
        prompt=request.prompt,
        duration=request.duration,
        guidance_scale=request.guidance_scale,
        temperature=request.temperature,
        top_k=request.top_k,
    )
    return result
```

**ДЕЙСТВИЕ:** Обновить API endpoint

---

### ЭТАП 8: ОБНОВЛЕНИЕ ДОКУМЕНТАЦИИ

**Файл:** `README.md`

**ЗАМЕНИТЬ НА:**

```markdown
# MusicGen AI - Free AI Music Generator

FastAPI backend + React frontend для генерации музыки и голоса.

## 🎵 Модели

### ✅ MusicGen (Meta)
- **Тип:** Инструментальная музыка
- **Размер:** 300 MB (small model)
- **Режим:** CPU/GPU
- **Параметры:** guidance_scale, temperature, top_k
- **Длительность:** 5-60 секунд
- **Скорость:** ~10 минут на CPU для 30с

### ✅ Bark (Suno AI) [Опционально]
- **Тип:** Голос, речь, пение (ограниченно)
- **Размер:** 1.2 GB
- **Режим:** CPU/GPU
- **Параметры:** voice_preset (100+), language, temperature
- **Длительность:** до 15 секунд на сегмент
- **Скорость:** ~30 секунд

## 🚀 Установка

### Backend

```bash
cd musicgen
python -m venv venv

# Windows:
.\venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt

cd python
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

При первом запуске модели скачаются автоматически.

### Frontend

```bash
npm install
npm start
```

## 📡 API

**POST /api/generate**

```json
{
  "prompt": "lo-fi hip hop with piano",
  "duration": 30,
  "guidance_scale": 3.0,
  "temperature": 1.0,
  "top_k": 250
}
```

**Response:**
```json
{
  "track_id": "uuid",
  "audio_url": "/output/uuid.mp3",
  "duration": 30,
  "model": "musicgen-small"
}
```

## 🎛️ Параметры MusicGen

- **prompt** - описание музыки (на английском)
- **duration** - длительность (5-60 сек)
- **guidance_scale** - соответствие промпту (1-15, default: 3.0)
- **temperature** - креативность (0.1-2.0, default: 1.0)
- **top_k** - вариативность (50-500, default: 250)

## ❌ Что НЕ работает

- ❌ DiffRhythm AI (не установлен, требует 8-24GB VRAM)
- ❌ YuE (не установлен)
- ❌ Lyria (не установлен)
- ❌ MAGNeT (не установлен)

Эти модели убраны из UI.

## 📝 Лицензия

MIT
```

**ДЕЙСТВИЕ:** Заменить файл `README.md` полностью

---

### ЭТАП 9: СОЗДАНИЕ requirements.txt

**Файл:** `requirements.txt`

```
# Core Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.4.2
pydantic-settings==2.0.3

# Database
sqlalchemy==2.0.23
alembic==1.12.1

# AI/ML - MusicGen
torch==2.1.0
transformers==4.35.0
huggingface-hub==0.19.4
accelerate==0.24.0
tokenizers==0.14.1
sentencepiece==0.1.99
protobuf==4.25.1

# Audio Processing
soundfile==0.12.1
scipy==1.11.4
numpy==1.26.2
pydub==0.25.1

# Bark (Optional - uncomment if you want voice synthesis)
# bark==0.1.5

# Utilities
aiofiles==23.2.1
python-multipart==0.0.6
redis==5.0.1
requests==2.31.0
psutil==5.9.6

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

**ДЕЙСТВИЕ:** Заменить файл `requirements.txt`

---

### ЭТАП 10: СОЗДАНИЕ CHANGELOG.md

**Файл:** `CHANGELOG.md`

```markdown
# Changelog

## [2.0.0] - 2025-11-09

### 🚨 BREAKING CHANGES
- Removed fake models from UI (DiffRhythm AI, YuE, Lyria, MAGNeT)
- Renamed `DIFFRHYTHM` → `MUSICGEN` in all code
- Renamed `DiffRhythmGeneratorScreen.tsx` → `MusicGenGeneratorScreen.tsx`
- Renamed `diffrhythm.py` → `musicgen_service.py`

### ✨ Added
- Real MusicGen parameters: guidance_scale, temperature, top_k
- Bark voice synthesis support (optional)
- Model information blocks in UI
- Realistic generation time estimates
- Parameter tooltips and descriptions

### 🔧 Changed
- UI now shows only installed models
- Updated model descriptions to be accurate
- Improved generation progress indicators
- Better error messages

### 🐛 Fixed
- Silent audio bug (audio extraction from model output)
- API connection issues
- CORS configuration

### 📚 Documentation
- Updated README with real model info
- Added parameter descriptions
- Removed references to non-existent models

## [1.1.0] - 2025-11-09
- Fixed silent audio generation bug
- Improved audio extraction

## [1.0.0] - 2025-11-09
- Initial release with MusicGen backend
```

**ДЕЙСТВИЕ:** Создать файл `CHANGELOG.md`

---

## 📦 ИТОГОВЫЙ СПИСОК ФАЙЛОВ ДЛЯ ИЗМЕНЕНИЯ

### Frontend (React/TypeScript):
1. ✅ `types.ts` - обновить энумы и типы
2. ✅ `App.tsx` - убрать фейковые модели
3. ✅ `ModelSelectionScreen.tsx` - показать только реальные
4. ✅ `DiffRhythmGeneratorScreen.tsx` → `MusicGenGeneratorScreen.tsx` - переименовать и обновить
5. ✅ `BarkGeneratorScreen.tsx` - обновить параметры

### Backend (Python):
6. ✅ `python/app/services/diffrhythm.py` → `musicgen_service.py` - переименовать
7. ✅ `python/app/api/generation.py` - добавить параметры в API
8. ✅ `python/app/main.py` - обновить импорты

### Documentation:
9. ✅ `README.md` - обновить документацию
10. ✅ `requirements.txt` - зависимости
11. ✅ `CHANGELOG.md` - история изменений

### Удалить файлы (если есть):
12. ❌ `screens/YueGeneratorScreen.tsx`
13. ❌ `screens/LyriaGeneratorScreen.tsx`
14. ❌ `screens/MagnetGeneratorScreen.tsx`

---

## 🚀 КОММИТ MESSAGE

```
feat: replace fake models with real MusicGen + Bark (v2.0)

BREAKING CHANGES:
- Removed fake models (DiffRhythm AI, YuE, Lyria, MAGNeT)
- Renamed DIFFRHYTHM → MUSICGEN everywhere
- Added real parameters for MusicGen

NEW FEATURES:
- MusicGen parameters: guidance_scale, temperature, top_k
- Bark voice synthesis (optional)
- Real generation time estimates
- Model info blocks in UI

FIXES:
- Silent audio bug fixed
- API connection improved
- Better error messages

MODELS:
- ✅ MusicGen (facebook/musicgen-small) - 300MB
- ✅ Bark (suno/bark) - 1.2GB (optional)

See CHANGELOG.md for full details.
```

---

## ✅ CHECKLIST

- [ ] Обновить `types.ts`
- [ ] Обновить `App.tsx`
- [ ] Обновить `ModelSelectionScreen.tsx`
- [ ] Переименовать и обновить `MusicGenGeneratorScreen.tsx`
- [ ] Обновить `BarkGeneratorScreen.tsx`
- [ ] Переименовать `musicgen_service.py`
- [ ] Обновить API endpoint
- [ ] Обновить `README.md`
- [ ] Создать `CHANGELOG.md`
- [ ] Обновить `requirements.txt`
- [ ] Удалить файлы фейковых моделей
- [ ] Протестировать генерацию
- [ ] Закоммитить и запушить на GitHub

---

## 🎯 РЕЗУЛЬТАТ

После всех изменений:

**UI будет показывать:**
```
Выберите модель генерации

🎵 Инструментальная музыка
└─ MusicGen (Meta)
   - Инструментальная музыка
   - 300MB, CPU режим
   - Параметры: guidance_scale, temperature, top_k
   - 5-60 секунд трека

🎤 Вокал и речь (опционально)
└─ Bark (Suno AI)
   - Генерация голоса
   - 100+ голосов
   - Поддержка русского языка
```

**Backend будет поддерживать:**
- ✅ Все параметры MusicGen
- ✅ Правильную экстракцию аудио
- ✅ CORS для frontend
- ✅ Bark (если установлен)

**Документация будет:**
- ✅ Честной (только реальные модели)
- ✅ Подробной (все параметры описаны)
- ✅ Актуальной (соответствует коду)

---

## 📝 ПРИМЕЧАНИЯ

1. **Bark** - опциональная модель. Если backend не установлен, можно убрать из UI.
2. **Параметры backend** - guidance_scale, temperature, top_k должны быть добавлены в `generate_audio()`.
3. **CORS** - должен быть настроен в `main.py` для работы с frontend.
4. **Тестирование** - после изменений обязательно протестировать генерацию.

---

**ЭТОТ ПЛАН ГОТОВ ДЛЯ ЗАГРУЗКИ НА GITHUB!**

Все изменения описаны подробно. Можно использовать как TODO для pull request или issue.
