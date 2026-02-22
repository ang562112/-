import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export default function BackgroundParticles() {
    const [particles, setParticles] = useState([]);

    useEffect(() => {
        const newParticles = Array.from({ length: 40 }).map((_, i) => ({
            id: i,
            x: Math.random() * 100,
            y: Math.random() * 100,
            size: Math.random() * 3 + 1,
            duration: Math.random() * 20 + 20,
            opacity: Math.random() * 0.4 + 0.1,
            delay: Math.random() * -20, // Negative start makes them start mid-animation
        }));
        setParticles(newParticles);
    }, []);

    return (
        <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
            {particles.map((p) => (
                <motion.div
                    key={p.id}
                    className="absolute rounded-full bg-aptos"
                    style={{
                        width: p.size,
                        height: p.size,
                        left: `${p.x}%`,
                        top: `${p.y}%`,
                        opacity: p.opacity,
                        boxShadow: '0 0 12px 2px rgba(45, 216, 167, 0.5)',
                    }}
                    animate={{
                        y: [0, -150, 0],
                        x: [0, Math.random() * 60 - 30, 0],
                        opacity: [p.opacity, p.opacity * 2.5, p.opacity],
                    }}
                    transition={{
                        duration: p.duration,
                        repeat: Infinity,
                        delay: p.delay,
                        ease: "linear",
                    }}
                />
            ))}
        </div>
    );
}
