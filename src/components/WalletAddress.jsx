import { Copy, Check } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

export default function WalletAddress() {
    const address = "0x7f23...a9b4";
    const fullAddress = "0x7f23bba30caebf06746ae045763ca445edcddda9b4";
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(fullAddress);
        setCopied(true);

        toast.success('Wallet address copied!', {
            icon: '✅',
            style: {
                background: '#18181B', // zinc-900
                color: '#fff',
                border: '1px solid rgba(45, 216, 167, 0.4)',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)'
            },
        });

        setTimeout(() => {
            setCopied(false);
        }, 2000);
    };

    return (
        <div className="w-full flex justify-center">
            <button
                onClick={handleCopy}
                title="Copy Address"
                className="group relative flex items-center gap-3 bg-zinc-800/40 hover:bg-zinc-800/80 border border-white/5 hover:border-aptos/50 transition-all duration-300 rounded-full px-5 py-2.5 shadow-lg active:scale-95 focus:outline-none focus:ring-2 focus:ring-aptos/50"
            >
                <div className="w-2 h-2 rounded-full bg-aptos animate-pulse shadow-[0_0_10px_rgba(45,216,167,0.8)]" />
                <span className="text-zinc-300 group-hover:text-white font-mono text-sm tracking-widest transition-colors duration-300">{address}</span>

                <div className="text-zinc-500 group-hover:text-aptos transition-colors duration-300 h-4 w-4 relative">
                    <AnimatePresence mode="wait">
                        {copied ? (
                            <motion.div
                                key="check"
                                initial={{ scale: 0, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0, opacity: 0 }}
                                transition={{ duration: 0.15 }}
                                className="absolute inset-0"
                            >
                                <Check className="w-4 h-4 text-aptos" />
                            </motion.div>
                        ) : (
                            <motion.div
                                key="copy"
                                initial={{ scale: 0, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0, opacity: 0 }}
                                transition={{ duration: 0.15 }}
                                className="absolute inset-0"
                            >
                                <Copy className="w-4 h-4" />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </button>
        </div>
    );
}
