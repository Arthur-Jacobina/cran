interface AudioVisualizerProps {
  audioData: number[];
}

export const AudioVisualizer: React.FC<AudioVisualizerProps> = ({ audioData }) => {
  // Convert the 0-255 range audio data to a height percentage
  const getBarHeight = (value: number) => {
    // The audio data is centered around 128 (silence)
    // Calculate distance from center (128)
    const amplitude = Math.abs(value - 128)*2;
    
    // Scale the amplitude to create a more visible effect
    // This will give a minimum height of 4px and scale up to 40px for loud sounds
    return Math.max(4, (amplitude / 128) * 36 + 4);
  };

  return (
    <div className="flex items-center justify-center bg-gray-50 gap-0.5 w-full">
      {audioData.map((value, index) => (
        <div
          key={index}
          className="w-full bg-blue-500 rounded-xs transition-all duration-75"
          style={{
            height: `${getBarHeight(value)}px`,
          }}
        />
      ))}
    </div>
  );
};