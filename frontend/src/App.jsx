import React, { useRef, useState } from 'react';
import { motion, useScroll, useTransform, useSpring } from 'framer-motion';
import { ArrowRight, FileText } from 'lucide-react';

export default function App() {
  const containerRef = useRef(null);
  const [isLaunching, setIsLaunching] = useState(false);

  // Global scroll progression for the portal zoom section
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end start'],
  });

  const smoothProgress = useSpring(scrollYProgress, {
    stiffness: 90,
    damping: 25,
    restDelta: 0.001,
  });

  // Circle mask expands from initial circle to full viewport on scroll
  const clipRadius = useTransform(smoothProgress, [0, 0.45], [7, 150]);
  const imageScale = useTransform(smoothProgress, [0, 0.45], [1.25, 1.0]);
  
  // Headline & Subtitle fade in as portal expands
  const textOpacity = useTransform(smoothProgress, [0.05, 0.25], [0, 1]);
  const textScale = useTransform(smoothProgress, [0.05, 0.25], [0.95, 1]);

  // Button slides up and fades in on scrolling further
  const buttonOpacity = useTransform(smoothProgress, [0.15, 0.35], [0, 1]);
  const buttonY = useTransform(smoothProgress, [0.15, 0.35], [80, 0]);

  const handleLaunchProject = () => {
    const configuredUrl = import.meta.env.VITE_FILING_INSIGHT_URL || 'http://localhost:8501';
    setIsLaunching(true);
    window.location.assign(configuredUrl);
  };

  return (
    <div className="relative w-full bg-black text-white selection:bg-white/20">
      
      {/* HERO SECTION WITH PORTAL & DYNAMIC SCROLL OVERLAYS */}
      <div ref={containerRef} className="relative h-[220vh] w-full bg-black">
        <div className="sticky top-0 h-screen w-screen overflow-hidden flex items-center justify-center bg-black">
          
          {/* Animated Circle Mask Reveal Layer */}
          <motion.div
            style={{
              clipPath: useTransform(clipRadius, (r) => `circle(${r}% at 50% 50%)`),
              WebkitClipPath: useTransform(clipRadius, (r) => `circle(${r}% at 50% 50%)`),
            }}
            className="absolute inset-0 w-full h-full"
          >
            {/* Clean Wallpaper Background Image Layer (No Baked-In Text) */}
            <motion.div style={{ scale: imageScale }} className="absolute inset-0 w-full h-full">
              <img
                src="/assets/hero-bg.jpg"
                alt="Workspace Nighttime View"
                className="w-full h-full object-cover select-none"
              />
              <div className="absolute inset-0 bg-black/35 pointer-events-none" />
            </motion.div>

            {/* Top-left branding */}
            <div className="absolute top-6 left-6 md:top-10 md:left-10 z-20">
              <span className="font-display font-bold text-lg md:text-xl tracking-tight text-white/90 drop-shadow-md">
                Know Da Numbers
              </span>
            </div>

            {/* Center Typography & Glass-Morphed Pop-up Button */}
            <div className="absolute inset-0 w-full h-full flex flex-col items-center justify-center text-center px-4 z-20 pointer-events-auto">
              
              {/* Main Headlines */}
              <motion.div
                style={{ opacity: textOpacity, scale: textScale }}
                className="flex flex-col items-center max-w-4xl mx-auto mb-10"
              >
                <h1 className="font-display text-4xl sm:text-6xl md:text-7xl font-bold tracking-tight text-white leading-tight mb-4 drop-shadow-lg">
                  Where Filings Become Intelligence.
                </h1>
                
                <p className="text-base sm:text-xl md:text-2xl text-white/80 font-light tracking-wide drop-shadow-md">
                  Decode. Discover. Decide.
                </p>
              </motion.div>

              {/* Pop-up Glass Morphed Button that slides from below on scrolling */}
              <motion.div
                style={{
                  opacity: buttonOpacity,
                  y: buttonY,
                }}
                className="mt-2"
              >
                <button
                  onClick={handleLaunchProject}
                  disabled={isLaunching}
                  aria-busy={isLaunching}
                  className="group relative px-8 py-4 sm:px-10 sm:py-5 rounded-2xl bg-white/10 hover:bg-white/20 backdrop-blur-xl border border-white/25 text-white font-display text-lg sm:text-xl font-semibold tracking-wide shadow-[0_8px_32px_0_rgba(0,0,0,0.5),inset_0_0_0_1px_rgba(255,255,255,0.15)] hover:shadow-[0_8px_40px_0_rgba(255,255,255,0.2),inset_0_0_0_1px_rgba(255,255,255,0.3)] transition-all duration-300 transform hover:scale-105 active:scale-95 flex items-center space-x-3 cursor-pointer"
                >
                  <FileText className="w-5 h-5 text-amber-300 drop-shadow group-hover:rotate-6 transition-transform" />
                  <span className="drop-shadow">{isLaunching ? 'Opening dashboard…' : 'File Your Insights'}</span>
                  <ArrowRight className="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1.5 text-amber-300" />
                </button>
              </motion.div>

            </div>

          </motion.div>

          {/* Initial Circle Hint when scroll = 0 */}
          <motion.div
            style={{
              opacity: useTransform(smoothProgress, [0, 0.12], [1, 0]),
            }}
            className="absolute inset-0 pointer-events-none flex flex-col items-center justify-center z-30"
          >
            <div className="w-28 h-28 rounded-full border border-white/20 flex flex-col items-center justify-center bg-black/40 backdrop-blur-sm shadow-[0_0_40px_rgba(255,255,255,0.1)]">
              <span className="text-[10px] font-mono tracking-widest uppercase text-white/80 mb-1">
                Scroll
              </span>
              <span className="text-[9px] font-mono text-white/40">&darr;</span>
            </div>
          </motion.div>

        </div>
      </div>

    </div>
  );
}
