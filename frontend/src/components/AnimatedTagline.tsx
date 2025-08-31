import React, { useState, useEffect } from 'react';

interface AnimatedTaglineProps {
  text: string;
  speed?: number;
  className?: string;
}

const AnimatedTagline: React.FC<AnimatedTaglineProps> = ({ 
  text, 
  speed = 50, 
  className = "" 
}) => {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(true);


  useEffect(() => {
    if (currentIndex < text.length && isTyping) {
      const timeout = setTimeout(() => {
        setDisplayText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);

      return () => clearTimeout(timeout);
    } else if (currentIndex >= text.length) {
      setIsTyping(false);
    }
  }, [currentIndex, text, speed, isTyping]);

  return (
    <div className={`text-center ${className}`}>
      <div className="inline-block relative">
        <span className="text-2xl sm:text-3xl lg:text-4xl font-light text-gray-800 tracking-wide">
          {displayText}
        </span>
        {isTyping && (
          <span className="text-2xl sm:text-3xl lg:text-4xl text-blue-600 animate-pulse font-mono">
            |
          </span>
        )}

      </div>
    </div>
  );
};

export default AnimatedTagline;
