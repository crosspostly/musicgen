
import React from 'react';
import { GenerationModel, Screen } from '../types';
import { Card } from '../components/common';
import { ChevronRightIcon, MicrophoneIcon } from '../components/icons';

interface ModelSelectionScreenProps {
  onSelectModel: (model: GenerationModel) => void;
  onNavigate: (screen: Screen) => void;
}

const ModelCard: React.FC<{
  title: string;
  description: string;
  features: { label: string; value: string }[];
  warning?: string;
  onSelect: () => void;
  isRecommended?: boolean;
}> = ({ title, description, features, warning, onSelect, isRecommended }) => (
  <div className={`bg-gray-800 border ${isRecommended ? 'border-indigo-500' : 'border-gray-700'} rounded-lg shadow-lg p-6 flex flex-col h-full hover:border-indigo-400 hover:bg-gray-800/50 transition-all duration-300 transform hover:-translate-y-1`}>
    <div className="flex-grow">
      <h3 className={`text-2xl font-bold ${isRecommended ? 'text-indigo-400' : 'text-white'}`}>{title}</h3>
      <p className="text-gray-400 mt-1">{description}</p>
      <div className="mt-4 space-y-2 text-sm">
        {features.map((feature, index) => (
          <p key={index}><span className="font-semibold text-gray-300">{feature.label}:</span> <span className="text-gray-400">{feature.value}</span></p>
        ))}
      </div>
      {warning && <p className="mt-3 text-xs text-amber-400 bg-amber-900/50 p-2 rounded-md">{warning}</p>}
    </div>
    <button onClick={onSelect} className="mt-6 w-full bg-indigo-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-indigo-500 transition-colors flex items-center justify-center gap-2">
      Перейти к {title.split(' ')[0]}
      <ChevronRightIcon className="w-5 h-5" />
    </button>
  </div>
);

const ModelSelectionScreen: React.FC<ModelSelectionScreenProps> = ({ onSelectModel, onNavigate }) => {
  return (
    <div className="animate-fade-in space-y-12">
      <div className="text-center">
        <h2 className="text-4xl font-extrabold text-white">Выберите модель генерации</h2>
        <p className="mt-2 text-lg text-gray-400">Каждая модель предлагает уникальные возможности и результаты.</p>
      </div>

      <Card className="!p-0 border-indigo-500/50">
        <div className="p-4 bg-indigo-900/30 rounded-t-lg">
          <h3 className="text-2xl font-bold text-white flex items-center gap-3"><MicrophoneIcon /> Полные песни с вокалом (инструменты + пение)</h3>
        </div>
        <div className="p-6 grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ModelCard
            isRecommended
            title="DiffRhythm ⭐"
            description="ASLP-Lab"
            features={[
              { label: '📊 Стоимость', value: 'БЕСПЛАТНО' },
              { label: '⚡ Скорость', value: 'ОЧЕНЬ БЫСТРО (песня за ~10 сек!)' },
              { label: '🎵 Качество', value: 'Отличное, естественный вокал' },
              { label: '⏱️ Длина', value: 'До 4:45 минут' },
            ]}
            warning="✓ ИДЕАЛЬНО для перепродажи на стриминге"
            onSelect={() => onSelectModel(GenerationModel.DIFFRHYTHM)}
          />
          <ModelCard
            title="YuE"
            description="Multimodal Art Projection"
            features={[
              { label: '📊 Стоимость', value: 'БЕСПЛАТНО' },
              { label: '⚡ Скорость', value: 'Быстро (~30-40 сек за песню)' },
              { label: '🎵 Качество', value: 'Отличное, синхронный вокал' },
              { label: '🔧 Управление', value: 'Контроль над инструментами' },
            ]}
            warning="✓ Лучше для Rock/Metal и сложных аранжировок"
            onSelect={() => onSelectModel(GenerationModel.YUE)}
          />
          <ModelCard
            title="Bark"
            description="Suno AI"
            features={[
              { label: '📊 Стоимость', value: 'БЕСПЛАТНО' },
              { label: '⚡ Скорость', value: 'Среднее (~20 сек на сегмент)' },
              { label: '🎤 Тип вокала', value: '100+ голосовых пресетов' },
              { label: '✨ Особенность', value: 'Спецэффекты (смех, шепот)' },
            ]}
            warning="✓ Для разговорных интро и спецэффектов"
            onSelect={() => onSelectModel(GenerationModel.BARK)}
          />
        </div>
      </Card>

      <Card>
        <h3 className="text-2xl font-bold text-white mb-6">🎵 Инструментальная музыка (без вокала)</h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <ModelCard
            title="Lyria RealTime"
            description="Google DeepMind"
            features={[
              { label: '💰 Стоимость', value: '$0.06 за 30 сек' },
              { label: '⚡ Скорость', value: 'Очень быстро' },
              { label: '🎵 Качество', value: 'Профессиональное (48kHz)' },
              { label: '🔧 Управление', value: 'Real-time контроль' },
            ]}
            warning="Требует: Google Cloud API ключ"
            onSelect={() => onSelectModel(GenerationModel.LYRIA)}
          />
          <ModelCard
            title="MAGNeT"
            description="Facebook Open-Source"
            features={[
              { label: '💰 Стоимость', value: 'Бесплатно' },
              { label: '⚡ Скорость', value: 'Медленнее' },
              { label: '🎵 Качество', value: 'Хорошее (16kHz)' },
              { label: '🔧 Управление', value: 'Фиксированные параметры' },
            ]}
            warning="✅ Локально, полный контроль"
            onSelect={() => onSelectModel(GenerationModel.MAGNET)}
          />
          <div onClick={() => onNavigate(Screen.FREESTYLE)} className="cursor-pointer bg-gray-800 border border-dashed border-gray-600 rounded-lg p-6 flex flex-col h-full hover:border-indigo-400 hover:bg-gray-800/50 transition-all duration-300 transform hover:-translate-y-1 items-center justify-center text-center">
             <h3 className="text-2xl font-bold text-white">Свободная импровизация</h3>
             <p className="text-gray-400 mt-2">Играйте на виртуальных инструментах, применяйте эффекты и записывайте свои мелодии в реальном времени.</p>
             <div className="mt-4 text-indigo-400 font-semibold flex items-center gap-2">
                 Начать импровизировать <ChevronRightIcon className="w-5 h-5" />
             </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ModelSelectionScreen;
