import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export default function FallingStarlight() {
    const [stars, setStars] = useState([]);

    useEffect(() => {
        // Generate an array of objects to map into animated divs
        const generateStars = (count, sizeRange, durationRange, isTeal) => {
            return Array.from({ length: count }).map((_, i) => ({
                id: `${isTeal ? 'teal' : 'white'}-${sizeRange[0]}-${i}`,
                x: Math.random() * 100, // horizontal start %
                y: Math.random() * -100 - 10, // vertical start (offscreen top, varying heights)
                size: Math.random() * (sizeRange[1] - sizeRange[0]) + sizeRange[0],
                duration: Math.random() * (durationRange[1] - durationRange[0]) + durationRange[0],
                delay: Math.random() * -30, // Negative delay to start mid-animation
                opacity: Math.random() * 0.4 + 0.3,
                isTeal,
            }));
        };
        // 3 Layers for Parallax
        // Small (Background, slow, mostly white)
        const layer1 = generateStars(50, [1, 2], [25, 40], false);
        // Medium (Midground, medium speed, mix of teal and white)
        const layer2 = [
            ...generateStars(20, [2, 3], [15, 25], false),
            ...generateStars(15, [2, 3], [15, 25], true),
        ];
        // Large (Foreground, fast, mix)
        const layer3 = [
            ...generateStars(10, [3, 5], [10, 15], false),
            ...generateStars(8, [3, 5], [10, 15], true),
        ];

        setStars([...layer1, ...layer2, ...layer3]);
    }, []);

    return (
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0 bg-[#060608]">
            {stars.map((star) => (
                <motion.div
                    key={star.id}
                    className={cn(
                        "absolute rounded-full",
                        star.isTeal ? "bg-aptos" : "bg-zinc-200"
                    )}
                    style={{
                        width: star.size,
                        height: star.size,
                        left: `${star.x}%`,
                        top: `${star.y}%`,
                        opacity: star.opacity,
                        boxShadow: star.isTeal
                            ? '0 0 10px 2px rgba(45, 216, 167, 0.4)'
                            : '0 0 8px 1px rgba(255, 255, 255, 0.2)',
                    }}
                    animate={{
                        y: ["0vh", "120vh"], // Fall past the bottom of the screen
                        opacity: [star.opacity * 0.5, star.opacity, star.opacity * 0.5], // pulse slightly
                    }}
                    transition={{
                        y: {
                            duration: star.duration,
                            repeat: Infinity,
                            ease: "linear",
                            delay: star.delay,
                        },
                        opacity: {
                            duration: star.duration / 2,
                            repeat: Infinity,
                            ease: "easeInOut",
                            delay: star.delay,
                        }
                    }}
                />
            ))}
            {/* Matte black deep space radial overlay for atmosphere */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(0,0,0,0)_0%,#040405_100%)] z-10" />
        </div>
    );
}
