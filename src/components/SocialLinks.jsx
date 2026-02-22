import { Twitter, Mail, Phone } from 'lucide-react';

export default function SocialLinks() {
    const links = [
        { name: 'X (Twitter)', icon: Twitter, url: 'https://x.com/tv72019740' },
        { name: 'Email', icon: Mail, url: 'mailto:ang56231234@gmail.com' },
        { name: 'Phone', icon: Phone, url: 'tel:010-9655-6694' },
    ];

    return (
        <div className="flex justify-center gap-3 sm:gap-4 w-full">
            {links.map((link) => {
                const Icon = link.icon;
                return (
                    <a
                        key={link.name}
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group relative flex items-center justify-center w-12 h-12 rounded-full bg-zinc-800/60 border border-zinc-700/50 hover:bg-zinc-800 hover:border-aptos transition-all duration-300 hover:scale-[1.15] hover:shadow-[0_0_20px_rgba(45,216,167,0.3)] focus:outline-none focus:ring-2 focus:ring-aptos/50"
                        aria-label={link.name}
                    >
                        <Icon className="w-5 h-5 text-zinc-400 group-hover:text-aptos transition-colors duration-300" />

                        {/* Tooltip */}
                        <span className="absolute -top-11 scale-0 opacity-0 group-hover:scale-100 group-hover:opacity-100 group-active:scale-95 transition-all duration-200 bg-zinc-800 text-xs font-semibold px-3 py-1.5 rounded-lg text-white whitespace-nowrap border border-white/5 shadow-xl pointer-events-none">
                            {link.name}
                            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 border-[5px] border-transparent border-t-zinc-800" />
                        </span>
                    </a>
                );
            })}
        </div>
    );
}
