'use client';

import { useMemo } from 'react';

const HeartParticles = () => {
  const particles = useMemo(() => {
    return Array(15).fill(null).map(() => ({
      left: Math.random() * 100,
      top: Math.random() * 100,
      duration: 10 + Math.random() * 10,
      delay: Math.random() * 10,
    }));
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((particle, i) => (
        <div
          key={i}
          className="absolute animate-float"
          style={{
            left: `${particle.left}%`,
            top: `${particle.top}%`,
            animation: `float ${particle.duration}s linear infinite`,
            animationDelay: `-${particle.delay}s`,
          }}
        >
          <div className="text-blue-400 opacity-30 text-2xl transform rotate-45">
            ♥
          </div>
        </div>
      ))}
    </div>
  );
};

export default HeartParticles; 