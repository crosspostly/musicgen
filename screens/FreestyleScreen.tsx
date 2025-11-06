
import React, { useState, useEffect, useRef } from 'react';
import { Card, Button, Slider } from '../components/common';
import { ArrowLeftIcon, PlayIcon, StopIcon, PauseIcon } from '../components/icons';

interface FreestyleScreenProps {
  onBack: () => void;
}

type RecordingState = 'idle' | 'recording' | 'paused' | 'finished';

const FreestyleScreen: React.FC<FreestyleScreenProps> = ({ onBack }) => {
  const [instrument, setInstrument] = useState('Пианино');
  const [reverb, setReverb] = useState(0.3);
  const [delay, setDelay] = useState(0.2);
  const [recordingState, setRecordingState] = useState<RecordingState>('idle');
  const [recordTime, setRecordTime] = useState(0);

  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (recordingState === 'recording') {
      intervalRef.current = window.setInterval(() => {
        setRecordTime(prev => prev + 1);
      }, 1000);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [recordingState]);

  const handleRecord = () => {
    if (recordingState === 'idle' || recordingState === 'finished') {
        setRecordTime(0);
        setRecordingState('recording');
    } else if (recordingState === 'paused') {
        setRecordingState('recording');
    }
  };

  const handlePause = () => setRecordingState('paused');
  const handleStop = () => setRecordingState('finished');
  
  const formatTime = (seconds: number) => {
    const min = Math.floor(seconds / 60).toString().padStart(2, '0');
    const sec = (seconds % 60).toString().padStart(2, '0');
    return `${min}:${sec}`;
  };

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <Button variant="secondary" onClick={onBack} className="mb-4">
        <ArrowLeftIcon />
        Назад к выбору модели
      </Button>
      <h2 className="text-3xl font-bold mb-6 text-center">🎸 Свободная импровизация</h2>

      <div className="grid md:grid-cols-3 gap-8">
        <Card className="md:col-span-1 space-y-6">
          <div>
            <h3 className="text-lg font-bold mb-2">Инструмент</h3>
            <div className="space-y-2">
                {['Пианино', 'Гитара', 'Синтезатор'].map(inst => (
                    <Button key={inst} variant={instrument === inst ? 'primary' : 'secondary'} className="w-full" onClick={() => setInstrument(inst)}>{inst}</Button>
                ))}
            </div>
          </div>
           <div>
            <h3 className="text-lg font-bold mb-2">Эффекты</h3>
            <div className="space-y-4">
                <Slider label="Реверберация" value={reverb} min={0} max={1} step={0.05} onChange={e => setReverb(+e.target.value)} hint="Добавляет пространственное эхо"/>
                <Slider label="Дилэй" value={delay} min={0} max={1} step={0.05} onChange={e => setDelay(+e.target.value)} hint="Создает повторяющиеся отзвуки"/>
            </div>
          </div>
        </Card>
        <Card className="md:col-span-2 flex flex-col items-center justify-center">
            <div className="text-center">
                <h3 className="text-6xl font-bold font-mono tracking-tighter mb-4">{formatTime(recordTime)}</h3>
                <div className="h-24 w-full bg-gray-900 rounded-lg flex items-center justify-center mb-6">
                    <p className="text-gray-500">Здесь будет визуализация звука (симуляция)</p>
                </div>
                <div className="flex justify-center items-center gap-4">
                    {recordingState !== 'recording' && (
                        <Button onClick={handleRecord} className="!p-4 !rounded-full text-lg">
                            <PlayIcon className="w-8 h-8"/>
                        </Button>
                    )}
                     {recordingState === 'recording' && (
                        <Button onClick={handlePause} variant="secondary" className="!p-4 !rounded-full text-lg">
                            <PauseIcon className="w-8 h-8"/>
                        </Button>
                     )}
                     <Button onClick={handleStop} variant="danger" className="!p-6 !rounded-full text-lg">
                        <StopIcon className="w-10 h-10"/>
                    </Button>
                </div>
                {recordingState === 'finished' && <p className="mt-4 text-green-400">Запись завершена! ({formatTime(recordTime)})</p>}
            </div>
        </Card>
      </div>
    </div>
  );
};

export default FreestyleScreen;
