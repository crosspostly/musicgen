# MusicGen Local - AI Music Creation Suite

> 🎵 **Create, process, and monetize music with AI**  
> Local application for mass music creation and automatic distribution to streaming platforms

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 16+](https://img.shields.io/badge/node.js-16+-green.svg)](https://nodejs.org/)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/crosspostly/musicgen
cd musicgen

# Run with Docker (recommended)
docker-compose up

# Or run locally
npm run install:all  # Install frontend and backend dependencies
cp .env.example .env  # Configure environment variables
npm run dev          # Start both frontend and backend
```

Web interface opens at `http://localhost:3000`  
Backend API available at `http://localhost:3001`

## ✨ Core Features (MVP Phase 1)

- **⚡ DiffRhythm Integration** - Generate music in ~10 seconds with natural vocals
- **🎵 Audio Loop Creator** - Create 1-10 hour loops for YouTube streams  
- **📝 Metadata Editor** - Batch edit titles, artists, genres
- **🖥️ Web Interface** - Intuitive UI for all functions

## 🎯 AI Models

| Model | Speed | Quality | Max Duration | Size |
|--------|----------|----------|--------------|--------|
| **DiffRhythm ⭐** | ~10 sec | Excellent | 4:45 min | 3.2GB |

## 📁 Project Structure

```
musicgen/
├── components/              # Reusable UI components
├── screens/                # Main application screens  
├── services/               # Frontend API integration layer
├── backend/                # Node.js + Express API server
│   ├── src/
│   │   ├── config/        # Environment and logging config
│   │   ├── controllers/   # Request handlers
│   │   ├── routes/        # API route definitions
│   │   ├── services/      # Business logic layer
│   │   ├── db/           # Database operations
│   │   ├── middleware/    # Express middleware
│   │   └── types/        # TypeScript definitions
│   ├── tests/            # Backend test suite
│   └── package.json      # Backend dependencies
├── docker-compose.yml     # Multi-service deployment
├── requirements.txt       # Python dependencies (for future AI services)
└── .env.example          # Environment configuration
```

## 🛠️ Development

**Возможности**:
- Анализ точек зацикливания
- Плавные переходы без щелчков
- Настраиваемая длительность (1 мин - 10 часов)
- Экспорт в MP3/WAV высокого качества

### 📤 Export & Looping Workflow
Улучшенный экспортный экран с интеграцией loop-создания:

```javascript
// Шаг 1: Просмотр и загрузка оригинального трека
// - MP3/WAV форматы высокого качества
// - Встроенный аудио-плеер для предварительного прослушивания
// - Редактирование метаданных (исполнитель, альбом, жанр)

// Шаг 2: Создание бесшовного loop
const loopOptions = {
  trackId: 'track-123',
  duration: 3600,        // 1 час (1 мин - 10 часов)
  fadeInOut: true,       // Плавные переходы
  format: 'mp3'          // или 'wav'
};

// Шаг 3: Отслеживание прогресса
// - Анализ аудио для оптимальных точек loop
// - Рендеринг с плавными переходами
// - Экспорт в выбранный формат
// - Загрузка файла в локальное хранилище

// Шаг 4: Управление экспортами
// - Список всех созданных loop-файлов
// - Информация о сохраненных путях
// - Кнопки для загрузки готовых файлов
```

**Особенности**:
- Пошаговый workflow от генерации до экспорта
- Прогресс-бары для отслеживания создания loop
- Обработка ошибок с кнопкой повтора
- Хранение файлов в локальной файловой системе
- Поддержка MP3 и WAV форматов
- Настраиваемые параметры fade-in/out

### 📺 YouTube Integration
Полная автоматизация YouTube workflow:

```javascript
// Автозагрузка с метаданными
await youtube.uploadTrack({
  audioFile: 'looped_track.mp3',
  title: 'Lo-Fi Hip Hop Radio - 24/7 Study Music',
  description: 'Relaxing beats for study and work...',
  thumbnail: 'cover_1280x720.jpg',
  scheduledFor: '2025-11-07T10:00:00Z'
});
```

**Интеграции**:
- YouTube Data API v3 + Upload API
- OAuth 2.0 аутентификация
- Планировщик публикаций
- Автоматические теги и описания

### 🖼️ Cover Auto Cropper
Умная обрезка обложек под все платформы:

```javascript
// Автообрезка под форматы
await coverCropper.processImage({
  input: 'original_cover.jpg',
  formats: {
    spotify: '1000x1000',        // Квадрат
    youtube: '1280x720',         // YouTube thumbnail
    instagram: '1080x1080'       // Instagram пост
  },
  smartCrop: true  // Детекция объектов/лиц
});
```
### System Requirements
- **Node.js** 16+ 
- **Python** 3.8+
- **Docker** (optional but recommended)
- **Free space**: 5GB+ for AI models

### Setup
```bash
# Copy environment file
cp .env.example .env

# Install all dependencies (frontend + backend)
npm run install:all

# Start development servers
npm run dev          # Both frontend (3000) and backend (3001)
npm run dev:frontend # Frontend only
npm run dev:backend  # Backend only
```

### Available Scripts
- `npm run dev` - Start both frontend and backend concurrently
- `npm run dev:frontend` - Start React development server (port 3000)
- `npm run dev:backend` - Start Express API server (port 3001)
- `npm run build` - Build both frontend and backend
- `npm run test` - Run all tests
- `npm run test:backend` - Run backend tests only

### Backend Development
The Node.js backend provides:
- REST API at `http://localhost:3001/api`
- SQLite database with auto-initialization
- File storage management
- Job orchestration and progress tracking
- Health check endpoints

See `backend/src/` for complete implementation.

## 📖 Documentation

- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical architecture and setup
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide

## 🤝 Contributing

We welcome community contributions! See the implementation guide for technical details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**⭐ Star the repo if you find it useful!**

Created with ❤️ for music enthusiasts and entrepreneurs