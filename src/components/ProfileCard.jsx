import { useRef } from 'react';
import { motion, useMotionValue, useTransform, useSpring } from 'framer-motion';
import SocialLinks from './SocialLinks';
import WalletAddress from './WalletAddress';

export default function ProfileCard() {
    const cardRef = useRef(null);

    const x = useMotionValue(0);
    const y = useMotionValue(0);

    const mouseXSpring = useSpring(x, { stiffness: 150, damping: 15 });
    const mouseYSpring = useSpring(y, { stiffness: 150, damping: 15 });

    const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ["12.5deg", "-12.5deg"]);
    const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ["-12.5deg", "12.5deg"]);

    const handleMouseMove = (e) => {
        if (!cardRef.current) return;
        const rect = cardRef.current.getBoundingClientRect();
        const width = rect.width;
        const height = rect.height;
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        const xPct = mouseX / width - 0.5;
        const yPct = mouseY / height - 0.5;

        x.set(xPct);
        y.set(yPct);
    };

    const handleMouseLeave = () => {
        x.set(0);
        y.set(0);
    };

    return (
        <motion.div
            className="relative z-10"
            style={{ perspective: "1000px" }}
            animate={{ y: [0, -20, 0] }}
            transition={{
                duration: 8,
                repeat: Infinity,
                ease: "easeInOut"
            }}
        >
            <motion.div
                ref={cardRef}
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
                style={{
                    rotateX,
                    rotateY,
                    transformStyle: "preserve-3d"
                }}
                className="w-full max-w-[340px] sm:max-w-md bg-zinc-900/50 backdrop-blur-xl border border-white/5 rounded-3xl p-8 flex flex-col items-center shadow-[0_20px_40px_rgba(0,0,0,0.5)] overflow-hidden relative"
            >
                <div className="absolute inset-0 bg-gradient-to-br from-aptos/10 via-transparent to-transparent pointer-events-none" />

                {/* Avatar */}
                <div
                    className="w-24 h-24 sm:w-28 sm:h-28 rounded-full bg-zinc-800 border-2 border-aptos/70 flex items-center justify-center mb-6 shadow-[0_0_25px_rgba(45,216,167,0.4)] transition-transform duration-300"
                    style={{ transform: "translateZ(60px)" }}
                >
                    <span className="text-4xl sm:text-5xl">🌌</span>
                </div>

                {/* Profile Info */}
                <div style={{ transform: "translateZ(40px)" }} className="text-center mb-8 relative w-full">
                    <h1 className="text-3xl font-extrabold text-white mb-2 tracking-tight">양승준</h1>
                    <h2 className="text-aptos font-semibold mb-3 tracking-wide text-sm sm:text-base">Aptos Movers Number 1</h2>
                    <p className="text-zinc-400 text-sm max-w-[260px] mx-auto leading-relaxed">
                        Aptos 무버스 멤버이고 질좋은 컨텐츠 생산 잘합니다. 또한 X에서 활동 열심히 하고있어요. 요로시쿠!
                    </p>
                </div>

                {/* Features */}
                <div style={{ transform: "translateZ(30px)" }} className="w-full space-y-6">
                    <WalletAddress />
                    <div className="w-full h-px bg-white/5 my-4" />
                    <SocialLinks />

                    {/* Add Save Contact Button */}
                    <div className="w-full flex justify-center mt-6">
                        <button
                            onClick={() => {
                                const vcard = `BEGIN:VCARD\nVERSION:3.0\nN:양;승준;;;\nFN:양승준\nORG:Aptos Movers\nTITLE:Number 1\nTEL;TYPE=WORK,VOICE:010-9655-6694\nEMAIL:ang56231234@gmail.com\nEND:VCARD`;
                                const blob = new Blob([vcard], { type: 'text/vcard;charset=utf-8' });
                                const url = URL.createObjectURL(blob);
                                const link = document.createElement('a');
                                link.href = url;
                                link.setAttribute('download', '양승준_Contact.vcf');
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                            }}
                            className="bg-zinc-800 hover:bg-aptos hover:text-black border border-aptos/50 text-aptos shadow-[0_0_15px_rgba(45,216,167,0.2)] hover:shadow-[0_0_25px_rgba(45,216,167,0.6)] transition-all duration-300 rounded-full px-6 py-2.5 font-bold tracking-wide active:scale-95 focus:outline-none focus:ring-2 focus:ring-aptos/50"
                        >
                            Save Contact
                        </button>
                    </div>
                </div>

            </motion.div>
        </motion.div>
    );
}
