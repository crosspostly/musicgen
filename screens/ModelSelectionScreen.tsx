
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
        <p className="mt-2 text-lg text-gray-400">Доступны реальные модели с полной поддержкой параметров.</p>
      </div>

      <Card className="!p-0 border-indigo-500/50">
        <div className="p-4 bg-indigo-900/30 rounded-t-lg">
          <h3 className="text-2xl font-bold text-white flex items-center gap-3">🎵 Инструментальная музыка</h3>
        </div>
        <div className="p-6 grid md:grid-cols-1 lg:grid-cols-2 gap-6">
          <ModelCard
            isRecommended
            title="MusicGen"
            description="Meta"
            features={[
              { label: '💰 Стоимость', value: 'БЕСПЛАТНО' },
              { label: '⚡ Скорость', value: '~10 мин на CPU для 30с' },
              { label: '📦 Размер модели', value: '300 MB' },
              { label: '⏱️ Длительность', value: '5-60 секунд' },
              { label: '🔧 Параметры', value: 'guidance_scale, temperature, top_k' },
            ]}
            warning="✅ Генерирует только инструментальную музыку"
            onSelect={() => onSelectModel(GenerationModel.MUSICGEN)}
          />
        </div>
      </Card>

      <Card>
        <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">🎤 Вокал и речь</h3>
        <div className="grid md:grid-cols-1 lg:grid-cols-2 gap-6">
          <ModelCard
            title="Bark"
            description="Suno AI"
            features={[
              { label: '💰 Стоимость', value: 'БЕСПЛАТНО' },
              { label: '⚡ Скорость', value: '~30 сек на сегмент' },
              { label: '🌍 Голоса', value: '100+ голосов, поддержка русского' },
              { label: '⏱️ Длина', value: 'макс 150 символов (~15 сек)' },
              { label: '🎭 Особенности', value: 'смех, пение, шепот, эмоции' },
            ]}
            warning="⚠️ Требуется установка backend"
            onSelect={() => onSelectModel(GenerationModel.BARK)}
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
